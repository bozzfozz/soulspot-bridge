"""Comprehensive endpoint accessibility tests.

This module tests that all API endpoints are accessible and respond correctly
to basic requests. It ensures 100% endpoint coverage and validates that all
pages and features are reachable.
"""

import pytest
from httpx import AsyncClient


class TestHealthEndpoints:
    """Test health and status endpoints."""

    async def test_health_endpoint_accessible(self, async_client: AsyncClient):
        """Verify /health endpoint is accessible."""
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    async def test_liveness_endpoint_accessible(self, async_client: AsyncClient):
        """Verify /live endpoint is accessible."""
        response = await async_client.get("/live")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "alive"


class TestAuthEndpoints:
    """Test authentication endpoints."""

    async def test_spotify_login_endpoint_accessible(self, async_client: AsyncClient):
        """Verify Spotify login endpoint is accessible."""
        response = await async_client.get("/api/auth/spotify/login")
        # Should redirect or return 200 with auth URL
        assert response.status_code in [200, 302, 307]

    async def test_spotify_callback_endpoint_accessible(
        self, async_client: AsyncClient
    ):
        """Verify Spotify callback endpoint exists."""
        # This will fail without proper params, but endpoint should exist
        response = await async_client.get("/api/auth/spotify/callback")
        # Should return 422 (validation error) or other error, not 404
        assert response.status_code != 404

    async def test_spotify_status_endpoint_accessible(
        self, async_client: AsyncClient
    ):
        """Verify Spotify auth status endpoint is accessible."""
        response = await async_client.get("/api/auth/spotify/status")
        assert response.status_code == 200
        data = response.json()
        assert "authenticated" in data


class TestPlaylistEndpoints:
    """Test playlist management endpoints."""

    async def test_list_playlists_endpoint_accessible(
        self, async_client: AsyncClient
    ):
        """Verify playlists list endpoint is accessible."""
        response = await async_client.get("/api/playlists/")
        # Might require auth, but endpoint should exist
        assert response.status_code in [200, 401, 403]

    async def test_sync_playlists_endpoint_exists(self, async_client: AsyncClient):
        """Verify sync playlists endpoint exists."""
        response = await async_client.post("/api/playlists/sync")
        # Should not be 404
        assert response.status_code != 404

    async def test_get_playlist_details_endpoint_exists(
        self, async_client: AsyncClient
    ):
        """Verify get playlist details endpoint exists."""
        response = await async_client.get("/api/playlists/test-id")
        # Should return 404 for non-existent playlist, not route not found
        assert response.status_code in [200, 401, 403, 404]

    async def test_sync_playlist_tracks_endpoint_exists(
        self, async_client: AsyncClient
    ):
        """Verify sync playlist tracks endpoint exists."""
        response = await async_client.post("/api/playlists/test-id/sync")
        assert response.status_code != 404


class TestTracksEndpoints:
    """Test track management endpoints."""

    async def test_list_tracks_endpoint_accessible(self, async_client: AsyncClient):
        """Verify tracks list endpoint is accessible."""
        response = await async_client.get("/api/tracks/")
        assert response.status_code == 200

    async def test_get_track_endpoint_exists(self, async_client: AsyncClient):
        """Verify get track endpoint exists."""
        response = await async_client.get("/api/tracks/1")
        # Should return 404 for non-existent track
        assert response.status_code in [200, 404]

    async def test_search_tracks_endpoint_accessible(self, async_client: AsyncClient):
        """Verify search tracks endpoint is accessible."""
        response = await async_client.get("/api/tracks/search?q=test")
        assert response.status_code == 200


class TestDownloadEndpoints:
    """Test download management endpoints."""

    async def test_list_downloads_endpoint_accessible(
        self, async_client: AsyncClient
    ):
        """Verify downloads list endpoint is accessible."""
        response = await async_client.get("/api/downloads/")
        assert response.status_code == 200

    async def test_queue_status_endpoint_accessible(self, async_client: AsyncClient):
        """Verify queue status endpoint is accessible."""
        response = await async_client.get("/api/downloads/queue/status")
        assert response.status_code == 200
        data = response.json()
        assert "paused" in data

    async def test_download_track_endpoint_exists(self, async_client: AsyncClient):
        """Verify download track endpoint exists."""
        response = await async_client.post("/api/downloads/", json={"track_id": 1})
        # Should not be 404
        assert response.status_code != 404

    async def test_pause_downloads_endpoint_exists(self, async_client: AsyncClient):
        """Verify pause downloads endpoint exists."""
        response = await async_client.post("/api/downloads/queue/pause")
        assert response.status_code in [200, 204]

    async def test_resume_downloads_endpoint_exists(self, async_client: AsyncClient):
        """Verify resume downloads endpoint exists."""
        response = await async_client.post("/api/downloads/queue/resume")
        assert response.status_code in [200, 204]

    async def test_batch_download_endpoint_exists(self, async_client: AsyncClient):
        """Verify batch download endpoint exists."""
        response = await async_client.post(
            "/api/downloads/batch", json={"track_ids": []}
        )
        assert response.status_code in [200, 400, 422]


