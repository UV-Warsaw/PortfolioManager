"""Portfolio router — handles XTB Excel file import."""

import logging

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.core.database import get_db
from app.models.user import User
from app.repositories.portfolio import DividendRepository, TransactionRepository
from app.schemas.portfolio import ImportResponse
from app.services.auth import get_current_user
from app.services.excel_import import VALID_ACCOUNTS, parse_excel_to_records

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
    """
    Upload an XTB Excel export and import transactions and dividends.

    Args:
        file: The Excel file (.xlsx or .xls).
        account: Account type — IKE, PLN, or USD.
        session: Database session.

    Returns:
        ImportResponse with counts of imported records.

    Raises:
        HTTPException 401: Missing or invalid token.
        HTTPException 400: Invalid account type or unsupported file format.
        HTTPException 500: Unexpected parsing or database error.
    """
    # Validate token — raises 401 if invalid
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
        tx_repo.bulk_create(records["transactions"])
        div_repo.bulk_create(records["dividends"])
    except Exception as exc:
        logger.exception("Database insert failed")
        raise HTTPException(status_code=500, detail="Failed to save records") from exc

    return ImportResponse(
        imported_transactions=len(records["transactions"]),
        imported_dividends=len(records["dividends"]),
        account=acc,
    )
