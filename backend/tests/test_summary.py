"""Tests for PROJ-23: dashboard summary endpoints."""

from datetime import datetime

from sqlmodel import Session

from app.models.assets import OtherAsset, OtherAssetClass
from app.models.bonds import Bond, CapitalizationType
from app.models.cash import CashAccount, CashAccountType
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

    def test_get_portfolio_summary_with_holdings(self, db_session: Session) -> None:
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

    def test_get_dividend_yearly_summary_with_data(self, db_session: Session) -> None:
        """get_dividend_yearly_summary aggregates by year."""
        repo = DividendRepository(db_session)
        repo.bulk_create([_make_dividend(date=datetime(2023, 3, 15, 0, 0, 0))])
        service = SummaryService(db_session)
        result = service.get_dividend_yearly_summary()
        assert len(result) == 1
        assert result[0].year == 2023
        assert result[0].total == 25.0

    def test_get_dividend_monthly_timeline_empty(self, db_session: Session) -> None:
        """get_dividend_monthly_timeline returns empty list when no dividends."""
        service = SummaryService(db_session)
        result = service.get_dividend_monthly_timeline()
        assert result == []

    def test_get_dividend_monthly_timeline_with_data(self, db_session: Session) -> None:
        """get_dividend_monthly_timeline returns monthly data."""
        repo = DividendRepository(db_session)
        repo.bulk_create([_make_dividend(date=datetime(2023, 3, 15, 0, 0, 0))])
        service = SummaryService(db_session)
        result = service.get_dividend_monthly_timeline()
        assert len(result) == 1
        assert result[0].month == 3
        assert result[0].total == 25.0


class TestDashboardEndpoints:
    """Integration tests for dashboard API endpoints."""

    def test_get_dashboard_unauthorized(self, client) -> None:
        """GET /summary/dashboard requires auth."""
        response = client.get("/summary/dashboard")
        # HTTPBearer returns 401 or 403 depending on version
        assert response.status_code in (401, 403)

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
        assert body[0]["year"] == 2023
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

    def test_get_dividend_timeline_with_data(self, client, db_session: Session) -> None:
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
        assert body[0]["month"] == 3
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
        assert body[0]["month"] == 3
        assert body[0]["total"] == 25.0


# ── helpers for PROJ-23 wealth tests ─────────────────────────────────────────


def _make_bond(session: Session, principal: float = 1000.0, quantity: int = 1) -> Bond:
    bond = Bond(
        name="Test Bond",
        annual_rate=5.0,
        years=2.0,
        capitalization=CapitalizationType.ANNUAL,
        principal=principal,
        quantity=quantity,
        purchase_date=datetime(2024, 1, 1),
    )
    session.add(bond)
    session.commit()
    session.refresh(bond)
    return bond


def _make_cash_account(session: Session, balance: float = 500.0) -> CashAccount:
    acct = CashAccount(
        name="Test Account",
        account_type=CashAccountType.SAVINGS,
        balance=balance,
        currency="PLN",
    )
    session.add(acct)
    session.commit()
    session.refresh(acct)
    return acct


def _make_crypto(
    session: Session, price: float = 300.0, qty: float = 2.0
) -> OtherAsset:
    asset = OtherAsset(
        name="BTC",
        asset_class=OtherAssetClass.CRYPTO,
        current_value=price,
        quantity=qty,
        purchase_price=250.0,
        currency="PLN",
    )
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return asset


def _make_real_estate(
    session: Session,
    value: float = 400000.0,
    mortgage: float = 100000.0,
) -> OtherAsset:
    asset = OtherAsset(
        name="Flat",
        asset_class=OtherAssetClass.REAL_ESTATE,
        current_value=value,
        mortgage_remaining=mortgage,
        currency="PLN",
    )
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return asset


# ── PROJ-23 service unit tests ────────────────────────────────────────────────


