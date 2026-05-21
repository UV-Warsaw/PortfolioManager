"""Tests for PROJ-16: transaction deduplication and holdings calculation."""

from datetime import datetime

import pytest
from sqlmodel import Session

from app.repositories.portfolio import TransactionRepository
from app.services.portfolio import get_active_holdings

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_tx(
    ticker: str = "AAPL",
    quantity: float = 10.0,
    tx_type: str = "BUY",
    account: str = "PLN",
    date: datetime | None = None,
) -> dict:
    """Return a minimal transaction dict for testing."""
    return {
        "date": date or datetime(2024, 1, 15, 10, 0, 0),
        "ticker": ticker,
        "type": tx_type,
        "quantity": quantity,
        "price": 100.0,
        "market_price": None,
        "amount": quantity * 100.0,
        "raw": "{}",
        "account": account,
    }


def _register_and_login(client) -> str:
    """Register a test user and return a JWT token."""
    client.post(
        "/auth/register", json={"email": "holdings@test.com", "password": "Pass1234!"}
    )
    res = client.post(
        "/auth/login", json={"email": "holdings@test.com", "password": "Pass1234!"}
    )
    return res.json()["access_token"]


# ---------------------------------------------------------------------------
# Unit: TransactionRepository.bulk_create_with_dedup
# ---------------------------------------------------------------------------


def test_bulk_create_inserts_new_records(db_session: Session) -> None:
    """First import creates all records."""
    repo = TransactionRepository(db_session)
    records = [_make_tx("AAPL", 5.0), _make_tx("MSFT", 3.0)]
    created, skipped = repo.bulk_create_with_dedup(records)
    assert len(created) == 2
    assert skipped == 0


def test_bulk_create_dedup_skips_exact_duplicates(db_session: Session) -> None:
    """Second import of the same records results in zero new inserts."""
    repo = TransactionRepository(db_session)
    records = [_make_tx("AAPL", 5.0), _make_tx("MSFT", 3.0)]
    repo.bulk_create_with_dedup(records)
    created, skipped = repo.bulk_create_with_dedup(records)
    assert len(created) == 0
    assert skipped == 2


def test_bulk_create_dedup_partial_overlap(db_session: Session) -> None:
    """Only new records are inserted when file has both old and new rows."""
    repo = TransactionRepository(db_session)
    first = [_make_tx("AAPL", 5.0)]
    repo.bulk_create_with_dedup(first)
    second = [_make_tx("AAPL", 5.0), _make_tx("TSLA", 2.0)]
    created, skipped = repo.bulk_create_with_dedup(second)
    assert len(created) == 1
    assert skipped == 1
    assert created[0].ticker == "TSLA"


def test_dedup_different_quantity_is_not_duplicate(db_session: Session) -> None:
    """Same ticker+date+account but different quantity is treated as a new record."""
    repo = TransactionRepository(db_session)
    repo.bulk_create_with_dedup([_make_tx("AAPL", 5.0)])
    created, skipped = repo.bulk_create_with_dedup([_make_tx("AAPL", 10.0)])
    assert len(created) == 1
    assert skipped == 0


# ---------------------------------------------------------------------------
# Unit: TransactionRepository.get_holdings
# ---------------------------------------------------------------------------


def test_get_holdings_buy_only(db_session: Session) -> None:
    """Holdings equal total bought quantity when no sells exist."""
    repo = TransactionRepository(db_session)
    repo.bulk_create([_make_tx("AAPL", 10.0, "BUY"), _make_tx("AAPL", 5.0, "BUY")])
    holdings = repo.get_holdings()
    assert len(holdings) == 1
    assert holdings[0]["ticker"] == "AAPL"
    assert holdings[0]["quantity"] == pytest.approx(15.0)


def test_get_holdings_buy_minus_sell(db_session: Session) -> None:
    """Holdings reflect net position after partial sell."""
    repo = TransactionRepository(db_session)
    repo.bulk_create(
        [
            _make_tx("AAPL", 10.0, "BUY"),
            _make_tx("AAPL", 3.0, "SELL"),
        ]
    )
    holdings = repo.get_holdings()
    assert len(holdings) == 1
    assert holdings[0]["quantity"] == pytest.approx(7.0)


