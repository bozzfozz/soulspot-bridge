# Hey future me - dieser Router ist für den Worker-Status-Indicator in der Sidebar!
#
# Er gibt den Status aller Background-Worker zurück (Token Refresh, Spotify Sync).
# Das Frontend pollt /api/workers/status/html alle 10 Sekunden via HTMX und zeigt
# animierte Icons im Sidebar-Footer an:
# - Idle: Icon pulsiert sanft (grün)
# - Active: Icon dreht sich
# - Error: Icon ist rot
#
# Hover zeigt einen kombinierten Tooltip mit Details zu allen Workern.
# Klick auf ein Icon navigiert zu den entsprechenden Settings.
#
# Wenn du neue Worker hinzufügst, füge sie hier in get_all_workers_status() ein.
# Das System ist bewusst simpel gehalten - kein ABC/Registry Pattern,
# einfach direkt die Worker vom app.state holen.
"""Background worker status API endpoints."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

router = APIRouter()


class WorkerStatusInfo(BaseModel):
    """Status information for a single worker."""

    name: str = Field(description="Display name of the worker")
    icon: str = Field(description="Font Awesome icon class")
    settings_url: str = Field(description="URL to settings page for this worker")
    running: bool = Field(description="Whether the worker is currently running")
    status: str = Field(description="Current status: idle, active, error, or stopped")
    details: dict[str, Any] = Field(
        default_factory=dict, description="Worker-specific details"
    )


class AllWorkersStatus(BaseModel):
    """Status of all background workers."""

    workers: dict[str, WorkerStatusInfo] = Field(
        description="Status information for each worker"
    )


def _format_time_ago(dt: datetime | None) -> str:
    """Format a datetime as a relative time string (e.g., 'vor 5 min').

    Hey future me - diese Funktion macht aus einem Timestamp einen lesbaren String.
    Wird für "Letzter Sync: vor 3 min" im Tooltip verwendet.
    """
    if dt is None:
        return "noch nie"

    now = datetime.utcnow()
    diff = now - dt

    seconds = int(diff.total_seconds())

    if seconds < 60:
        return "gerade eben"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"vor {minutes} min"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"vor {hours} h"
    else:
        days = seconds // 86400
        return f"vor {days} d"


def _format_time_until(minutes: int) -> str:
    """Format minutes until next action as readable string."""
    if minutes <= 0:
        return "jetzt"
    elif minutes < 60:
        return f"in {minutes} min"
    else:
        hours = minutes // 60
        return f"in {hours} h"


def _get_token_worker_status(request: Request) -> WorkerStatusInfo:
    """Get status for the Token Refresh Worker.

    Hey future me - holt den Status vom TokenRefreshWorker.
    Der Worker ist auf app.state.token_refresh_worker gespeichert (siehe lifecycle.py).
    """
    worker = getattr(request.app.state, "token_refresh_worker", None)

    if worker is None:
        return WorkerStatusInfo(
            name="Token Refresh",
            icon="fa-solid fa-key",
            settings_url="/settings?tab=spotify",
            running=False,
            status="stopped",
            details={"error": "Worker not initialized"},
        )

    raw_status = worker.get_status()

    # Determine status based on token availability
    # We can't async check token here, so we just show worker status
    status = "idle" if raw_status.get("running") else "stopped"

    return WorkerStatusInfo(
        name="Token Refresh",
        icon="fa-solid fa-key",
        settings_url="/settings?tab=spotify",
        running=raw_status.get("running", False),
        status=status,
        details={
            "check_interval_seconds": raw_status.get("check_interval_seconds", 300),
            "refresh_threshold_minutes": raw_status.get("refresh_threshold_minutes", 10),
        },
    )


def _get_spotify_sync_worker_status(request: Request) -> WorkerStatusInfo:
    """Get status for the Spotify Sync Worker.

    Hey future me - holt den Status vom SpotifySyncWorker.
    Der Worker ist auf app.state.spotify_sync_worker gespeichert.
    """
    worker = getattr(request.app.state, "spotify_sync_worker", None)

    if worker is None:
        return WorkerStatusInfo(
            name="Spotify Sync",
            icon="fa-brands fa-spotify",
            settings_url="/settings?tab=spotify",
            running=False,
            status="stopped",
            details={"error": "Worker not initialized"},
        )

    raw_status = worker.get_status()

    # Format last sync times
    last_syncs = raw_status.get("last_sync", {})
    formatted_last_syncs = {}
    for sync_type, iso_time in last_syncs.items():
        if iso_time:
            dt = datetime.fromisoformat(iso_time)
            formatted_last_syncs[sync_type] = _format_time_ago(dt)
        else:
            formatted_last_syncs[sync_type] = "noch nie"

    # Check for errors in stats
    stats = raw_status.get("stats", {})
    has_errors = any(
        s.get("last_error") is not None for s in stats.values() if isinstance(s, dict)
    )

    # Determine status
    if not raw_status.get("running"):
        status = "stopped"
    elif has_errors:
        status = "error"
    else:
        status = "idle"

    return WorkerStatusInfo(
        name="Spotify Sync",
        icon="fa-brands fa-spotify",
        settings_url="/settings?tab=spotify",
        running=raw_status.get("running", False),
        status=status,
        details={
            "last_syncs": formatted_last_syncs,
            "check_interval_seconds": raw_status.get("check_interval_seconds", 60),
            "stats": stats,
            "has_errors": has_errors,
        },
    )


# Hey future me – dieser Endpoint gibt JSON mit allen Worker-Statuses zurück.
# Nützlich für Debugging und falls jemand die API direkt nutzen will.
@router.get("/status")
async def get_all_workers_status(request: Request) -> AllWorkersStatus:
    """Get status of all background workers.

    Returns status information for:
    - Token Refresh Worker: Keeps Spotify OAuth tokens fresh
    - Spotify Sync Worker: Automatically syncs Spotify data

    Each worker includes:
    - name: Display name
    - icon: Font Awesome icon class
    - settings_url: Link to relevant settings page
    - running: Whether the worker is running
    - status: Current state (idle, active, error, stopped)
    - details: Worker-specific information
    """
    workers = {
        "token_refresh": _get_token_worker_status(request),
        "spotify_sync": _get_spotify_sync_worker_status(request),
    }

    return AllWorkersStatus(workers=workers)


# Hey future me – dieser Endpoint rendert das HTML-Partial für HTMX!
# Wird alle 10 Sekunden vom Sidebar-Footer gepollt.
# Gibt die Worker-Icons mit Status und den kombinierten Tooltip zurück.
@router.get("/status/html", response_class=HTMLResponse)
async def get_workers_status_html(request: Request) -> HTMLResponse:
    """Get HTML partial for worker status indicator.

    Returns an HTML fragment for HTMX polling that shows:
    - Worker icons with status-based animations
    - Combined tooltip with all worker details on hover

    Used by the sidebar footer to display real-time worker status.
    """
    # Get status for all workers
    token_status = _get_token_worker_status(request)
    spotify_status = _get_spotify_sync_worker_status(request)

    # Build last syncs HTML for tooltip
    last_syncs = spotify_status.details.get("last_syncs", {})
    sync_rows = ""
    sync_icons = {
        "artists": "🎤",
        "playlists": "📋",
        "liked_songs": "❤️",
        "saved_albums": "💿",
    }
    sync_labels = {
        "artists": "Artists",
        "playlists": "Playlists",
        "liked_songs": "Liked",
        "saved_albums": "Albums",
    }

    for sync_type, icon in sync_icons.items():
        last_time = last_syncs.get(sync_type, "noch nie")
        label = sync_labels.get(sync_type, sync_type)
        sync_rows += f'<div class="tooltip-sync-row">{icon} {label}: <span>{last_time}</span></div>'

    # Determine overall status for combined indicator
    # If any worker has error, show error; if any active, show active; else idle
    if spotify_status.status == "error" or token_status.status == "error":
        overall_status = "error"
    elif spotify_status.status == "active" or token_status.status == "active":
        overall_status = "active"
    elif spotify_status.status == "stopped" and token_status.status == "stopped":
        overall_status = "stopped"
    else:
        overall_status = "idle"

    # Status badge text
    status_text = {
        "idle": "Aktiv",
        "active": "Syncing",
        "error": "Fehler",
        "stopped": "Gestoppt",
    }

    html = f'''
<div class="worker-indicator-single" tabindex="0">
    <a href="{spotify_status.settings_url}" 
       class="worker-icon" 
       data-status="{overall_status}"
       aria-label="Background Workers: {status_text.get(overall_status, overall_status)}"
       title="">
        <i class="fa-solid fa-compact-disc"></i>
    </a>
    
    <div class="worker-tooltip" role="tooltip">
        <div class="tooltip-header">
            <span>Background Workers</span>
            <span class="tooltip-badge tooltip-badge-{overall_status}">{status_text.get(overall_status, overall_status)}</span>
        </div>
        
        <div class="tooltip-section">
            <div class="tooltip-row">
                <span><i class="{token_status.icon}"></i> {token_status.name}</span>
                <span class="tooltip-status tooltip-status-{token_status.status}">●</span>
            </div>
            <div class="tooltip-detail">
                Refresh alle {token_status.details.get("check_interval_seconds", 300) // 60} min
            </div>
        </div>
        
        <div class="tooltip-divider"></div>
        
        <div class="tooltip-section">
            <div class="tooltip-row">
                <span><i class="{spotify_status.icon}" style="color: #1DB954;"></i> {spotify_status.name}</span>
                <span class="tooltip-status tooltip-status-{spotify_status.status}">●</span>
            </div>
            <div class="tooltip-sync-grid">
                {sync_rows}
            </div>
        </div>
    </div>
</div>
'''

    return HTMLResponse(content=html)
