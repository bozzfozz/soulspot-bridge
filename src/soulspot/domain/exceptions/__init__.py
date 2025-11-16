"""Domain exceptions."""

from typing import Any


class DomainException(Exception):
    """Base exception for all domain exceptions."""

    def __init__(self, message: str, *args: Any) -> None:
        super().__init__(message, *args)
        self.message = message


class EntityNotFoundException(DomainException):
    """Raised when an entity is not found."""

    def __init__(self, entity_type: str, entity_id: Any) -> None:
        super().__init__(f"{entity_type} with id {entity_id} not found")
        self.entity_type = entity_type
        self.entity_id = entity_id


class ValidationException(DomainException):
    """Raised when entity validation fails.

    Used to signal that an entity's invariants or business rules
    have been violated (e.g., invalid email format, negative price).
    """

    pass


class InvalidStateException(DomainException):
    """Raised when an entity is in an invalid state for the requested operation.

    Example: Attempting to cancel a download that's already completed,
    or trying to publish a draft that hasn't been reviewed.
    """

    pass


class DuplicateEntityException(DomainException):
    """Raised when trying to create a duplicate entity."""

    def __init__(self, entity_type: str, entity_id: Any) -> None:
        super().__init__(f"{entity_type} with id {entity_id} already exists")
        self.entity_type = entity_type
        self.entity_id = entity_id
