"""Tests for PROJ-23: dashboard summary endpoints."""

from datetime import datetime

import pytest
from sqlmodel import Session

from app.repositories.portfolio import DividendRepository, TransactionRepository
from app.services.summary import SummaryService


def _register_and_login(client) -> str:
    """Register a test user and return a JWT token."""
    client.post(
        "/auth/register", json={"email": "dashboard@test.com", "password": "Pass1234!"}
    )
    res = client.post(
        "/auth/login",
        json={"email": "dashboard@test.com", "password": "Pass1234!"},
    )
    return res.json()["access_token"]


def _make_transaction(
    ticker: str = "AAPL",
    quantity: float = 10.0,
    price: float = 150.0,
    account: str = "USD",
) -> dict:
    """Return a minimal transaction dict for testing."""
    return {
        "date": datetime(2024, 1, 15, 10, 0, 0),
        "ticker": ticker,
        "type": "BUY",
        "quantity": quantity,
        "price": price,
        "market_price": price * 1.2,
        "amount": quantity * price,
        "raw": "{}",
        "account": account,
    }


def _make_dividend(
    ticker: str = "AAPL",
    amount: float = 25.0,
    account: str = "USD",
    date: datetime | None = None,
) -> dict:
    """Return a minimal dividend dict for testing."""
    return {
        "date": date or datetime(2023, 3, 15, 0, 0, 0),
        "ticker": ticker,
        "amount": amount,
        "currency": "USD",
        "raw": "{}",
        "account": account,
    }


class TestSummaryService:
    """Unit tests for SummaryService."""

    def test_get_portfolio_summary_empty(self, db_session: Session) -> None:
        """get_portfolio_summary returns zero values when no holdings."""
        service = SummaryService(db_session)
        result = service.get_portfolio_summary()
        assert result["portfolio_value"] == 0.0
        assert result["total_invested"] == 0.0
        assert result["profit"] == 0.0
        assert result["profit_percentage"] == 0.0
        assert result["top_holdings"] == []

    def test_get_portfolio_summary_with_holdings(
        self, db_session: Session
    ) -> None:
        """get_portfolio_summary returns correct values with holdings."""
        repo = TransactionRepository(db_session)
        repo.bulk_create([_make_transaction()])
        service = SummaryService(db_session)
        result = service.get_portfolio_summary()
        assert result["portfolio_value"] > 0
        assert result["total_invested"] > 0
        assert result["profit"] >= 0
        assert len(result["top_holdings"]) == 1
        assert result["top_holdings"][0]["ticker"] == "AAPL"

    def test_get_dividend_yearly_summary_empty(self, db_session: Session) -> None:
        """get_dividend_yearly_summary returns empty list when no dividends."""
        service = SummaryService(db_session)
        result = service.get_dividend_yearly_summary()
        assert result == []

    def test_get_dividend_yearly_summary_with_data(
        self, db_session: Session
    ) -> None:
        """get_dividend_yearly_summary aggregates by year."""
        repo = DividendRepository(db_session)
        repo.bulk_create([_make_dividend(date=datetime(2023, 3, 15, 0, 0, 0))])
        service = SummaryService(db_session)
        result = service.get_dividend_yearly_summary()
        assert len(result) == 1
        assert result[0].year == "2023"
        assert result[0].total == 25.0

    def test_get_dividend_monthly_timeline_empty(self, db_session: Session) -> None:
        """get_dividend_monthly_timeline returns empty list when no dividends."""
        service = SummaryService(db_session)
        result = service.get_dividend_monthly_timeline()
        assert result == []

    def test_get_dividend_monthly_timeline_with_data(
        self, db_session: Session
    ) -> None:
        """get_dividend_monthly_timeline returns monthly data."""
        repo = DividendRepository(db_session)
        repo.bulk_create([_make_dividend(date=datetime(2023, 3, 15, 0, 0, 0))])
        service = SummaryService(db_session)
        result = service.get_dividend_monthly_timeline()
        assert len(result) == 1
        assert result[0].month == "2023-03"
        assert result[0].total == 25.0


class TestDashboardEndpoints:
    """Integration tests for dashboard API endpoints."""

    def test_get_dashboard_unauthorized(self, client) -> None:
        """GET /summary/dashboard requires auth."""
        response = client.get("/summary/dashboard")
        assert response.status_code == 403

    def test_get_dashboard_empty(self, client) -> None:
        """GET /summary/dashboard returns zeros when no holdings."""
        token = _register_and_login(client)
        response = client.get(
            "/summary/dashboard",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["portfolio_value"] == 0.0
        assert body["total_invested"] == 0.0
        assert body["profit"] == 0.0
        assert body["top_holdings"] == []

    def test_get_dashboard_with_data(self, client, db_session: Session) -> None:
        """GET /summary/dashboard returns portfolio summary."""
        token = _register_and_login(client)
        repo = TransactionRepository(db_session)
        repo.bulk_create([_make_transaction()])
        response = client.get(
            "/summary/dashboard",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["portfolio_value"] > 0
        assert body["total_invested"] > 0
        assert len(body["top_holdings"]) > 0

    def test_get_dividend_yearly_summary_empty(self, client) -> None:
        """GET /summary/dividends/yearly returns empty list."""
        token = _register_and_login(client)
        response = client.get(
            "/summary/dividends/yearly",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_get_dividend_yearly_summary_with_data(
        self, client, db_session: Session
    ) -> None:
        """GET /summary/dividends/yearly returns yearly summaries."""
        token = _register_and_login(client)
        repo = DividendRepository(db_session)
        repo.bulk_create([_make_dividend(date=datetime(2023, 3, 15, 0, 0, 0))])
        response = client.get(
            "/summary/dividends/yearly",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["year"] == "2023"
        assert body[0]["total"] == 25.0

    def test_get_dividend_timeline_empty(self, client) -> None:
        """GET /summary/dividends/timeline returns empty list."""
        token = _register_and_login(client)
        response = client.get(
            "/summary/dividends/timeline",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_get_dividend_timeline_with_data(
        self, client, db_session: Session
    ) -> None:
        """GET /summary/dividends/timeline returns monthly data."""
        token = _register_and_login(client)
        repo = DividendRepository(db_session)
        repo.bulk_create([_make_dividend(date=datetime(2023, 3, 15, 0, 0, 0))])
        response = client.get(
            "/summary/dividends/timeline",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["month"] == "2023-03"
        assert body[0]["total"] == 25.0

    def test_get_dividend_timeline_filtered_by_year(
        self, client, db_session: Session
    ) -> None:
        """GET /summary/dividends/timeline filters by year."""
        token = _register_and_login(client)
        repo = DividendRepository(db_session)
        repo.bulk_create(
            [
                _make_dividend(date=datetime(2022, 1, 15, 0, 0, 0)),
                _make_dividend(date=datetime(2023, 3, 15, 0, 0, 0)),
            ]
        )
        response = client.get(
            "/summary/dividends/timeline?year=2023",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["month"] == "03"
        assert body[0]["total"] == 25.0