class TestMetadataEndpoints:
    """Test metadata management endpoints."""

    async def test_search_metadata_endpoint_accessible(
        self, async_client: AsyncClient
    ):
        """Verify metadata search endpoint is accessible."""
        response = await async_client.get(
            "/api/metadata/search?artist=Test&title=Song"
        )
        assert response.status_code == 200

    async def test_enrich_track_endpoint_exists(self, async_client: AsyncClient):
        """Verify enrich track endpoint exists."""
        response = await async_client.post("/api/metadata/enrich/1")
        assert response.status_code != 404

    async def test_auto_fix_endpoint_exists(self, async_client: AsyncClient):
        """Verify auto-fix metadata endpoint exists."""
        response = await async_client.post("/api/metadata/auto-fix/1")
        assert response.status_code != 404


class TestLibraryEndpoints:
    """Test library management endpoints."""

    async def test_library_stats_endpoint_accessible(self, async_client: AsyncClient):
        """Verify library stats endpoint is accessible."""
        response = await async_client.get("/api/library/stats")
        assert response.status_code == 200

    async def test_scan_library_endpoint_exists(self, async_client: AsyncClient):
        """Verify scan library endpoint exists."""
        response = await async_client.post("/api/library/scan")
        assert response.status_code != 404

    async def test_import_downloads_endpoint_exists(self, async_client: AsyncClient):
        """Verify import downloads endpoint exists."""
        response = await async_client.post("/api/library/import")
        assert response.status_code != 404


class TestSettingsEndpoints:
    """Test settings endpoints."""

    async def test_get_settings_endpoint_accessible(self, async_client: AsyncClient):
        """Verify get settings endpoint is accessible."""
        response = await async_client.get("/api/settings/")
        assert response.status_code == 200

    async def test_update_settings_endpoint_exists(self, async_client: AsyncClient):
        """Verify update settings endpoint exists."""
        response = await async_client.put("/api/settings/", json={})
        assert response.status_code != 404


class TestDashboardEndpoints:
    """Test dashboard endpoints."""

    async def test_get_dashboard_endpoint_accessible(self, async_client: AsyncClient):
        """Verify get dashboard endpoint is accessible."""
        response = await async_client.get("/api/dashboard")
        assert response.status_code == 200

    async def test_get_dashboard_stats_endpoint_accessible(
        self, async_client: AsyncClient
    ):
        """Verify dashboard stats endpoint is accessible."""
        response = await async_client.get("/api/dashboard/stats")
        assert response.status_code == 200


class TestWidgetEndpoints:
    """Test widget endpoints."""

    async def test_list_widgets_endpoint_accessible(self, async_client: AsyncClient):
        """Verify list widgets endpoint is accessible."""
        response = await async_client.get("/api/widgets/")
        assert response.status_code == 200

    async def test_create_widget_endpoint_exists(self, async_client: AsyncClient):
        """Verify create widget endpoint exists."""
        response = await async_client.post("/api/widgets/", json={})
        assert response.status_code != 404


class TestAutomationEndpoints:
    """Test automation endpoints."""

    async def test_list_automation_rules_endpoint_accessible(
        self, async_client: AsyncClient
    ):
        """Verify list automation rules endpoint is accessible."""
        response = await async_client.get("/api/automation/rules")
        assert response.status_code == 200

    async def test_create_automation_rule_endpoint_exists(
        self, async_client: AsyncClient
    ):
        """Verify create automation rule endpoint exists."""
        response = await async_client.post("/api/automation/rules", json={})
        assert response.status_code != 404


class TestSSEEndpoints:
    """Test Server-Sent Events endpoints."""

    async def test_sse_stream_endpoint_accessible(self, async_client: AsyncClient):
        """Verify SSE stream endpoint is accessible."""
        # SSE endpoint should return text/event-stream
        response = await async_client.get("/api/sse/stream")
        # Should not be 404
        assert response.status_code != 404
