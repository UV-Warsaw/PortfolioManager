"""Repository for Transaction and Dividend models."""

from datetime import datetime

from sqlalchemy import case, func
from sqlmodel import Session, select

from app.models.portfolio import Dividend, Transaction
from app.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    """Repository for Transaction database operations."""

    def __init__(self, session: Session) -> None:
        """Initialise with a database session."""
        super().__init__(Transaction, session)

    def _exists(
        self,
        date: datetime | None,
        ticker: str | None,
        quantity: float | None,
        account: str | None,
        user_id: int,
    ) -> bool:
        """Return True if a matching transaction already exists in the database."""
        stmt = select(Transaction).where(
            Transaction.date == date,
            Transaction.ticker == ticker,
            Transaction.quantity == quantity,
            Transaction.account == account,
            Transaction.user_id == user_id,
        )
        return self.session.exec(stmt).first() is not None

    def bulk_create(self, records: list[dict], user_id: int) -> list[Transaction]:
        """Insert a list of transaction dicts without deduplication checking."""
        created: list[Transaction] = []
        for rec in records:
            date_val = rec.get("date")
            if isinstance(date_val, str):
                date_val = datetime.fromisoformat(date_val)
            tx = Transaction(
                date=date_val,
                ticker=rec.get("ticker"),
                type=rec.get("type"),
                quantity=rec.get("quantity"),
                price=rec.get("price"),
                market_price=rec.get("market_price"),
                amount=rec.get("amount"),
                raw=rec.get("raw"),
                account=rec.get("account"),
                user_id=user_id,
            )
            self.session.add(tx)
            created.append(tx)
        self.session.commit()
        for tx in created:
            self.session.refresh(tx)
        return created

    def bulk_create_with_dedup(
        self, records: list[dict], user_id: int
    ) -> tuple[list[Transaction], int]:
        """Insert transactions, skipping duplicates keyed by (date, ticker, quantity, account).

        Returns:
            A tuple of (created_transactions, skipped_count).
        """
        created: list[Transaction] = []
        skipped = 0
        for rec in records:
            date_val = rec.get("date")
            if isinstance(date_val, str):
                date_val = datetime.fromisoformat(date_val)
            if self._exists(
                date_val, rec.get("ticker"), rec.get("quantity"), rec.get("account"), user_id
            ):
                skipped += 1
                continue
            tx = Transaction(
                date=date_val,
                ticker=rec.get("ticker"),
                type=rec.get("type"),
                quantity=rec.get("quantity"),
                price=rec.get("price"),
                market_price=rec.get("market_price"),
                amount=rec.get("amount"),
                raw=rec.get("raw"),
                account=rec.get("account"),
                user_id=user_id,
            )
            self.session.add(tx)
            created.append(tx)
        self.session.commit()
        for tx in created:
            self.session.refresh(tx)
        return created, skipped

    def delete_by_account(self, account: str, user_id: int) -> int:
        """Delete all transactions for the given user+account and return deleted row count."""
        from sqlmodel import delete as sql_delete

        stmt = sql_delete(Transaction).where(Transaction.account == account, Transaction.user_id == user_id)
        result = self.session.exec(stmt)
        self.session.commit()
        return result.rowcount

    def get_holdings(self, account: str | None = None, user_id: int | None = None) -> list[dict]:
        """Return active holdings aggregated per ticker and account.

        Buy quantities are summed; sell quantities are subtracted.
        Positions with net quantity <= 0 are excluded (fully sold).

        Args:
            account: Optional account filter (IKE, PLN, USD).

        Returns:
            List of dicts with keys ticker, account, quantity.
        """
        net_qty = func.sum(
            case(
                (Transaction.type.in_(["SELL", "Stock sell"]), -Transaction.quantity),
                else_=Transaction.quantity,
            )
        ).label("net_quantity")

        stmt = (
            select(Transaction.ticker, Transaction.account, net_qty)
            .where(Transaction.quantity.is_not(None))
            .group_by(Transaction.ticker, Transaction.account)
        )
        if user_id is not None:
            stmt = stmt.where(Transaction.user_id == user_id)
        if account:
            stmt = stmt.where(Transaction.account == account)

        rows = self.session.exec(stmt).all()
        return [
            {"ticker": row[0], "account": row[1], "quantity": row[2]}
            for row in rows
            if row[2] is not None and row[2] > 0
        ]

    def get_account_values(self, user_id: int | None = None) -> dict[str, float]:
        """Return current market value per account for the given user."""
        market_val = func.sum(Transaction.market_price * Transaction.quantity).label(
            "market_value"
        )

        stmt = (
            select(Transaction.account, market_val)
            .where(
                Transaction.market_price.is_not(None),
                Transaction.quantity.is_not(None),
                Transaction.ticker.is_not(None),
                Transaction.type.in_(["BUY", "Stock purchase"]),
            )
            .group_by(Transaction.account)
        )
        if user_id is not None:
            stmt = stmt.where(Transaction.user_id == user_id)
        rows = self.session.exec(stmt).all()
        return {
            row[0]: round(float(row[1]), 2)
            for row in rows
            if row[0] is not None and row[1] is not None
        }

    def get_cost_basis(self, user_id: int | None = None) -> dict[str, float]:
        """Return cost basis per account for the given user."""
        cost_val = func.sum(Transaction.price * Transaction.quantity).label("cost")

        stmt = (
            select(Transaction.account, cost_val)
            .where(
                Transaction.price.is_not(None),
                Transaction.quantity.is_not(None),
                Transaction.ticker.is_not(None),
                Transaction.type == "BUY",
            )
            .group_by(Transaction.account)
        )
        if user_id is not None:
            stmt = stmt.where(Transaction.user_id == user_id)
        rows = self.session.exec(stmt).all()
        return {
            row[0]: round(float(row[1]), 2)
            for row in rows
            if row[0] is not None and row[1] is not None
        }

    def get_top_holdings(self, limit: int = 10, user_id: int | None = None) -> list[tuple[str, float]]:
        """Return the top N holdings by current market value for the given user."""
        market_val = func.sum(Transaction.market_price * Transaction.quantity).label(
            "market_value"
        )

        stmt = (
            select(Transaction.ticker, market_val)
            .where(
                Transaction.market_price.is_not(None),
                Transaction.quantity.is_not(None),
                Transaction.ticker.is_not(None),
                Transaction.type.in_(["BUY", "Stock purchase"]),
            )
            .group_by(Transaction.ticker)
            .having(market_val > 0)
            .order_by(market_val.desc())
            .limit(limit)
        )
        if user_id is not None:
            stmt = stmt.where(Transaction.user_id == user_id)
        rows = self.session.exec(stmt).all()
        return [(row[0], round(float(row[1]), 2)) for row in rows if row[0] is not None]