class TestWealthSummaryService:
    """Unit tests for SummaryService.get_wealth_summary()."""

    def test_empty_portfolio_has_no_data(self, db_session: Session) -> None:
        """Returns has_data=False and zero total when no assets exist."""
        result = SummaryService(db_session).get_wealth_summary()
        assert result.has_data is False
        assert result.total_value == 0.0
        assert len(result.breakdown) == 5

    def test_breakdown_has_five_classes(self, db_session: Session) -> None:
        """Breakdown always contains exactly the five expected asset classes."""
        result = SummaryService(db_session).get_wealth_summary()
        names = {item.name for item in result.breakdown}
        assert names == {"Stocks", "Bonds", "Cash", "Crypto", "Real Estate"}

    def test_bond_value_uses_compound_interest(self, db_session: Session) -> None:
        """Bond value uses BondCalculationService (compound interest > principal)."""
        _make_bond(db_session, principal=1000.0, quantity=1)
        result = SummaryService(db_session).get_wealth_summary()
        bonds_item = next(i for i in result.breakdown if i.name == "Bonds")
        # After 1+ years at 5% annual, value must exceed principal
        assert bonds_item.value > 1000.0
        assert result.has_data is True

    def test_cash_value_reflects_balance(self, db_session: Session) -> None:
        """Cash class value equals total cash account balances."""
        _make_cash_account(db_session, balance=2500.0)
        result = SummaryService(db_session).get_wealth_summary()
        cash_item = next(i for i in result.breakdown if i.name == "Cash")
        assert cash_item.value == 2500.0

    def test_crypto_value_is_quantity_times_price(self, db_session: Session) -> None:
        """Crypto class value = quantity × current_value (price per unit)."""
        _make_crypto(db_session, price=300.0, qty=2.0)
        result = SummaryService(db_session).get_wealth_summary()
        crypto_item = next(i for i in result.breakdown if i.name == "Crypto")
        assert crypto_item.value == 600.0

    def test_real_estate_value_is_net_equity(self, db_session: Session) -> None:
        """Real Estate value = property value − mortgage (net equity)."""
        _make_real_estate(db_session, value=400000.0, mortgage=100000.0)
        result = SummaryService(db_session).get_wealth_summary()
        re_item = next(i for i in result.breakdown if i.name == "Real Estate")
        assert re_item.value == 300000.0

    def test_real_estate_net_equity_clamped_at_zero(self, db_session: Session) -> None:
        """Real Estate net equity never goes below zero."""
        _make_real_estate(db_session, value=50000.0, mortgage=200000.0)
        result = SummaryService(db_session).get_wealth_summary()
        re_item = next(i for i in result.breakdown if i.name == "Real Estate")
        assert re_item.value == 0.0

    def test_percentages_sum_to_100(self, db_session: Session) -> None:
        """Breakdown percentages sum to ~100% when there is data."""
        _make_cash_account(db_session, balance=1000.0)
        _make_crypto(db_session, price=500.0, qty=1.0)
        result = SummaryService(db_session).get_wealth_summary()
        total_pct = sum(i.percentage for i in result.breakdown)
        assert abs(total_pct - 100.0) < 0.1

    def test_total_is_sum_of_classes(self, db_session: Session) -> None:
        """total_value equals sum of all class values."""
        _make_cash_account(db_session, balance=1000.0)
        _make_crypto(db_session, price=200.0, qty=3.0)
        result = SummaryService(db_session).get_wealth_summary()
        assert result.total_value == round(sum(i.value for i in result.breakdown), 2)


# ── PROJ-23 endpoint integration tests ───────────────────────────────────────


