"""Repository for Transaction and Dividend models."""

from datetime import datetime

from sqlmodel import Session

from app.models.portfolio import Dividend, Transaction
from app.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session: Session) -> None:
        super().__init__(Transaction, session)

    def bulk_create(self, records: list[dict]) -> list[Transaction]:
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


class DividendRepository(BaseRepository[Dividend]):
    def __init__(self, session: Session) -> None:
        super().__init__(Dividend, session)

    def bulk_create(self, records: list[dict]) -> list[Dividend]:
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
