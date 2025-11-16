"""Library management API endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from soulspot.api.dependencies import get_db_session
from soulspot.application.use_cases.scan_library import (
    GetBrokenFilesUseCase,
    GetDuplicatesUseCase,
    ScanLibraryUseCase,
)

router = APIRouter(prefix="/library", tags=["library"])


class ScanRequest(BaseModel):
    """Request to start a library scan."""

    scan_path: str


class ScanResponse(BaseModel):
    """Response from library scan."""

    scan_id: str
    status: str
    scan_path: str
    total_files: int
    scanned_files: int
    broken_files: int
    duplicate_files: int
    progress_percent: float


@router.post("/scan")
async def start_library_scan(
    request: ScanRequest,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """Start a library scan.

    Args:
        request: Scan request with path
        session: Database session

    Returns:
        Scan information with ID
    """
    try:
        use_case = ScanLibraryUseCase(session)
        scan = await use_case.execute(request.scan_path)

        return {
            "scan_id": scan.id,
            "status": scan.status.value,
            "scan_path": scan.scan_path,
            "total_files": scan.total_files,
            "message": "Library scan started",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to start library scan: {str(e)}"
        ) from e


@router.get("/scan/{scan_id}")
async def get_scan_status(
    scan_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> ScanResponse:
    """Get library scan status.

    Args:
        scan_id: Scan ID
        session: Database session

    Returns:
        Scan status and progress
    """
    use_case = ScanLibraryUseCase(session)
    scan = await use_case.get_scan_status(scan_id)

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    return ScanResponse(
        scan_id=scan.id,
        status=scan.status.value,
        scan_path=scan.scan_path,
        total_files=scan.total_files,
        scanned_files=scan.scanned_files,
        broken_files=scan.broken_files,
        duplicate_files=scan.duplicate_files,
        progress_percent=scan.get_progress_percent(),
    )


@router.get("/duplicates")
async def get_duplicates(
    resolved: bool | None = Query(None, description="Filter by resolved status"),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """Get duplicate files.

    Args:
        resolved: Filter by resolved status
        session: Database session

    Returns:
        List of duplicate files
    """
    use_case = GetDuplicatesUseCase(session)
    duplicates = await use_case.execute(resolved=resolved)

    return {
        "duplicates": duplicates,
        "total_count": len(duplicates),
        "total_duplicate_files": sum(d["duplicate_count"] for d in duplicates),
        "total_wasted_bytes": sum(
            d["total_size_bytes"] - (d["total_size_bytes"] // d["duplicate_count"])
            for d in duplicates
        ),
    }


@router.get("/broken-files")
async def get_broken_files(
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """Get broken/corrupted files.

    Args:
        session: Database session

    Returns:
        List of broken files
    """
    use_case = GetBrokenFilesUseCase(session)
    broken_files = await use_case.execute()

    return {
        "broken_files": broken_files,
        "total_count": len(broken_files),
    }


@router.get("/stats")
async def get_library_stats(
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """Get library statistics.

    Args:
        session: Database session

    Returns:
        Library statistics
    """
    from sqlalchemy import func, select

    from soulspot.infrastructure.persistence.models import (
        FileDuplicateModel,
        TrackModel,
    )

    # Count total tracks
    total_tracks_stmt = select(func.count(TrackModel.id))
    total_tracks_result = await session.execute(total_tracks_stmt)
    total_tracks = total_tracks_result.scalar() or 0

    # Count tracks with files
    tracks_with_files_stmt = select(func.count(TrackModel.id)).where(
        TrackModel.file_path.isnot(None)
    )
    tracks_with_files_result = await session.execute(tracks_with_files_stmt)
    tracks_with_files = tracks_with_files_result.scalar() or 0

    # Count broken files
    broken_files_stmt = select(func.count(TrackModel.id)).where(
        TrackModel.is_broken == True  # noqa: E712
    )
    broken_files_result = await session.execute(broken_files_stmt)
    broken_files = broken_files_result.scalar() or 0

    # Count duplicate groups
    duplicates_stmt = select(func.count(FileDuplicateModel.id)).where(
        FileDuplicateModel.resolved == False  # noqa: E712
    )
    duplicates_result = await session.execute(duplicates_stmt)
    duplicate_groups = duplicates_result.scalar() or 0

    # Total file size
    total_size_stmt = select(func.sum(TrackModel.file_size)).where(
        TrackModel.file_size.isnot(None)
    )
    total_size_result = await session.execute(total_size_stmt)
    total_size = total_size_result.scalar() or 0

    return {
        "total_tracks": total_tracks,
        "tracks_with_files": tracks_with_files,
        "broken_files": broken_files,
        "duplicate_groups": duplicate_groups,
        "total_size_bytes": total_size,
        "scanned_percentage": (
            (tracks_with_files / total_tracks * 100) if total_tracks > 0 else 0
        ),
    }
