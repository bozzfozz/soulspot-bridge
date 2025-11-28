# Spotify Session Refactoring Plan

> **Status:** Planned  
> **Priority:** Medium  
> **Created:** 2025-11-28  
> **Estimated Effort:** 2-3 hours

## Overview

Refaktoriere alle Spotify-OAuth-spezifischen "Session"-Klassen zu "SpotifySession"-Präfix für bessere semantische Klarheit. Vermeidet Verwechslung mit generischen "Session"-Konzepten (z.B. DB-Sessions, User-Sessions) und ermöglicht spätere Erweiterung für andere Streaming-Dienste (Tidal, Deezer, etc.).

## Current State

| Current Name | Location |
|-------------|----------|
| `Session` | `session_store.py` (dataclass) |
| `SessionStore` | `session_store.py` (in-memory store) |
| `DatabaseSessionStore` | `session_store.py` (persistent store) |
| `SessionModel` | `models.py` (SQLAlchemy model) |
| `SessionRepository` | `repositories.py` |
| `sessions` | Database table name |

## Target State

| New Name | Location |
|----------|----------|
| `SpotifySession` | `session_store.py` |
| `SpotifySessionStore` | `session_store.py` |
| `DatabaseSpotifySessionStore` | `session_store.py` |
| `SpotifySessionModel` | `models.py` |
| `SpotifySessionRepository` | `repositories.py` |
| `spotify_sessions` | Database table name |

---

## Implementation Steps

### Step 1: session_store.py (MAJOR)

**File:** `src/soulspot/application/services/session_store.py`

**Changes:**
```python
# BEFORE (line ~16)
@dataclass
class Session:
    """User OAuth session with tokens and state."""

# AFTER
@dataclass
class SpotifySession:
    """Spotify OAuth session with tokens and state."""
```

```python
# BEFORE (line ~83)
class SessionStore:
    """In-memory OAuth session store."""
    
    def create_session(...) -> Session:
    def get_session(...) -> Session | None:

# AFTER
class SpotifySessionStore:
    """In-memory Spotify session store."""
    
    def create_session(...) -> SpotifySession:
    def get_session(...) -> SpotifySession | None:
```

```python
# BEFORE (line ~255)
class DatabaseSessionStore:
    """Database-backed session store."""

# AFTER
class DatabaseSpotifySessionStore:
    """Database-backed Spotify session store."""
```

**Internal import to update:**
```python
# BEFORE (inside DatabaseSessionStore methods)
from soulspot.infrastructure.persistence.repositories import SessionRepository

# AFTER
from soulspot.infrastructure.persistence.repositories import SpotifySessionRepository
```

---

### Step 2: services/__init__.py

**File:** `src/soulspot/application/services/__init__.py`

```python
# BEFORE
from soulspot.application.services.session_store import Session, SessionStore

__all__ = [
    ...
    "Session",
    "SessionStore",
    ...
]

# AFTER
from soulspot.application.services.session_store import SpotifySession, SpotifySessionStore

__all__ = [
    ...
    "SpotifySession",
    "SpotifySessionStore",
    ...
]
```

---

### Step 3: dependencies.py

**File:** `src/soulspot/api/dependencies.py`

```python
# BEFORE (line ~9-11)
from soulspot.application.services.session_store import (
    DatabaseSessionStore,
)

# AFTER
from soulspot.application.services.session_store import (
    DatabaseSpotifySessionStore,
)
```

```python
# BEFORE (line ~48)
def get_session_store(request: Request) -> DatabaseSessionStore:
    return request.app.state.session_store

# AFTER
def get_session_store(request: Request) -> DatabaseSpotifySessionStore:
    return request.app.state.session_store
```

---

### Step 4: auth.py

**File:** `src/soulspot/api/routers/auth.py`

```python
# BEFORE (line ~12)
from soulspot.application.services.session_store import DatabaseSessionStore

# AFTER
from soulspot.application.services.session_store import DatabaseSpotifySessionStore
```

