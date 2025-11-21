"""Token management service for OAuth tokens."""

import logging
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import httpx

from soulspot.domain.ports import ISpotifyClient

logger = logging.getLogger(__name__)


@dataclass
class TokenInfo:
    """Information about an OAuth token."""

    access_token: str
    refresh_token: str | None
    expires_at: datetime
    token_type: str = "Bearer"
    scope: str | None = None

    # Hey future me, this is a simple expiry check - is NOW >= expires_at? Returns True if expired.
    # Important: we compare using UTC everywhere to avoid timezone headaches! Don't mix timezone-aware
    # and timezone-naive datetimes or you'll get weird comparison errors. If expires_at is None (shouldn't
    # happen but defensive), this will crash - but that's a bug we want to know about!
    def is_expired(self) -> bool:
        """Check if the token is expired."""
        return datetime.now(UTC) >= self.expires_at

    # Yo, this is for PROACTIVE refresh - don't wait until token is expired, refresh it BEFORE! Default
    # threshold is 5 minutes (300s). So if token expires at 3:00pm and it's 2:56pm, this returns True.
    # Why? Network delays, clock drift, processing time - better to refresh early than get 401 errors
    # mid-request! You can tune threshold per use case - background jobs might use longer (10 min),
    # user-facing API calls might use shorter (1 min).
    def expires_soon(self, threshold_seconds: int = 300) -> bool:
        """Check if token expires within threshold.

        Args:
            threshold_seconds: Time threshold in seconds (default 5 minutes)

        Returns:
            True if token expires within threshold
        """
        return datetime.now(UTC) >= (
            self.expires_at - timedelta(seconds=threshold_seconds)
        )


