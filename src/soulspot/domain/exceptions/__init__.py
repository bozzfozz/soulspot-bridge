"""Domain exceptions."""

from typing import Any


class DomainException(Exception):
    """Base exception for all domain exceptions."""

    # Hey future me, we store message as an attribute so code can inspect it without parsing str(exception).
    # The *args lets subclasses pass extra context. This is your base class - DON'T raise it directly!
    # Always use a specific subclass (EntityNotFound, Validation, etc) so callers can catch precisely.
    def __init__(self, message: str, *args: Any) -> None:
        super().__init__(message, *args)
        self.message = message


class EntityNotFoundException(DomainException):
    """Raised when an entity is not found."""

    # Yo, this is for "get by ID" operations that fail - Track 123 doesn't exist, Playlist "abc" not found.
    # We store entity_type and entity_id separately so error handlers can log them structured (not just
    # string parsing). Use this instead of returning None when "not found" is truly exceptional! If you
    # expect missing entities often, use Optional return type instead of exceptions (exceptions are slow!).
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

    # Listen, this is for uniqueness violations - trying to create a Watchlist for an artist that already
    # has one, importing a track with duplicate Spotify ID, etc. DON'T use this for DB unique constraint
    # violations (that's infrastructure layer)! This is domain logic - "business rule says this must be unique".
    # Callers should catch this and show user-friendly "already exists" message, not 500 error!
    def __init__(self, entity_type: str, entity_id: Any) -> None:
        super().__init__(f"{entity_type} with id {entity_id} already exists")
        self.entity_type = entity_type
        self.entity_id = entity_id
