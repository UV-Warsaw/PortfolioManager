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
    ) -> bool:
        """Return True if a matching transaction already exists in the database."""
        stmt = select(Transaction).where(
            Transaction.date == date,
            Transaction.ticker == ticker,
            Transaction.quantity == quantity,
            Transaction.account == account,
        )
        return self.session.exec(stmt).first() is not None

    def bulk_create(self, records: list[dict]) -> list[Transaction]:
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
            )
            self.session.add(tx)
            created.append(tx)
        self.session.commit()
        for tx in created:
            self.session.refresh(tx)
        return created

    def bulk_create_with_dedup(
        self, records: list[dict]
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
                date_val, rec.get("ticker"), rec.get("quantity"), rec.get("account")
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
            )
            self.session.add(tx)
            created.append(tx)
        self.session.commit()
        for tx in created:
            self.session.refresh(tx)
        return created, skipped

    def delete_by_account(self, account: str) -> int:
        """Delete all transactions for the given account and return the deleted row count.

        Used during re-import to clear stale data before inserting fresh records.

        Args:
            account: Account identifier (IKE, PLN, USD).

        Returns:
            Number of rows deleted.
        """
        from sqlmodel import delete as sql_delete

        stmt = sql_delete(Transaction).where(Transaction.account == account)
        result = self.session.exec(stmt)
        self.session.commit()
        return result.rowcount

    def get_holdings(self, account: str | None = None) -> list[dict]:
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
                (Transaction.type == "SELL", -Transaction.quantity),
                else_=Transaction.quantity,
            )
        ).label("net_quantity")

        stmt = (
            select(Transaction.ticker, Transaction.account, net_qty)
            .where(Transaction.quantity.is_not(None))
            .group_by(Transaction.ticker, Transaction.account)
        )
        if account:
            stmt = stmt.where(Transaction.account == account)

        rows = self.session.exec(stmt).all()
        return [
            {"ticker": row[0], "account": row[1], "quantity": row[2]}
            for row in rows
            if row[2] is not None and row[2] > 0
        ]

    def get_account_values(self) -> dict[str, float]:
        """Return current market value per account — sum of market_price * quantity.

        Only open BUY positions with a non-null market_price and ticker are included.
        Cash-operation rows (ticker IS NULL or type != BUY) are excluded.

        Values are stored in PLN — USD prices are converted during import.

        Returns:
            Dict mapping account name to current market value (PLN).
        """
        market_val = func.sum(Transaction.market_price * Transaction.quantity).label(
            "market_value"
        )

        stmt = (
            select(Transaction.account, market_val)
            .where(
                Transaction.market_price.is_not(None),
                Transaction.quantity.is_not(None),
                Transaction.ticker.is_not(None),
                Transaction.type == "BUY",
            )
            .group_by(Transaction.account)
        )
        rows = self.session.exec(stmt).all()
        return {
            row[0]: round(float(row[1]), 2)
            for row in rows
            if row[0] is not None and row[1] is not None
        }

    def get_top_holdings(self, limit: int = 10) -> list[tuple[str, float]]:
        """Return the top N holdings by current market value across all accounts.

        Market value is computed as sum(market_price * quantity) for BUY rows.
        Only positions with a non-null market_price and ticker are considered.

        Args:
            limit: Maximum number of holdings to return.

        Returns:
            List of (ticker, market_value) tuples ordered by market_value descending.
        """
        market_val = func.sum(Transaction.market_price * Transaction.quantity).label(
            "market_value"
        )

        stmt = (
            select(Transaction.ticker, market_val)
            .where(
                Transaction.market_price.is_not(None),
                Transaction.quantity.is_not(None),
                Transaction.ticker.is_not(None),
                Transaction.type == "BUY",
            )
            .group_by(Transaction.ticker)
            .having(market_val > 0)
            .order_by(market_val.desc())
            .limit(limit)
        )
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
    ) -> bool:
        """Return True if a matching dividend already exists in the database."""
        stmt = select(Dividend).where(
            Dividend.date == date,
            Dividend.ticker == ticker,
            Dividend.amount == amount,
            Dividend.account == account,
        )
        return self.session.exec(stmt).first() is not None

    def bulk_create(self, records: list[dict]) -> list[Dividend]:
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
            )
            self.session.add(div)
            created.append(div)
        self.session.commit()
        for div in created:
            self.session.refresh(div)
        return created

    def delete_by_account(self, account: str) -> int:
        """Delete all dividends for the given account and return the deleted row count.

        Used during re-import to clear stale data before inserting fresh records.

        Args:
            account: Account identifier (IKE, PLN, USD).

        Returns:
            Number of rows deleted.
        """
        from sqlmodel import delete as sql_delete

        stmt = sql_delete(Dividend).where(Dividend.account == account)
        result = self.session.exec(stmt)
        self.session.commit()
        return result.rowcount

    def bulk_create_with_dedup(self, records: list[dict]) -> tuple[list[Dividend], int]:
        """Insert dividends, skipping duplicates keyed by (date, ticker, amount, account).

        Returns:
            A tuple of (created_dividends, skipped_count).
        """
        created: list[Dividend] = []
        skipped = 0
        for rec in records:
            date_val = rec.get("date")
            if isinstance(date_val, str):
                date_val = datetime.fromisoformat(date_val)
            if self._exists(
                date_val, rec.get("ticker"), rec.get("amount"), rec.get("account")
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
            )
            self.session.add(div)
            created.append(div)
        self.session.commit()
        for div in created:
            self.session.refresh(div)
        return created, skipped

    def get_yearly_summary(self, account: str | None = None) -> list[dict]:
        """Get dividend summary grouped by year.

        Args:
            account: Optional account filter (IKE, PLN, USD).

        Returns:
            List of dicts with 'year' and 'total' keys.
        """
        stmt = (
            select(
                func.strftime("%Y", Dividend.date).label("year"),
                func.coalesce(func.sum(Dividend.amount), 0).label("total"),
            )
            .group_by("year")
            .order_by("year")
        )

        if account:
            stmt = stmt.where(Dividend.account == account)

        results = self.session.exec(stmt).all()
        return [{"year": r[0], "total": float(r[1])} for r in results]

    def get_monthly_timeline(
        self, year: int | None = None, account: str | None = None
    ) -> list[dict]:
        """Get dividend timeline by month.

        Args:
            year: Optional year filter — returns 12 months for that year.
            account: Optional account filter (IKE, PLN, USD).

        Returns:
            List of dicts with 'month', 'total', and optionally 'year' keys.
        """
        if year:
            stmt = (
                select(
                    func.strftime("%m", Dividend.date).label("month"),
                    func.coalesce(func.sum(Dividend.amount), 0).label("total"),
                )
                .where(func.strftime("%Y", Dividend.date) == str(year))
                .group_by("month")
            )
        else:
            stmt = select(
                func.strftime("%Y-%m", Dividend.date).label("month"),
                func.coalesce(func.sum(Dividend.amount), 0).label("total"),
            ).group_by("month")

        if account:
            stmt = stmt.where(Dividend.account == account)

        stmt = stmt.order_by("month")
        results = self.session.exec(stmt).all()
        return [{"month": r[0], "total": float(r[1])} for r in results]