**Update all 6 function signatures:**
```python
# BEFORE (lines 31, 95, 200, 272, 313, 386)
async def some_endpoint(
    session_store: DatabaseSessionStore = Depends(get_session_store),
):

# AFTER
async def some_endpoint(
    session_store: DatabaseSpotifySessionStore = Depends(get_session_store),
):
```

---

### Step 5: models.py

**File:** `src/soulspot/infrastructure/persistence/models.py`

```python
# BEFORE (line ~527)
class SessionModel(Base):
    """User session with OAuth tokens."""
    __tablename__ = "sessions"
    
    # Indexes
    __table_args__ = (
        Index("ix_sessions_last_accessed", "last_accessed_at"),
        Index("ix_sessions_token_expires", "token_expires_at"),
    )

# AFTER
class SpotifySessionModel(Base):
    """Spotify OAuth session with tokens."""
    __tablename__ = "spotify_sessions"
    
    # Indexes
    __table_args__ = (
        Index("ix_spotify_sessions_last_accessed", "last_accessed_at"),
        Index("ix_spotify_sessions_token_expires", "token_expires_at"),
    )
```

---

### Step 6: repositories.py

**File:** `src/soulspot/infrastructure/persistence/repositories.py`

```python
# BEFORE (line ~8)
if TYPE_CHECKING:
    from soulspot.application.services.session_store import Session

# AFTER
if TYPE_CHECKING:
    from soulspot.application.services.session_store import SpotifySession
```

```python
# BEFORE (line ~34-44)
from .models import (
    ...
    SessionModel,
    ...
)

# AFTER
from .models import (
    ...
    SpotifySessionModel,
    ...
)
```

```python
# BEFORE (line ~2197)
class SessionRepository:
    """Repository for session persistence."""
    
    async def create(self, session: "Session") -> None:
        db_session = SessionModel(...)

# AFTER
class SpotifySessionRepository:
    """Repository for Spotify session persistence."""
    
    async def create(self, session: "SpotifySession") -> None:
        db_session = SpotifySessionModel(...)
```

---

### Step 7: lifecycle.py

**File:** `src/soulspot/infrastructure/lifecycle.py`

```python
# BEFORE (line ~128)
from soulspot.application.services.session_store import DatabaseSessionStore

# AFTER
from soulspot.application.services.session_store import DatabaseSpotifySessionStore
```

```python
# BEFORE (line ~135)
session_store = DatabaseSessionStore(
    session_timeout_seconds=settings.api.session_max_age,
    get_db_session=get_db_session_for_store,
)

# AFTER
session_store = DatabaseSpotifySessionStore(
    session_timeout_seconds=settings.api.session_max_age,
    get_db_session=get_db_session_for_store,
)
```

---

### Step 8: Database Migration

> **Hinweis:** Da wir noch nicht in Produktion sind, können wir die DB einfach neu erstellen statt eine komplexe Migration zu schreiben.

**Option A: DB löschen und neu erstellen (empfohlen für Dev)**
```bash
# Alte DB löschen (lokaler Dev-Pfad)
rm -f ./soulspot.db

# Oder für Docker:
# rm -f /config/soulspot.db

# Neue DB mit allen Migrationen erstellen
alembic upgrade head
```

**Option B: Migration für Dokumentation (falls später Prod-Migration nötig)**

**New File:** `alembic/versions/YYYYMMDD_rename_sessions_to_spotify_sessions.py`