class TokenManager:
    """Service for managing OAuth tokens with automatic refresh.

    This service:
    1. Stores OAuth tokens (access and refresh tokens)
    2. Checks token expiration
    3. Automatically refreshes expired tokens
    4. Generates OAuth PKCE parameters
    5. Handles authorization flow
    """

    # Listen up future me, this TokenManager is ALSO in-memory storage (dict)! Same problems as SessionStore -
    # server restart loses all tokens, no sharing across app instances. The _tokens dict is keyed by user_id
    # (which is... what exactly? Session ID? Spotify user ID? Be careful!). In production, move to Redis
    # or encrypted DB storage. Tokens are SECRETS - if someone steals them, they can access Spotify as that user!
    def __init__(self, spotify_client: ISpotifyClient) -> None:
        """Initialize token manager.

        Args:
            spotify_client: Spotify client for token operations
        """
        self._spotify_client = spotify_client
        self._tokens: dict[str, TokenInfo] = {}

    # Hey, this generates the OAuth "state" parameter for CSRF protection. It's a random 32-byte string
    # (urlsafe encoding). We send this to Spotify, they return it in callback, we verify it matches.
    # If it doesn't match, someone is trying to replay an old auth code! Use secrets module NOT random -
    # secrets is cryptographically secure, random is predictable and DANGEROUS for security tokens!
    def generate_auth_state(self) -> str:
        """Generate a random state parameter for OAuth.

        Returns:
            Random state string for CSRF protection
        """
        return secrets.token_urlsafe(32)

    # Yo, this is the FIRST step of OAuth PKCE flow - generate auth URL with state and code_verifier.
    # If state is None, we auto-generate one (convenient for callers). The code_verifier is generated
    # HERE but must be stored somewhere (session, DB) because we need it later to exchange the code!
    # Don't lose the code_verifier or OAuth flow fails! Returns all three (URL, state, verifier) so
    # caller can store state+verifier before redirecting user.
    async def get_authorization_url(
        self, state: str | None = None
    ) -> tuple[str, str, str]:
        """Get Spotify authorization URL for OAuth PKCE flow.

        Args:
            state: Optional state parameter, generated if not provided

        Returns:
            Tuple of (authorization URL, state, code verifier)
        """
        if not state:
            state = self.generate_auth_state()

        # Generate PKCE code verifier
        from soulspot.infrastructure.integrations.spotify_client import SpotifyClient

        code_verifier = SpotifyClient.generate_code_verifier()

        # Get authorization URL
        auth_url = await self._spotify_client.get_authorization_url(
            state, code_verifier
        )

        return auth_url, state, code_verifier

    # Listen future me, this is the OAuth callback handler - we got an auth code from Spotify, now exchange
    # it for access+refresh tokens. The code_verifier MUST be the same one used in get_authorization_url!
    # Spotify verifies the PKCE challenge - if verifier doesn't match, you get 400 error. The user_id is
    # OPTIONAL - if provided, we auto-store the token in our dict. If not, caller must store it manually.
    # expires_in from Spotify is usually 3600 (1 hour). We calculate absolute expires_at timestamp.
    async def exchange_authorization_code(
        self,
        code: str,
        code_verifier: str,
        user_id: str | None = None,
    ) -> TokenInfo:
        """Exchange authorization code for access token.

        Args:
            code: Authorization code from callback
            code_verifier: PKCE code verifier used in authorization
            user_id: Optional user ID to associate token with

        Returns:
            TokenInfo with access and refresh tokens
        """
        # Exchange code for tokens
        token_response = await self._spotify_client.exchange_code(code, code_verifier)

        # Calculate expiration time
        expires_in = token_response.get("expires_in", 3600)
        expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)

        # Create TokenInfo
        token_info = TokenInfo(
            access_token=token_response["access_token"],
            refresh_token=token_response.get("refresh_token"),
            expires_at=expires_at,
            token_type=token_response.get("token_type", "Bearer"),
            scope=token_response.get("scope"),
        )

        # Store token if user_id provided
        if user_id:
            self._tokens[user_id] = token_info

        return token_info

    # Hey, this is your "give me a valid token" helper - handles ALL the refresh logic automatically!
    # If token doesn't exist, returns None. If token exists but is expired/expiring-soon, tries to refresh
    # it using refresh_token. If refresh fails (network error, invalid refresh token, etc), logs warning
    # and returns None. This means callers get None for BOTH "no token" and "refresh failed" - they can't
    # distinguish! The expires_soon() check (5 min threshold) means we proactively refresh before expiry.
    async def get_valid_token(self, user_id: str) -> str | None:
        """Get a valid access token, refreshing if necessary.

        Args:
            user_id: User ID associated with the token

        Returns:
            Valid access token or None if not available
        """
        token_info = self._tokens.get(user_id)
        if not token_info:
            return None

        # Refresh if expired or expiring soon
        if token_info.expires_soon():
            if token_info.refresh_token:
                try:
                    await self.refresh_token(user_id)
                    refreshed_token = self._tokens.get(user_id)
                    if refreshed_token:
                        return refreshed_token.access_token
                    return None
                except (httpx.HTTPError, ValueError) as e:
                    # If refresh fails, token might be invalid
                    logger.warning(
                        "Failed to refresh token for user %s: %s",
                        user_id,
                        e,
                        exc_info=True,
                    )
                    return None
            else:
                # No refresh token available
                return None

        return token_info.access_token

    # Yo, this is the low-level refresh operation - call Spotify's token endpoint with refresh_token,
    # get new access_token (and maybe new refresh_token). If no token found or no refresh_token, raises
    # ValueError. The new refresh_token from Spotify is OPTIONAL - if they don't provide one, we keep
    # using the old one (important!). We preserve scope if Spotify doesn't return it. Updates the stored
    # token in _tokens dict. This can fail with httpx errors if Spotify is down or refresh_token is invalid.
    async def refresh_token(self, user_id: str) -> TokenInfo:
        """Refresh an expired access token.

        Args:
            user_id: User ID associated with the token

        Returns:
            New TokenInfo with refreshed access token

        Raises:
            ValueError: If no token found for user or no refresh token available
        """
        token_info = self._tokens.get(user_id)
        if not token_info:
            raise ValueError(f"No token found for user: {user_id}")

        if not token_info.refresh_token:
            raise ValueError(f"No refresh token available for user: {user_id}")

        # Refresh the token
        token_response = await self._spotify_client.refresh_token(
            token_info.refresh_token
        )

        # Calculate new expiration time
        expires_in = token_response.get("expires_in", 3600)
        expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)

        # Update token info
        new_token_info = TokenInfo(
            access_token=token_response["access_token"],
            refresh_token=token_response.get("refresh_token", token_info.refresh_token),
            expires_at=expires_at,
            token_type=token_response.get("token_type", "Bearer"),
            scope=token_response.get("scope", token_info.scope),
        )

        # Store updated token
        self._tokens[user_id] = new_token_info

        return new_token_info

    # Hey, this is a simple setter - store token for user_id. Overwrites existing token if any. Use this
    # after manual token acquisition or when migrating tokens from another storage. No validation here -
    # we trust the caller to provide valid TokenInfo! Could store expired tokens, None tokens, etc.
    def store_token(self, user_id: str, token_info: TokenInfo) -> None:
        """Store token information for a user.

        Args:
            user_id: User ID to associate token with
            token_info: Token information to store
        """
        self._tokens[user_id] = token_info

    # Yo, simple getter - returns TokenInfo for user or None if not found. The returned TokenInfo might
    # be expired! Caller should check is_expired() or use get_valid_token() instead if they need a fresh
    # token. This is for inspection/debugging more than actual use.
    def get_token_info(self, user_id: str) -> TokenInfo | None:
        """Get token information for a user.

        Args:
            user_id: User ID

        Returns:
            TokenInfo if available, None otherwise
        """
        return self._tokens.get(user_id)

    # Listen, revoke means DELETE - the token is removed from our storage. We don't actually call Spotify's
    # token revocation endpoint! The token is still valid on Spotify's side, we just forget about it locally.
    # If you want true revocation (invalidate token at Spotify), you need to add that API call! Returns
    # True if deleted, False if user_id not found (idempotent).
    def revoke_token(self, user_id: str) -> bool:
        """Revoke (delete) token for a user.

        Args:
            user_id: User ID

        Returns:
            True if token was revoked, False if no token found
        """
        if user_id in self._tokens:
            del self._tokens[user_id]
            return True
        return False

    # Hey, this is for admin/debugging - list all user_ids that have tokens stored. Useful for cleanup,
    # monitoring, or finding orphaned tokens. The list could be HUGE if you have thousands of users!
    # Consider pagination if this grows large. Returns list of dict keys - order is not guaranteed.
    def list_user_ids(self) -> list[str]:
        """List all user IDs with stored tokens.

        Returns:
            List of user IDs
        """
        return list(self._tokens.keys())
