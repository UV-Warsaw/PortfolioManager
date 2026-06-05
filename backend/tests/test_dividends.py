"""Tests for PROJ-17: dividend import and analysis."""

from datetime import datetime

from sqlmodel import Session

from app.repositories.portfolio import DividendRepository
from app.services.portfolio import get_dividend_summary, get_dividend_timeline

# Fixed user id matching the first registered user (id=1) in a fresh in-memory DB.
TEST_USER_ID = 1


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


def _register_and_login(client) -> str:
    """Register a test user and return a JWT token."""
    client.post(
        "/auth/register", json={"email": "dividends@test.com", "password": "Pass1234!"}
    )
    res = client.post(
        "/auth/login",
        json={"email": "dividends@test.com", "password": "Pass1234!"},
    )
    return res.json()["access_token"]


class TestDividendRepository:
    """Unit tests for DividendRepository methods."""

    def test_get_yearly_summary_empty(self, db_session: Session) -> None:
        """get_yearly_summary returns empty list when no dividends exist."""
        repo = DividendRepository(db_session)
        result = repo.get_yearly_summary()
        assert result == []

    def test_get_yearly_summary_single_dividend(self, db_session: Session) -> None:
        """get_yearly_summary returns one entry for a single dividend."""
        repo = DividendRepository(db_session)
        repo.bulk_create(
            [_make_dividend(date=datetime(2023, 3, 15, 0, 0, 0))], user_id=TEST_USER_ID
        )
        result = repo.get_yearly_summary()
        assert len(result) == 1
        assert result[0]["year"] == 2023
        assert result[0]["total"] == 25.0

    def test_get_yearly_summary_multiple_years(self, db_session: Session) -> None:
        """get_yearly_summary aggregates dividends by year."""
        repo = DividendRepository(db_session)
        repo.bulk_create(
            [
                _make_dividend(amount=10.0, date=datetime(2022, 3, 15, 0, 0, 0)),
                _make_dividend(amount=15.0, date=datetime(2022, 6, 15, 0, 0, 0)),
                _make_dividend(amount=25.0, date=datetime(2023, 3, 15, 0, 0, 0)),
            ],
            user_id=TEST_USER_ID,
        )
        result = repo.get_yearly_summary()
        assert len(result) == 2
        assert result[0]["year"] == 2022
        assert result[0]["total"] == 25.0
        assert result[1]["year"] == 2023
        assert result[1]["total"] == 25.0

    def test_get_yearly_summary_filtered_by_account(self, db_session: Session) -> None:
        """get_yearly_summary filters by account when provided."""
        repo = DividendRepository(db_session)
        repo.bulk_create(
            [
                _make_dividend(
                    amount=10.0, account="USD", date=datetime(2023, 3, 15, 0, 0, 0)
                ),
                _make_dividend(
                    amount=20.0, account="PLN", date=datetime(2023, 3, 15, 0, 0, 0)
                ),
            ],
            user_id=TEST_USER_ID,
        )
        result = repo.get_yearly_summary(account="USD")
        assert len(result) == 1
        assert result[0]["total"] == 10.0

    def test_get_monthly_timeline_empty(self, db_session: Session) -> None:
        """get_monthly_timeline returns empty list when no dividends exist."""
        repo = DividendRepository(db_session)
        result = repo.get_monthly_timeline()
        assert result == []

    def test_get_monthly_timeline_all_months(self, db_session: Session) -> None:
        """get_monthly_timeline returns all months across all years."""
        repo = DividendRepository(db_session)
        repo.bulk_create(
            [
                _make_dividend(amount=10.0, date=datetime(2022, 1, 15, 0, 0, 0)),
                _make_dividend(amount=15.0, date=datetime(2023, 3, 15, 0, 0, 0)),
                _make_dividend(amount=25.0, date=datetime(2023, 6, 15, 0, 0, 0)),
            ],
            user_id=TEST_USER_ID,
        )
        result = repo.get_monthly_timeline()
        assert len(result) == 3
        assert result[0]["month"] == 1
        assert result[0]["total"] == 10.0

    def test_get_monthly_timeline_filtered_by_year(self, db_session: Session) -> None:
        """get_monthly_timeline returns 12-month view when year is specified."""
        repo = DividendRepository(db_session)
        repo.bulk_create(
            [
                _make_dividend(amount=10.0, date=datetime(2022, 1, 15, 0, 0, 0)),
                _make_dividend(amount=15.0, date=datetime(2023, 3, 15, 0, 0, 0)),
                _make_dividend(amount=25.0, date=datetime(2023, 6, 15, 0, 0, 0)),
            ],
            user_id=TEST_USER_ID,
        )
        result = repo.get_monthly_timeline(year=2023)
        assert len(result) == 2
        assert result[0]["month"] == 3
        assert result[0]["total"] == 15.0
        assert result[1]["month"] == 6
        assert result[1]["total"] == 25.0

    def test_get_monthly_timeline_filtered_by_account(
        self, db_session: Session
    ) -> None:
        """get_monthly_timeline filters by account when provided."""
        repo = DividendRepository(db_session)
        repo.bulk_create(
            [
                _make_dividend(
                    amount=10.0, account="USD", date=datetime(2023, 3, 15, 0, 0, 0)
                ),
                _make_dividend(
                    amount=20.0, account="PLN", date=datetime(2023, 3, 15, 0, 0, 0)
                ),
            ],
            user_id=TEST_USER_ID,
        )
        result = repo.get_monthly_timeline(account="USD")
        assert len(result) == 1
        assert result[0]["total"] == 10.0