```python
"""Rename sessions table to spotify_sessions.

Revision ID: nn26009ppq57
Revises: (previous revision)
Create Date: 2025-11-28
"""
from alembic import op

revision = "nn26009ppq57"
down_revision = "gg20003jj51"  # Update to latest revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Rename sessions table to spotify_sessions for semantic clarity."""
    # SQLite doesn't support ALTER INDEX, so we drop and recreate
    
    # Drop old indexes
    op.drop_index("ix_sessions_last_accessed", table_name="sessions")
    op.drop_index("ix_sessions_token_expires", table_name="sessions")
    
    # Rename table
    op.rename_table("sessions", "spotify_sessions")
    
    # Create new indexes with updated names
    op.create_index(
        "ix_spotify_sessions_last_accessed",
        "spotify_sessions",
        ["last_accessed_at"]
    )
    op.create_index(
        "ix_spotify_sessions_token_expires",
        "spotify_sessions",
        ["token_expires_at"]
    )


def downgrade() -> None:
    """Revert table rename."""
    # Drop new indexes
    op.drop_index("ix_spotify_sessions_last_accessed", table_name="spotify_sessions")
    op.drop_index("ix_spotify_sessions_token_expires", table_name="spotify_sessions")
    
    # Rename table back
    op.rename_table("spotify_sessions", "sessions")
    
    # Recreate old indexes
    op.create_index(
        "ix_sessions_last_accessed",
        "sessions",
        ["last_accessed_at"]
    )
    op.create_index(
        "ix_sessions_token_expires",
        "sessions",
        ["token_expires_at"]
    )
```

---

### Step 9: Unit Tests

**File:** `tests/unit/application/services/test_session_store.py`

```python
# BEFORE
from soulspot.application.services.session_store import Session, SessionStore

class TestSession:
    def test_session_creation(self):
        session = Session(session_id="test")

class TestSessionStore:
    def test_create_session(self):
        store = SessionStore()

# AFTER
from soulspot.application.services.session_store import SpotifySession, SpotifySessionStore

class TestSpotifySession:
    def test_session_creation(self):
        session = SpotifySession(session_id="test")

class TestSpotifySessionStore:
    def test_create_session(self):
        store = SpotifySessionStore()
```

---

## Validation Checklist

After implementation, verify:

- [ ] `make format` passes
- [ ] `make lint` passes (ruff)
- [ ] `make type-check` passes (mypy)
- [ ] `pytest tests/ -v` all tests pass
- [ ] DB neu erstellt: `rm -f ./soulspot.db && alembic upgrade head`
- [ ] Manual test: OAuth login flow still works
- [ ] Manual test: Session persists after Docker restart

---

## Optional Follow-up (Separate PR)

Consider renaming dependency functions for full consistency:

| Current | Suggested |
|---------|-----------|
| `get_session_store()` | `get_spotify_session_store()` |
| `get_session_id()` | `get_spotify_session_id()` |

This would require updating all `Depends(get_session_store)` calls.

---

## Files Summary

| File | Change Type |
|------|-------------|
| `src/soulspot/application/services/session_store.py` | Major (3 class renames) |
| `src/soulspot/application/services/__init__.py` | Exports |
| `src/soulspot/api/dependencies.py` | Import + type hint |
| `src/soulspot/api/routers/auth.py` | Import + 6 type hints |
| `src/soulspot/infrastructure/persistence/models.py` | Class + table rename |
| `src/soulspot/infrastructure/persistence/repositories.py` | Class rename + imports |
| `src/soulspot/infrastructure/lifecycle.py` | Import + instantiation |
| `alembic/versions/xxx_rename_sessions_to_spotify.py` | New migration |
| `tests/unit/application/services/test_session_store.py` | Test class renames |

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| ~~Migration breaks existing sessions~~ | **Kein Risiko** - Nicht in Produktion, DB kann neu erstellt werden |
| Missed rename causes runtime error | Full test suite + type checking catches this |
| SQLite index rename limitations | **Nicht relevant** - DB wird neu erstellt |

---

## Execution Order

1. Update `models.py` (SpotifySessionModel, neue Tabelle `spotify_sessions`)
2. Update `repositories.py` (SpotifySessionRepository)
3. Update `session_store.py` (all 3 classes)
4. Update `__init__.py` exports
5. Update `dependencies.py`
6. Update `auth.py`
7. Update `lifecycle.py`
8. Update tests
9. Run `make format && make lint && make type-check`
10. Run `pytest tests/ -v`
11. **DB neu erstellen:** `rm -f ./soulspot.db && alembic upgrade head`
12. Manual verification (Spotify re-auth nötig)