class TestWealthEndpoint:
    """Integration tests for GET /summary/wealth."""

    def test_requires_auth(self, client) -> None:
        """Unauthenticated request returns 401/403."""
        response = client.get("/summary/wealth")
        assert response.status_code in (401, 403)

    def test_empty_portfolio(self, client) -> None:
        """Returns has_data=False with zeros when no assets exist."""
        token = _register_and_login(client)
        response = client.get(
            "/summary/wealth",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["has_data"] is False
        assert body["total_value"] == 0.0
        assert len(body["breakdown"]) == 5

    def test_cash_appears_in_breakdown(self, client, db_session: Session) -> None:
        """Cash account balance appears in the wealth breakdown."""
        _register_and_login(client)
        _make_cash_account(db_session, balance=3000.0)
        token = _register_and_login(client)
        response = client.get(
            "/summary/wealth",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["has_data"] is True
        cash = next(c for c in body["breakdown"] if c["name"] == "Cash")
        assert cash["value"] == 3000.0
        assert cash["percentage"] == 100.0

    def test_multiple_classes_present(self, client, db_session: Session) -> None:
        """Multiple non-zero classes are reflected with correct percentages."""
        _register_and_login(client)
        _make_cash_account(db_session, balance=1000.0)
        _make_crypto(db_session, price=500.0, qty=2.0)  # 1000 PLN
        token = _register_and_login(client)
        response = client.get(
            "/summary/wealth",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["total_value"] == 2000.0
        cash = next(c for c in body["breakdown"] if c["name"] == "Cash")
        crypto = next(c for c in body["breakdown"] if c["name"] == "Crypto")
        assert cash["percentage"] == 50.0
        assert crypto["percentage"] == 50.0

    def test_breakdown_fields_present(self, client) -> None:
        """Each breakdown item has name, value, and percentage fields."""
        token = _register_and_login(client)
        response = client.get(
            "/summary/wealth",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        for item in response.json()["breakdown"]:
            assert "name" in item
            assert "value" in item
            assert "percentage" in item


# ── PROJ-27 risk assessment tests ────────────────────────────────────────────


def _register_and_login_unique(client, email: str) -> str:
    """Register a unique user and return a JWT token."""
    client.post("/auth/register", json={"email": email, "password": "Pass1234!"})
    res = client.post("/auth/login", json={"email": email, "password": "Pass1234!"})
    return res.json()["access_token"]


class TestRiskAssessmentService:
    """Unit tests for SummaryService.get_risk_assessment()."""

    def test_empty_portfolio_returns_moderate_no_data(
        self, db_session: Session
    ) -> None:
        """Empty portfolio returns has_data=False and moderate as default."""
        result = SummaryService(db_session).get_risk_assessment("moderate")
        assert result.has_data is False
        assert result.portfolio_risk == "moderate"
        assert result.high_pct == 0.0
        assert result.medium_pct == 0.0
        assert result.low_pct == 0.0

    def test_user_preference_is_preserved(self, db_session: Session) -> None:
        """User preference is echoed back unchanged."""
        result = SummaryService(db_session).get_risk_assessment("conservative")
        assert result.user_preference == "conservative"

    def test_aggressive_when_stocks_dominate(self, db_session: Session) -> None:
        """Portfolio with >50% crypto → aggressive."""
        # 600 PLN crypto (high), 100 PLN cash (low) → high_pct = 85.7%
        _make_crypto(db_session, price=300.0, qty=2.0)  # 600 PLN
        _make_cash_account(db_session, balance=100.0)
        result = SummaryService(db_session).get_risk_assessment("conservative")
        assert result.portfolio_risk == "aggressive"
        assert result.high_pct > 50.0
        assert result.is_aligned is False

    def test_conservative_when_low_risk_dominates(self, db_session: Session) -> None:
        """Portfolio with ≥60% bonds + cash → conservative."""
        _make_cash_account(db_session, balance=800.0)  # 800 PLN low
        _make_crypto(db_session, price=100.0, qty=2.0)  # 200 PLN high → low_pct=80%
        result = SummaryService(db_session).get_risk_assessment("conservative")
        assert result.portfolio_risk == "conservative"
        assert result.low_pct >= 60.0
        assert result.is_aligned is True

    def test_moderate_when_mixed(self, db_session: Session) -> None:
        """Portfolio with neither bucket dominant → moderate."""
        # 400 high (crypto), 400 medium (stocks/RE), 200 low → high=40%, medium=40%, low=20%
        _make_crypto(db_session, price=200.0, qty=2.0)  # 400 high
        _make_real_estate(db_session, value=400.0, mortgage=0.0)  # 400 medium
        _make_cash_account(db_session, balance=200.0)  # 200 low
        result = SummaryService(db_session).get_risk_assessment("moderate")
        assert result.portfolio_risk == "moderate"
        assert result.is_aligned is True

    def test_aligned_true_when_match(self, db_session: Session) -> None:
        """is_aligned=True when portfolio_risk equals user_preference."""
        _make_cash_account(db_session, balance=1000.0)  # conservative portfolio
        result = SummaryService(db_session).get_risk_assessment("conservative")
        assert result.is_aligned is True

    def test_aligned_false_when_mismatch(self, db_session: Session) -> None:
        """is_aligned=False when portfolio_risk differs from user_preference."""
        _make_cash_account(db_session, balance=1000.0)  # conservative portfolio
        result = SummaryService(db_session).get_risk_assessment("aggressive")
        assert result.is_aligned is False

    def test_pcts_sum_to_100_when_data_present(self, db_session: Session) -> None:
        """high_pct + medium_pct + low_pct ≈ 100 when has_data=True."""
        _make_cash_account(db_session, balance=500.0)
        _make_crypto(db_session, price=250.0, qty=2.0)
        result = SummaryService(db_session).get_risk_assessment("moderate")
        assert result.has_data is True
        total = result.high_pct + result.medium_pct + result.low_pct
        assert abs(total - 100.0) < 0.5


class TestRiskEndpoint:
    """Integration tests for GET /summary/risk."""

    def test_requires_auth(self, client) -> None:
        """Unauthenticated request returns 401/403."""
        response = client.get("/summary/risk")
        assert response.status_code in (401, 403)

    def test_empty_portfolio_response_shape(self, client) -> None:
        """Returns correct shape with has_data=False on empty portfolio."""
        token = _register_and_login_unique(client, "risk_empty@test.com")
        response = client.get(
            "/summary/risk",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["has_data"] is False
        assert "portfolio_risk" in body
        assert "user_preference" in body
        assert "is_aligned" in body
        assert "high_pct" in body
        assert "medium_pct" in body
        assert "low_pct" in body

    def test_aggressive_portfolio_detected(self, client, db_session: Session) -> None:
        """Endpoint returns aggressive when stocks/crypto > 50%."""
        _register_and_login_unique(client, "risk_agg@test.com")
        _make_crypto(db_session, price=500.0, qty=3.0)  # 1500 high
        _make_cash_account(db_session, balance=100.0)  # 100 low
        token = _register_and_login_unique(client, "risk_agg2@test.com")
        response = client.get(
            "/summary/risk",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["portfolio_risk"] == "aggressive"

    def test_user_preference_reflects_profile(self, client) -> None:
        """user_preference matches the default risk level on a new user."""
        token = _register_and_login_unique(client, "risk_pref@test.com")
        response = client.get(
            "/summary/risk",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        # New users default to "moderate"
        assert response.json()["user_preference"] == "moderate"


# ── PROJ-28 diversification recommendation tests ─────────────────────────────


class TestDiversificationService:
    """Unit tests for SummaryService.get_diversification_recommendations()."""

    def test_empty_portfolio_is_diversified_no_data(self, db_session: Session) -> None:
        """Empty portfolio → is_diversified=True, has_data=False."""
        result = SummaryService(db_session).get_diversification_recommendations()
        assert result.has_data is False
        assert result.is_diversified is True
        assert result.recommendations == []

    def test_diversified_portfolio_no_recommendations(
        self, db_session: Session
    ) -> None:
        """Portfolio below threshold → empty recommendations list."""
        # 400 cash (40%) + 400 crypto (40%) → neither exceeds 70%
        _make_cash_account(db_session, balance=400.0)
        _make_crypto(db_session, price=200.0, qty=2.0)  # 400 PLN
        result = SummaryService(db_session).get_diversification_recommendations()
        assert result.has_data is True
        assert result.is_diversified is True
        assert result.recommendations == []

    def test_concentrated_cash_triggers_recommendation(
        self, db_session: Session
    ) -> None:
        """100% cash → one recommendation with link_to='cash'."""
        _make_cash_account(db_session, balance=1000.0)
        result = SummaryService(db_session).get_diversification_recommendations()
        assert result.is_diversified is False
        assert len(result.recommendations) == 1
        rec = result.recommendations[0]
        assert rec.asset_class == "Cash"
        assert rec.link_to == "cash"
        assert rec.percentage == 100.0

    def test_recommendation_problem_contains_percentage(
        self, db_session: Session
    ) -> None:
        """Problem string includes the percentage value."""
        _make_cash_account(db_session, balance=1000.0)
        result = SummaryService(db_session).get_diversification_recommendations()
        rec = result.recommendations[0]
        assert "100" in rec.problem

    def test_recommendation_has_action_text(self, db_session: Session) -> None:
        """Each recommendation has a non-empty action string."""
        _make_cash_account(db_session, balance=1000.0)
        result = SummaryService(db_session).get_diversification_recommendations()
        assert result.recommendations[0].action != ""

    def test_concentrated_crypto_triggers_recommendation(
        self, db_session: Session
    ) -> None:
        """100% crypto → recommendation with link_to='crypto'."""
        _make_crypto(db_session, price=500.0, qty=2.0)
        result = SummaryService(db_session).get_diversification_recommendations()
        assert result.is_diversified is False
        rec = result.recommendations[0]
        assert rec.asset_class == "Crypto"
        assert rec.link_to == "crypto"

    def test_exactly_at_threshold_is_diversified(self, db_session: Session) -> None:
        """Asset class at exactly 70% doesn't trigger a recommendation (threshold is strict >)."""
        # 700 cash + 300 crypto → cash = 70.0% exactly
        _make_cash_account(db_session, balance=700.0)
        _make_crypto(db_session, price=150.0, qty=2.0)  # 300 PLN
        result = SummaryService(db_session).get_diversification_recommendations()
        assert result.is_diversified is True

    def test_just_above_threshold_triggers(self, db_session: Session) -> None:
        """Asset class just above 70% triggers a recommendation."""
        # 710 cash + 290 crypto → cash ≈ 71%
        _make_cash_account(db_session, balance=710.0)
        _make_crypto(db_session, price=145.0, qty=2.0)  # 290 PLN
        result = SummaryService(db_session).get_diversification_recommendations()
        assert result.is_diversified is False


class TestDiversificationEndpoint:
    """Integration tests for GET /summary/diversification."""

    def test_requires_auth(self, client) -> None:
        """Unauthenticated request returns 401/403."""
        response = client.get("/summary/diversification")
        assert response.status_code in (401, 403)

    def test_empty_portfolio_shape(self, client) -> None:
        """Returns correct shape with has_data=False on empty portfolio."""
        token = _register_and_login_unique(client, "div_empty@test.com")
        response = client.get(
            "/summary/diversification",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["has_data"] is False
        assert body["is_diversified"] is True
        assert body["recommendations"] == []

    def test_concentrated_portfolio_has_recommendation(
        self, client, db_session: Session
    ) -> None:
        """Endpoint returns at least one recommendation for a concentrated portfolio."""
        _register_and_login_unique(client, "div_conc@test.com")
        _make_cash_account(db_session, balance=1000.0)
        token = _register_and_login_unique(client, "div_conc2@test.com")
        response = client.get(
            "/summary/diversification",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["is_diversified"] is False
        assert len(body["recommendations"]) >= 1
        rec = body["recommendations"][0]
        assert "asset_class" in rec
        assert "percentage" in rec
        assert "problem" in rec
        assert "action" in rec
        assert "link_to" in rec

    def test_diversified_portfolio_no_recommendations(
        self, client, db_session: Session
    ) -> None:
        """Endpoint returns empty recommendations for a well-diversified portfolio."""
        _register_and_login_unique(client, "div_ok@test.com")
        _make_cash_account(db_session, balance=400.0)
        _make_crypto(db_session, price=200.0, qty=2.0)  # 400 PLN
        token = _register_and_login_unique(client, "div_ok2@test.com")
        response = client.get(
            "/summary/diversification",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["is_diversified"] is True
        assert body["recommendations"] == []
