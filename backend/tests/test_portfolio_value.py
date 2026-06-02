"""Tests for PROJ-16: portfolio value and top-holdings endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.portfolio import Transaction
from app.repositories.portfolio import TransactionRepository
from app.schemas.portfolio import PortfolioValueResponse, TopHoldingsResponse


def _register_and_login(client: TestClient) -> str:
    """Register a test user and return a JWT token."""
    client.post(
        "/auth/register",
        json={"email": "value_test@test.com", "password": "Pass1234!"},
    )
    res = client.post(
        "/auth/login",
        json={"email": "value_test@test.com", "password": "Pass1234!"},
    )
    return res.json()["access_token"]


# ---------------------------------------------------------------------------
# Unit: TransactionRepository.get_account_values
# ---------------------------------------------------------------------------


def test_get_account_values_empty_db(db_session: Session) -> None:
    """Returns empty dict when no transactions exist."""
    repo = TransactionRepository(db_session)
    assert repo.get_account_values() == {}


def test_get_account_values_single_buy(db_session: Session) -> None:
    """Returns correct market value for a single BUY transaction."""
    db_session.add(
        Transaction(
            ticker="CDR", type="BUY", quantity=10.0, market_price=100.0, account="PLN"
        )
    )
    db_session.commit()

    repo = TransactionRepository(db_session)
    result = repo.get_account_values()
    assert result == {"PLN": 1000.0}


def test_get_account_values_multiple_accounts(db_session: Session) -> None:
    """Aggregates market value per account independently."""
    db_session.add_all(
        [
            Transaction(
                ticker="CDR",
                type="BUY",
                quantity=10.0,
                market_price=100.0,
                account="PLN",
            ),
            Transaction(
                ticker="PKN",
                type="BUY",
                quantity=5.0,
                market_price=100.0,
                account="PLN",
            ),
            Transaction(
                ticker="AAPL",
                type="BUY",
                quantity=2.0,
                market_price=400.0,
                account="IKE",
            ),
            Transaction(
                ticker="MSFT",
                type="BUY",
                quantity=1.0,
                market_price=1200.0,
                account="USD",
            ),
        ]
    )
    db_session.commit()

    repo = TransactionRepository(db_session)
    result = repo.get_account_values()
    assert result == {"PLN": 1500.0, "IKE": 800.0, "USD": 1200.0}


def test_get_account_values_sell_rows_ignored(db_session: Session) -> None:
    """SELL rows are not included in the market value calculation."""
    db_session.add_all(
        [
            Transaction(
                ticker="CDR",
                type="BUY",
                quantity=10.0,
                market_price=100.0,
                account="PLN",
            ),
            Transaction(
                ticker="CDR",
                type="SELL",
                quantity=4.0,
                market_price=110.0,
                account="PLN",
            ),
        ]
    )
    db_session.commit()

    repo = TransactionRepository(db_session)
    result = repo.get_account_values()
    assert result == {"PLN": 1000.0}


def test_get_account_values_null_market_price_ignored(db_session: Session) -> None:
    """Transactions with NULL market_price do not contribute to the total."""
    db_session.add_all(
        [
            Transaction(
                ticker="CDR",
                type="BUY",
                quantity=10.0,
                market_price=100.0,
                account="PLN",
            ),
            Transaction(
                ticker="PKN", type="BUY", quantity=5.0, market_price=None, account="PLN"
            ),
        ]
    )
    db_session.commit()

    repo = TransactionRepository(db_session)
    result = repo.get_account_values()
    assert result == {"PLN": 1000.0}


def test_get_account_values_cash_operations_excluded(db_session: Session) -> None:
    """Cash operation rows (ticker=None, e.g. dividends, deposits) are excluded."""
    db_session.add_all(
        [
            Transaction(
                ticker="CDR",
                type="BUY",
                quantity=10.0,
                market_price=200.0,
                account="PLN",
            ),
            # Cash-op rows that must not appear in the market value total
            Transaction(
                ticker=None, type="Dividend", quantity=None, amount=150.0, account="PLN"
            ),
            Transaction(
                ticker=None,
                type="IKE Deposit",
                quantity=None,
                amount=5000.0,
                account="IKE",
            ),
            Transaction(
                ticker=None,
                type="Withholding Tax",
                quantity=None,
                amount=-30.0,
                account="PLN",
            ),
        ]
    )
    db_session.commit()

    repo = TransactionRepository(db_session)
    result = repo.get_account_values()
    # Only the BUY stock row should count
    assert result == {"PLN": 2000.0}
    assert "IKE" not in result


# ---------------------------------------------------------------------------
# Unit: TransactionRepository.get_top_holdings
# ---------------------------------------------------------------------------


def test_get_top_holdings_empty_db(db_session: Session) -> None:
    """Returns empty list when no transactions exist."""
    repo = TransactionRepository(db_session)
    assert repo.get_top_holdings() == []


def test_get_top_holdings_ordering(db_session: Session) -> None:
    """Holdings are returned in descending market-value order."""
    db_session.add_all(
        [
            Transaction(
                ticker="AAPL",
                type="BUY",
                quantity=1.0,
                market_price=500.0,
                account="PLN",
            ),
            Transaction(
                ticker="CDR",
                type="BUY",
                quantity=1.0,
                market_price=3000.0,
                account="PLN",
            ),
            Transaction(
                ticker="MSFT",
                type="BUY",
                quantity=1.0,
                market_price=1500.0,
                account="PLN",
            ),
        ]
    )
    db_session.commit()

    repo = TransactionRepository(db_session)
    result = repo.get_top_holdings()
    tickers = [r[0] for r in result]
    assert tickers == ["CDR", "MSFT", "AAPL"]


def test_get_top_holdings_limit(db_session: Session) -> None:
    """Respects the limit parameter."""
    db_session.add_all(
        [
            Transaction(
                ticker=f"T{i}",
                type="BUY",
                quantity=1.0,
                market_price=float(i * 100),
                account="PLN",
            )
            for i in range(1, 16)
        ]
    )
    db_session.commit()

    repo = TransactionRepository(db_session)
    assert len(repo.get_top_holdings(limit=10)) == 10
    assert len(repo.get_top_holdings(limit=5)) == 5


def test_get_top_holdings_sell_rows_ignored(db_session: Session) -> None:
    """SELL rows are ignored; only BUY market value is counted per ticker."""
    db_session.add_all(
        [
            Transaction(
                ticker="CDR",
                type="BUY",
                quantity=10.0,
                market_price=100.0,
                account="PLN",
            ),
            Transaction(
                ticker="CDR",
                type="SELL",
                quantity=10.0,
                market_price=120.0,
                account="PLN",
            ),
            Transaction(
                ticker="PKN",
                type="BUY",
                quantity=5.0,
                market_price=100.0,
                account="PLN",
            ),
        ]
    )
    db_session.commit()

    repo = TransactionRepository(db_session)
    result = repo.get_top_holdings()
    tickers = [r[0] for r in result]
    assert "CDR" in tickers
    assert "PKN" in tickers
    cdr_value = next(v for t, v in result if t == "CDR")
    assert cdr_value == pytest.approx(1000.0)


# ---------------------------------------------------------------------------
# Integration: GET /portfolio/value
# ---------------------------------------------------------------------------


def test_portfolio_value_unauthenticated(client: TestClient) -> None:
    """Returns 401/403 when no bearer token is supplied."""
    res = client.get("/portfolio/value")
    assert res.status_code in (401, 403)


def test_portfolio_value_empty_database(client: TestClient) -> None:
    """Returns empty accounts and zero total when no transactions exist."""
    token = _register_and_login(client)
    res = client.get(
        "/portfolio/value",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    body = PortfolioValueResponse(**res.json())
    assert body.accounts == {}
    assert body.total == 0.0


def test_portfolio_value_cash_ops_not_counted(
    client: TestClient, db_session: Session
) -> None:
    """Cash-op rows do not inflate or deflate the portfolio value."""
    db_session.add_all(
        [
            Transaction(
                ticker="CDR",
                type="BUY",
                quantity=10.0,
                market_price=200.0,
                account="PLN",
            ),
            Transaction(
                ticker=None, type="Dividend", quantity=None, amount=100.0, account="PLN"
            ),
            Transaction(
                ticker=None,
                type="IKE Deposit",
                quantity=None,
                amount=5000.0,
                account="IKE",
            ),
        ]
    )
    db_session.commit()

    token = _register_and_login(client)
    res = client.get("/portfolio/value", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    body = PortfolioValueResponse(**res.json())
    assert body.accounts.get("PLN") == pytest.approx(2000.0)
    assert "IKE" not in body.accounts


def test_portfolio_value_returns_per_account_values(
    client: TestClient, db_session: Session
) -> None:
    """Returns accurate per-account market values after inserting transactions."""
    db_session.add_all(
        [
            Transaction(
                ticker="CDR",
                type="BUY",
                quantity=10.0,
                market_price=200.0,
                account="PLN",
            ),
            Transaction(
                ticker="AAPL",
                type="BUY",
                quantity=1.0,
                market_price=1500.0,
                account="IKE",
            ),
            Transaction(
                ticker="MSFT",
                type="BUY",
                quantity=2.0,
                market_price=1500.0,
                account="USD",
            ),
        ]
    )
    db_session.commit()

    token = _register_and_login(client)
    res = client.get(
        "/portfolio/value",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    body = PortfolioValueResponse(**res.json())
    assert body.accounts.get("PLN") == pytest.approx(2000.0)
    assert body.accounts.get("IKE") == pytest.approx(1500.0)
    assert body.accounts.get("USD") == pytest.approx(3000.0)
    assert body.total == pytest.approx(6500.0)


def test_portfolio_value_total_matches_account_sum(
    client: TestClient, db_session: Session
) -> None:
    """Total field equals the sum of all per-account market values."""
    db_session.add_all(
        [
            Transaction(
                ticker="CDR",
                type="BUY",
                quantity=5.0,
                market_price=110.0,
                account="PLN",
            ),
            Transaction(
                ticker="AAPL",
                type="BUY",
                quantity=3.0,
                market_price=300.0,
                account="IKE",
            ),
        ]
    )
    db_session.commit()

    token = _register_and_login(client)
    res = client.get(
        "/portfolio/value",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    body = PortfolioValueResponse(**res.json())
    assert body.total == pytest.approx(sum(body.accounts.values()))
    assert body.accounts.get("PLN") == pytest.approx(550.0)
    assert body.accounts.get("IKE") == pytest.approx(900.0)


# ---------------------------------------------------------------------------
# Integration: GET /portfolio/top-holdings
# ---------------------------------------------------------------------------


def test_top_holdings_unauthenticated(client: TestClient) -> None:
    """Returns 401/403 when no bearer token is supplied."""
    res = client.get("/portfolio/top-holdings")
    assert res.status_code in (401, 403)


def test_top_holdings_empty_database(client: TestClient) -> None:
    """Returns empty items list when no transactions exist."""
    token = _register_and_login(client)
    res = client.get(
        "/portfolio/top-holdings",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    body = TopHoldingsResponse(**res.json())
    assert body.items == []


def test_top_holdings_ordered_descending(
    client: TestClient, db_session: Session
) -> None:
    """Items are returned by market value descending."""
    db_session.add_all(
        [
            Transaction(
                ticker="AAPL",
                type="BUY",
                quantity=1.0,
                market_price=500.0,
                account="PLN",
            ),
            Transaction(
                ticker="CDR",
                type="BUY",
                quantity=1.0,
                market_price=3000.0,
                account="PLN",
            ),
            Transaction(
                ticker="MSFT",
                type="BUY",
                quantity=1.0,
                market_price=1500.0,
                account="PLN",
            ),
        ]
    )
    db_session.commit()

    token = _register_and_login(client)
    res = client.get(
        "/portfolio/top-holdings",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    body = TopHoldingsResponse(**res.json())
    tickers = [item.ticker for item in body.items]
    assert tickers == ["CDR", "MSFT", "AAPL"]


def test_top_holdings_max_ten_items(client: TestClient, db_session: Session) -> None:
    """Never returns more than 10 items regardless of how many holdings exist."""
    db_session.add_all(
        [
            Transaction(
                ticker=f"T{i}",
                type="BUY",
                quantity=1.0,
                market_price=float(i * 100),
                account="PLN",
            )
            for i in range(1, 16)
        ]
    )
    db_session.commit()

    token = _register_and_login(client)
    res = client.get(
        "/portfolio/top-holdings",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    body = TopHoldingsResponse(**res.json())
    assert len(body.items) == 10