class DividendRepository(BaseRepository[Dividend]):
    """Repository for Dividend database operations."""

    def __init__(self, session: Session) -> None:
        """Initialise with a database session."""
        super().__init__(Dividend, session)

    def _exists(
        self,
        date: datetime | None,
        ticker: str | None,
        amount: float | None,
        account: str | None,
        user_id: int,
    ) -> bool:
        """Return True if a matching dividend already exists in the database."""
        stmt = select(Dividend).where(
            Dividend.date == date,
            Dividend.ticker == ticker,
            Dividend.amount == amount,
            Dividend.account == account,
            Dividend.user_id == user_id,
        )
        return self.session.exec(stmt).first() is not None

    def bulk_create(self, records: list[dict], user_id: int) -> list[Dividend]:
        """Insert a list of dividend dicts without deduplication checking."""
        created: list[Dividend] = []
        for rec in records:
            date_val = rec.get("date")
            if isinstance(date_val, str):
                date_val = datetime.fromisoformat(date_val)
            div = Dividend(
                date=date_val,
                ticker=rec.get("ticker"),
                amount=rec.get("amount"),
                currency=rec.get("currency"),
                raw=rec.get("raw"),
                account=rec.get("account"),
                user_id=user_id,
            )
            self.session.add(div)
            created.append(div)
        self.session.commit()
        for div in created:
            self.session.refresh(div)
        return created

    def delete_by_account(self, account: str, user_id: int) -> int:
        """Delete all dividends for the given user+account."""
        from sqlmodel import delete as sql_delete

        stmt = sql_delete(Dividend).where(Dividend.account == account, Dividend.user_id == user_id)
        result = self.session.exec(stmt)
        self.session.commit()
        return result.rowcount

    def bulk_create_with_dedup(self, records: list[dict], user_id: int) -> tuple[list[Dividend], int]:
        """Insert dividends, skipping duplicates keyed by (date, ticker, amount, account)."""
        created: list[Dividend] = []
        skipped = 0
        for rec in records:
            date_val = rec.get("date")
            if isinstance(date_val, str):
                date_val = datetime.fromisoformat(date_val)
            if self._exists(
                date_val, rec.get("ticker"), rec.get("amount"), rec.get("account"), user_id
            ):
                skipped += 1
                continue
            div = Dividend(
                date=date_val,
                ticker=rec.get("ticker"),
                amount=rec.get("amount"),
                currency=rec.get("currency"),
                raw=rec.get("raw"),
                account=rec.get("account"),
                user_id=user_id,
            )
            self.session.add(div)
            created.append(div)
        self.session.commit()
        for div in created:
            self.session.refresh(div)
        return created, skipped

    def get_yearly_summary(self, account: str | None = None, user_id: int | None = None) -> list[dict]:
        """Get yearly dividend summary for the given user."""
        from sqlalchemy import extract

        year_col = extract("year", Dividend.date).label("year")
        total_col = func.sum(Dividend.amount).label("total")

        stmt = select(year_col, total_col).where(Dividend.date.is_not(None))

        if user_id is not None:
            stmt = stmt.where(Dividend.user_id == user_id)
        if account:
            stmt = stmt.where(Dividend.account == account)

        stmt = stmt.group_by(year_col).order_by(year_col)

        rows = self.session.exec(stmt).all()
        return [
            {"year": int(row[0]), "total": round(float(row[1]) if row[1] else 0.0, 2)}
            for row in rows
        ]

    def get_monthly_timeline(
        self, year: int | None = None, account: str | None = None, user_id: int | None = None
    ) -> list[dict]:
        """Get monthly dividend timeline for the given user."""
        from sqlalchemy import extract

        month_col = extract("month", Dividend.date).label("month")
        total_col = func.sum(Dividend.amount).label("total")

        stmt = select(month_col, total_col).where(Dividend.date.is_not(None))

        if user_id is not None:
            stmt = stmt.where(Dividend.user_id == user_id)
        if year:
            year_col = extract("year", Dividend.date)
            stmt = stmt.where(year_col == year)
        if account:
            stmt = stmt.where(Dividend.account == account)

        stmt = stmt.group_by(month_col).order_by(month_col)

        rows = self.session.exec(stmt).all()
        return [
            {"month": int(row[0]), "total": round(float(row[1]) if row[1] else 0.0, 2)}
            for row in rows
        ]
