"""Portfolio router — handles XTB Excel file import and holdings queries."""

import logging

from fastapi import APIRouter, Depends, Form, HTTPException, Query, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.core.database import get_db
from app.models.user import User
from app.repositories.portfolio import DividendRepository, TransactionRepository
from app.schemas.portfolio import (
    HoldingRead,
    ImportResponse,
    PortfolioValueResponse,
    TopHoldingsResponse,
)
from app.services.auth import get_current_user
from app.services.excel_import import VALID_ACCOUNTS, parse_excel_to_records
from app.services.portfolio import (
    get_active_holdings,
    get_portfolio_value,
    get_top_holdings,
)

logger = logging.getLogger("portfolio_backend.routers.portfolio")

router = APIRouter(prefix="/portfolio", tags=["portfolio"])
_bearer = HTTPBearer()


@router.post("/upload", response_model=ImportResponse)
async def upload_portfolio_file(
    file: UploadFile,
    account: str = Form(...),
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> ImportResponse:
    """Upload an XTB Excel export and import transactions and dividends.

    Duplicate records (matched by date, ticker, quantity/amount, account) are
    silently skipped and reported in the response.

    Args:
        file: The Excel file (.xlsx or .xls).
        account: Account type — IKE, PLN, or USD.
        session: Database session.
        credentials: Bearer token credentials.

    Returns:
        ImportResponse with counts of imported and skipped records.

    Raises:
        HTTPException 401: Missing or invalid token.
        HTTPException 400: Invalid account type or unsupported file format.
        HTTPException 500: Unexpected parsing or database error.
    """
    _current_user: User = get_current_user(credentials, session)
    acc = account.upper()
    if acc not in VALID_ACCOUNTS:
        raise HTTPException(
            status_code=400,
            detail=f"account must be one of: {', '.join(VALID_ACCOUNTS)}",
        )

    fname = (file.filename or "").lower()
    if not (fname.endswith(".xlsx") or fname.endswith(".xls")):
        raise HTTPException(
            status_code=400,
            detail="Only .xlsx and .xls files are supported",
        )

    try:
        records = parse_excel_to_records(file, account=acc)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Excel parsing failed")
        raise HTTPException(status_code=500, detail="Failed to parse file") from exc

    try:
        tx_repo = TransactionRepository(session)
        div_repo = DividendRepository(session)
        created_tx, skipped_tx = tx_repo.bulk_create_with_dedup(records["transactions"])
        created_div, skipped_div = div_repo.bulk_create_with_dedup(records["dividends"])
    except Exception as exc:
        logger.exception("Database insert failed")
        raise HTTPException(status_code=500, detail="Failed to save records") from exc

    return ImportResponse(
        imported_transactions=len(created_tx),
        imported_dividends=len(created_div),
        skipped_transactions=skipped_tx,
        skipped_dividends=skipped_div,
        account=acc,
    )


@router.get("/holdings", response_model=list[HoldingRead])
def get_holdings(
    account: str | None = Query(
        default=None, description="Filter by account: IKE, PLN, USD"
    ),
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> list[HoldingRead]:
    """Return active holdings with net quantity > 0 for the authenticated user.

    Positions that have been fully sold (net quantity <= 0) are excluded.

    Args:
        account: Optional account filter.
        session: Database session.
        credentials: Bearer token credentials.

    Returns:
        List of HoldingRead sorted by account then ticker.

    Raises:
        HTTPException 401: Missing or invalid token.
        HTTPException 400: Invalid account value.
    """
    _current_user: User = get_current_user(credentials, session)
    acc: str | None = None
    if account is not None:
        acc = account.upper()
        if acc not in VALID_ACCOUNTS:
            raise HTTPException(
                status_code=400,
                detail=f"account must be one of: {', '.join(VALID_ACCOUNTS)}",
            )
    return get_active_holdings(session, account=acc)


@router.get("/value", response_model=PortfolioValueResponse)
def get_portfolio_value_endpoint(
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> PortfolioValueResponse:
    """Return net cost basis per account and aggregate total.

    Values represent capital invested (BUY amounts minus SELL amounts) in PLN.
    USD account transactions are converted to PLN at import time.

    Args:
        session: Database session.
        credentials: Bearer token credentials.

    Returns:
        PortfolioValueResponse with per-account values and total.

    Raises:
        HTTPException 401: Missing or invalid token.
    """
    get_current_user(credentials, session)
    return get_portfolio_value(session)


@router.get("/top-holdings", response_model=TopHoldingsResponse)
def get_top_holdings_endpoint(
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> TopHoldingsResponse:
    """Return the top 10 holdings by net cost basis across all accounts.

    Only active stock positions (BUY/SELL transactions with a ticker) are
    considered. Holdings are ordered by cost basis descending.

    Args:
        session: Database session.
        credentials: Bearer token credentials.

    Returns:
        TopHoldingsResponse with up to 10 items.

    Raises:
        HTTPException 401: Missing or invalid token.
    """
    get_current_user(credentials, session)
    return get_top_holdings(session)