def test_get_holdings_fully_sold_excluded(db_session: Session) -> None:
    """Fully sold position is not returned in active holdings."""
    repo = TransactionRepository(db_session)
    repo.bulk_create(
        [
            _make_tx("AAPL", 5.0, "BUY"),
            _make_tx("AAPL", 5.0, "SELL"),
        ]
    )
    holdings = repo.get_holdings()
    assert holdings == []


def test_get_holdings_filtered_by_account(db_session: Session) -> None:
    """Account filter returns only matching holdings."""
    repo = TransactionRepository(db_session)
    repo.bulk_create(
        [
            _make_tx("AAPL", 5.0, account="PLN"),
            _make_tx("MSFT", 3.0, account="IKE"),
        ]
    )
    pln = repo.get_holdings(account="PLN")
    assert len(pln) == 1
    assert pln[0]["account"] == "PLN"


# ---------------------------------------------------------------------------
# Unit: get_active_holdings service
# ---------------------------------------------------------------------------


def test_get_active_holdings_sorted(db_session: Session) -> None:
    """Service returns holdings sorted by account then ticker."""
    repo = TransactionRepository(db_session)
    repo.bulk_create(
        [
            _make_tx("TSLA", 2.0, account="PLN"),
            _make_tx("AAPL", 5.0, account="PLN"),
            _make_tx("MSFT", 1.0, account="IKE"),
        ]
    )
    holdings = get_active_holdings(db_session)
    tickers = [h.ticker for h in holdings]
    assert tickers == ["MSFT", "AAPL", "TSLA"]


# ---------------------------------------------------------------------------
# Integration: GET /portfolio/holdings
# ---------------------------------------------------------------------------


def test_get_holdings_endpoint_empty(client) -> None:
    """Holdings endpoint returns empty list when no transactions exist."""
    token = _register_and_login(client)
    res = client.get(
        "/portfolio/holdings", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert res.json() == []


def test_get_holdings_endpoint_returns_active_positions(client) -> None:
    """Holdings endpoint reflects data saved via the upload endpoint."""
    from io import BytesIO

    import openpyxl

    token = _register_and_login(client)

    # Build a minimal XTB-style Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Open Position"
    ws.append(
        [
            "Position",
            "Volume",
            "Open Time",
            "Open Price",
            "Market Price",
            "Purchase Value",
        ]
    )
    ws.append(["AAPL", 10.0, "2024-01-15 10:00:00", 150.0, 160.0, 1500.0])
    ws.append(["MSFT", 5.0, "2024-02-01 09:30:00", 300.0, 320.0, 1500.0])
    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)

    res = client.post(
        "/portfolio/upload",
        files={
            "file": (
                "test.xlsx",
                buf,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
        data={"account": "PLN"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200

    res2 = client.get(
        "/portfolio/holdings", headers={"Authorization": f"Bearer {token}"}
    )
    assert res2.status_code == 200
    holdings = res2.json()
    tickers = {h["ticker"] for h in holdings}
    assert "AAPL" in tickers
    assert "MSFT" in tickers


def test_get_holdings_endpoint_dedup(client) -> None:
    """Uploading the same file twice does not duplicate holdings."""
    from io import BytesIO

    import openpyxl

    token = _register_and_login(client)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Open Position"
    ws.append(
        [
            "Position",
            "Volume",
            "Open Time",
            "Open Price",
            "Market Price",
            "Purchase Value",
        ]
    )
    ws.append(["AAPL", 10.0, "2024-01-15 10:00:00", 150.0, 160.0, 1500.0])

    def _excel_bytes() -> BytesIO:
        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf

    for _ in range(2):
        client.post(
            "/portfolio/upload",
            files={
                "file": (
                    "test.xlsx",
                    _excel_bytes(),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
            data={"account": "PLN"},
            headers={"Authorization": f"Bearer {token}"},
        )

    res = client.get(
        "/portfolio/holdings", headers={"Authorization": f"Bearer {token}"}
    )
    holdings = [h for h in res.json() if h["ticker"] == "AAPL"]
    assert len(holdings) == 1
    assert holdings[0]["quantity"] == pytest.approx(10.0)


def test_get_holdings_endpoint_invalid_account(client) -> None:
    """Holdings endpoint returns 400 for unknown account filter."""
    token = _register_and_login(client)
    res = client.get(
        "/portfolio/holdings?account=INVALID",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400


def test_get_holdings_endpoint_unauthenticated(client) -> None:
    """Holdings endpoint returns 401 without a token."""
    res = client.get("/portfolio/holdings")
    assert res.status_code == 401
