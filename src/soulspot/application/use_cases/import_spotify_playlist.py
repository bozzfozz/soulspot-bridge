"""Import Spotify playlist use case."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from soulspot.application.use_cases import UseCase
from soulspot.domain.entities import Playlist, Track
from soulspot.domain.ports import IPlaylistRepository, ISpotifyClient, ITrackRepository
from soulspot.domain.value_objects import PlaylistId, SpotifyUri, TrackId


@dataclass
class ImportSpotifyPlaylistRequest:
    """Request to import a Spotify playlist."""

    playlist_id: str
    access_token: str
    fetch_all_tracks: bool = True


@dataclass
class ImportSpotifyPlaylistResponse:
    """Response from importing a Spotify playlist."""

    playlist: Playlist
    tracks_imported: int
    tracks_failed: int
    errors: list[str]


class ImportSpotifyPlaylistUseCase(UseCase[ImportSpotifyPlaylistRequest, ImportSpotifyPlaylistResponse]):
    """Use case for importing a Spotify playlist into the system.
    
    This use case:
    1. Fetches playlist metadata from Spotify
    2. Creates or updates the playlist entity
    3. Fetches all tracks in the playlist
    4. Creates or updates track entities
    5. Associates tracks with the playlist
    """

    def __init__(
        self,
        spotify_client: ISpotifyClient,
        playlist_repository: IPlaylistRepository,
        track_repository: ITrackRepository,
    ) -> None:
        """Initialize the use case with required dependencies.
        
        Args:
            spotify_client: Client for Spotify API operations
            playlist_repository: Repository for playlist persistence
            track_repository: Repository for track persistence
        """
        self._spotify_client = spotify_client
        self._playlist_repository = playlist_repository
        self._track_repository = track_repository

    async def execute(self, request: ImportSpotifyPlaylistRequest) -> ImportSpotifyPlaylistResponse:
        """Execute the import playlist use case.
        
        Args:
            request: Request containing playlist ID and access token
            
        Returns:
            Response with imported playlist and statistics
        """
        errors: list[str] = []
        tracks_imported = 0
        tracks_failed = 0

        # 1. Fetch playlist metadata from Spotify
        try:
            spotify_playlist = await self._spotify_client.get_playlist(
                request.playlist_id,
                request.access_token,
            )
        except Exception as e:
            raise ValueError(f"Failed to fetch playlist from Spotify: {e}")

        # 2. Create or update playlist entity
        playlist_id = PlaylistId.generate()
        playlist = Playlist(
            id=playlist_id,
            name=spotify_playlist["name"],
            description=spotify_playlist.get("description"),
            spotify_uri=SpotifyUri(f"spotify:playlist:{request.playlist_id}"),
            owner=spotify_playlist["owner"]["display_name"],
            track_count=spotify_playlist["tracks"]["total"],
            is_public=spotify_playlist["public"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Check if playlist already exists by Spotify URI
        existing_playlist = await self._playlist_repository.get_by_spotify_uri(playlist.spotify_uri)
        if existing_playlist:
            # Update existing playlist
            existing_playlist.name = playlist.name
            existing_playlist.description = playlist.description
            existing_playlist.track_count = playlist.track_count
            existing_playlist.is_public = playlist.is_public
            existing_playlist.updated_at = datetime.utcnow()
            await self._playlist_repository.update(existing_playlist)
            playlist = existing_playlist
        else:
            # Add new playlist
            await self._playlist_repository.add(playlist)

        # 3. Process tracks if requested
        if request.fetch_all_tracks:
            track_items = spotify_playlist["tracks"]["items"]
            
            for item in track_items:
                try:
                    track_data = item.get("track")
                    if not track_data:
                        tracks_failed += 1
                        errors.append("Skipped item with no track data")
                        continue

                    # Create track entity
                    track_id = TrackId.generate()
                    track = Track(
                        id=track_id,
                        title=track_data["name"],
                        artist_names=[artist["name"] for artist in track_data["artists"]],
                        album_name=track_data["album"]["name"],
                        duration_ms=track_data["duration_ms"],
                        spotify_uri=SpotifyUri(track_data["uri"]),
                        isrc=track_data.get("external_ids", {}).get("isrc"),
                        track_number=track_data.get("track_number"),
                        disc_number=track_data.get("disc_number"),
                        release_date=track_data["album"].get("release_date"),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )

                    # Check if track already exists by Spotify URI
                    existing_track = await self._track_repository.get_by_spotify_uri(track.spotify_uri)
                    if existing_track:
                        # Update existing track
                        existing_track.title = track.title
                        existing_track.artist_names = track.artist_names
                        existing_track.album_name = track.album_name
                        existing_track.duration_ms = track.duration_ms
                        existing_track.isrc = track.isrc
                        existing_track.track_number = track.track_number
                        existing_track.disc_number = track.disc_number
                        existing_track.release_date = track.release_date
                        existing_track.updated_at = datetime.utcnow()
                        await self._track_repository.update(existing_track)
                        track = existing_track
                    else:
                        # Add new track
                        await self._track_repository.add(track)

                    # Associate track with playlist
                    await self._playlist_repository.add_track(playlist.id, track.id)
                    tracks_imported += 1

                except Exception as e:
                    tracks_failed += 1
                    errors.append(f"Failed to import track: {e}")

        return ImportSpotifyPlaylistResponse(
            playlist=playlist,
            tracks_imported=tracks_imported,
            tracks_failed=tracks_failed,
            errors=errors,
        )
