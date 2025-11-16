"""Example demonstrating library scanner functionality.

This example shows how to use the library scanning features to:
1. Scan a music library directory
2. Detect duplicate files
3. Find broken/corrupted files
4. Get library statistics
"""

import asyncio
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from soulspot.application.services.library_scanner import LibraryScannerService
from soulspot.application.use_cases.scan_library import (
    GetBrokenFilesUseCase,
    GetDuplicatesUseCase,
    ScanLibraryUseCase,
)
from soulspot.infrastructure.persistence.models import Base


async def main() -> None:
    """Run library scanner example."""
    # Create database engine and session
    engine = create_async_engine("sqlite+aiosqlite:///./example_library.db", echo=True)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Example 1: Scan a library directory
        print("\n=== Example 1: Scanning Library ===")
        scan_use_case = ScanLibraryUseCase(session)

        # Replace with your actual music library path
        library_path = "/path/to/your/music/library"

        # Check if path exists
        if not Path(library_path).exists():
            print(f"Library path does not exist: {library_path}")
            print("Creating example with tmp directory instead...")
            library_path = "/tmp/example_music"
            Path(library_path).mkdir(exist_ok=True)

        print(f"Scanning library: {library_path}")
        scan = await scan_use_case.execute(library_path)

        print(f"Scan ID: {scan.id}")
        print(f"Status: {scan.status.value}")
        print(f"Total files found: {scan.total_files}")
        print(f"Files scanned: {scan.scanned_files}")
        print(f"Broken files: {scan.broken_files}")
        print(f"Duplicate groups: {scan.duplicate_files}")
        print(f"Progress: {scan.get_progress_percent():.1f}%")

        # Example 2: Get scan status
        print("\n=== Example 2: Getting Scan Status ===")
        scan_status = await scan_use_case.get_scan_status(scan.id)
        if scan_status:
            print(f"Scan status: {scan_status.status.value}")
            print(f"Progress: {scan_status.get_progress_percent():.1f}%")

        # Example 3: Get duplicate files
        print("\n=== Example 3: Finding Duplicates ===")
        duplicates_use_case = GetDuplicatesUseCase(session)
        duplicates = await duplicates_use_case.execute(resolved=False)

        if duplicates:
            print(f"Found {len(duplicates)} duplicate groups:")
            for dup in duplicates[:5]:  # Show first 5
                print(f"\n  Hash: {dup['file_hash'][:16]}...")
                print(f"  Duplicate count: {dup['duplicate_count']}")
                print(f"  Total size: {dup['total_size_bytes'] / 1024 / 1024:.2f} MB")
                print(f"  Files:")
                for track in dup["tracks"]:
                    print(f"    - {track['title']} ({track['file_path']})")
        else:
            print("No duplicates found!")

        # Example 4: Get broken files
        print("\n=== Example 4: Finding Broken Files ===")
        broken_use_case = GetBrokenFilesUseCase(session)
        broken_files = await broken_use_case.execute()

        if broken_files:
            print(f"Found {len(broken_files)} broken files:")
            for broken in broken_files[:5]:  # Show first 5
                print(f"\n  Title: {broken['title']}")
                print(f"  Path: {broken['file_path']}")
                print(f"  Size: {broken['file_size'] / 1024:.1f} KB")
        else:
            print("No broken files found!")

        # Example 5: Using LibraryScannerService directly
        print("\n=== Example 5: Direct Scanner Usage ===")
        scanner = LibraryScannerService(hash_algorithm="sha256")

        # Discover files
        audio_files = scanner.discover_audio_files(Path(library_path))
        print(f"Discovered {len(audio_files)} audio files")

        # Scan a single file (if any exist)
        if audio_files:
            file_info = scanner.scan_file(audio_files[0])
            print(f"\nExample file scan:")
            print(f"  Path: {file_info.path}")
            print(f"  Size: {file_info.size / 1024:.1f} KB")
            print(f"  Hash: {file_info.hash_value[:16]}...")
            print(f"  Valid: {file_info.is_valid}")
            print(f"  Format: {file_info.format}")
            print(f"  Bitrate: {file_info.bitrate}")
            if file_info.title:
                print(f"  Title: {file_info.title}")
            if file_info.artist:
                print(f"  Artist: {file_info.artist}")

    await engine.dispose()
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
