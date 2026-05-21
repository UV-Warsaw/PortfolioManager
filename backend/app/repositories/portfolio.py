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
        """Return net cost basis per account (BUY amounts minus SELL amounts).

        Values are stored in PLN — USD transactions are converted during import.

        Returns:
            Dict mapping account name to net invested value (PLN).
        """
        net_val = func.sum(
            case(
                (Transaction.type == "BUY", Transaction.amount),
                else_=-Transaction.amount,
            )
        ).label("net_value")

        stmt = (
            select(Transaction.account, net_val)
            .where(Transaction.amount.is_not(None))
            .group_by(Transaction.account)
        )
        rows = self.session.exec(stmt).all()
        return {
            row[0]: round(float(row[1]), 2)
            for row in rows
            if row[0] is not None and row[1] is not None
        }


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
