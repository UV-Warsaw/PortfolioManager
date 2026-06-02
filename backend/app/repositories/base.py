"""Base repository providing generic CRUD operations."""

from typing import Generic, TypeVar

from sqlmodel import Session, SQLModel, select

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    """Generic repository with common database operations."""

    def __init__(self, model: type[ModelType], session: Session) -> None:
        """
        Initialise the repository.

        Args:
            model: SQLModel class managed by this repository.
            session: Active database session.
        """
        self.model = model
        self.session = session

    def create(self, record: ModelType) -> ModelType:
        """
        Create and persist a new record.

        Args:
            record: Model instance to persist.

        Returns:
            The persisted model instance.
        """
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def update(self, record: ModelType) -> ModelType:
        """
        Update and persist an existing record.

        Args:
            record: Model instance with updated values.

        Returns:
            The updated model instance.
        """
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def get_by_id(self, record_id: int) -> ModelType | None:
        """
        Retrieve a single record by primary key.

        Args:
            record_id: Primary key value.

        Returns:
            Model instance or None if not found.
        """
        return self.session.get(self.model, record_id)

    def get_all(self) -> list[ModelType]:
        """
        Retrieve all records for the model.

        Returns:
            List of model instances.
        """
        statement = select(self.model)
        return list(self.session.exec(statement).all())

    def delete(self, record: ModelType) -> None:
        """
        Delete a record from the database.

        Args:
            record: Model instance to delete.
        """
        self.session.delete(record)
        self.session.commit()