class TestDividendService:
    """Unit tests for portfolio service dividend functions."""

    def test_get_dividend_summary_empty(self, db_session: Session) -> None:
        """get_dividend_summary returns empty list when no dividends exist."""
        result = get_dividend_summary(db_session)
        assert result == []

    def test_get_dividend_summary_aggregates_by_year(self, db_session: Session) -> None:
        """get_dividend_summary calls repo method correctly."""
        repo = DividendRepository(db_session)
        repo.bulk_create(
            [
                _make_dividend(amount=10.0, date=datetime(2023, 1, 15, 0, 0, 0)),
                _make_dividend(amount=15.0, date=datetime(2023, 6, 15, 0, 0, 0)),
            ],
            user_id=TEST_USER_ID,
        )
        result = get_dividend_summary(db_session)
        assert len(result) == 1
        assert result[0]["year"] == 2023
        assert result[0]["total"] == 25.0

    def test_get_dividend_timeline_empty(self, db_session: Session) -> None:
        """get_dividend_timeline returns empty list when no dividends exist."""
        result = get_dividend_timeline(db_session)
        assert result == []

    def test_get_dividend_timeline_by_year(self, db_session: Session) -> None:
        """get_dividend_timeline filters by year correctly."""
        repo = DividendRepository(db_session)
        repo.bulk_create(
            [
                _make_dividend(amount=10.0, date=datetime(2022, 1, 15, 0, 0, 0)),
                _make_dividend(amount=15.0, date=datetime(2023, 3, 15, 0, 0, 0)),
                _make_dividend(amount=25.0, date=datetime(2023, 6, 15, 0, 0, 0)),
            ],
            user_id=TEST_USER_ID,
        )
        result = get_dividend_timeline(db_session, year=2023)
        assert len(result) == 2
        assert result[0]["month"] == 3


class TestDividendEndpoints:
    """Integration tests for dividend API endpoints."""

    def test_get_dividends_summary_empty(self, client) -> None:
        """GET /portfolio/dividends/summary returns empty list."""
        token = _register_and_login(client)
        response = client.get(
            "/portfolio/dividends/summary",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_get_dividends_summary_with_data(self, client, db_session: Session) -> None:
        """GET /portfolio/dividends/summary returns yearly summaries."""
        token = _register_and_login(client)
        repo = DividendRepository(db_session)
        repo.bulk_create(
            [
                _make_dividend(amount=10.0, date=datetime(2023, 1, 15, 0, 0, 0)),
                _make_dividend(amount=15.0, date=datetime(2023, 6, 15, 0, 0, 0)),
            ],
            user_id=TEST_USER_ID,
        )
        response = client.get(
            "/portfolio/dividends/summary",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["year"] == 2023
        assert body[0]["total"] == 25.0

    def test_get_dividends_summary_filtered_by_account(
        self, client, db_session: Session
    ) -> None:
        """GET /portfolio/dividends/summary filters by account."""
        token = _register_and_login(client)
        repo = DividendRepository(db_session)
        repo.bulk_create(
            [
                _make_dividend(
                    amount=10.0, account="USD", date=datetime(2023, 3, 15, 0, 0, 0)
                ),
                _make_dividend(
                    amount=20.0, account="PLN", date=datetime(2023, 3, 15, 0, 0, 0)
                ),
            ],
            user_id=TEST_USER_ID,
        )
        response = client.get(
            "/portfolio/dividends/summary?account=USD",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["total"] == 10.0

    def test_get_dividends_summary_invalid_account(self, client) -> None:
        """GET /portfolio/dividends/summary rejects invalid account."""
        token = _register_and_login(client)
        response = client.get(
            "/portfolio/dividends/summary?account=INVALID",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 400
        assert "account must be one of" in response.json()["detail"]

    def test_get_dividends_timeline_empty(self, client) -> None:
        """GET /portfolio/dividends/timeline returns empty list."""
        token = _register_and_login(client)
        response = client.get(
            "/portfolio/dividends/timeline",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_get_dividends_timeline_with_data(
        self, client, db_session: Session
    ) -> None:
        """GET /portfolio/dividends/timeline returns monthly data."""
        token = _register_and_login(client)
        repo = DividendRepository(db_session)
        repo.bulk_create(
            [
                _make_dividend(amount=10.0, date=datetime(2023, 1, 15, 0, 0, 0)),
                _make_dividend(amount=15.0, date=datetime(2023, 3, 15, 0, 0, 0)),
            ],
            user_id=TEST_USER_ID,
        )
        response = client.get(
            "/portfolio/dividends/timeline",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 2
        assert body[0]["month"] == 1
        assert body[0]["total"] == 10.0

    def test_get_dividends_timeline_filtered_by_year(
        self, client, db_session: Session
    ) -> None:
        """GET /portfolio/dividends/timeline filters by year."""
        token = _register_and_login(client)
        repo = DividendRepository(db_session)
        repo.bulk_create(
            [
                _make_dividend(amount=10.0, date=datetime(2022, 1, 15, 0, 0, 0)),
                _make_dividend(amount=15.0, date=datetime(2023, 3, 15, 0, 0, 0)),
            ],
            user_id=TEST_USER_ID,
        )
        response = client.get(
            "/portfolio/dividends/timeline?year=2023",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["month"] == 3
        assert body[0]["total"] == 15.0

    def test_get_dividends_timeline_unauthorized(self, client) -> None:
        """GET /portfolio/dividends/timeline requires auth."""
        response = client.get("/portfolio/dividends/timeline")
        # HTTPBearer returns 401 or 403 depending on version
        assert response.status_code in (401, 403)
