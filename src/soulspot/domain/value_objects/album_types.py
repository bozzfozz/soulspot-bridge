"""Album type enums for the domain layer (Lidarr-style dual type system).

Hey future me - this is based on how Lidarr/MusicBrainz model album types!

The KEY INSIGHT is that albums have TWO type dimensions:
1. PRIMARY TYPE: The main category (album, EP, single, etc.)
2. SECONDARY TYPES: Modifiers/attributes (compilation, live, soundtrack, etc.)

Why dual types? Because a live album can ALSO be a compilation! These are orthogonal
concepts. MusicBrainz, Spotify, and Lidarr all use this model.

Example combinations:
- "Thriller" by Michael Jackson: primary=album, secondary=[]
- "Unplugged in New York" by Nirvana: primary=album, secondary=[live]
- "Now That's What I Call Music 2024": primary=album, secondary=[compilation]
- "Pulp Fiction Soundtrack": primary=album, secondary=[soundtrack]
- "The Beatles Live at Hollywood Bowl": primary=album, secondary=[live, compilation]

Usage:
    from soulspot.domain.value_objects.album_types import PrimaryAlbumType, SecondaryAlbumType
    
    album.primary_type = PrimaryAlbumType.ALBUM
    album.secondary_types = [SecondaryAlbumType.COMPILATION, SecondaryAlbumType.LIVE]
    
    if SecondaryAlbumType.COMPILATION in album.secondary_types:
        # Show track-level artists in UI
"""

from enum import Enum
from typing import List


class PrimaryAlbumType(str, Enum):
    """Primary album type - the main category of the release.
    
    These are mutually exclusive - an album can only have ONE primary type.
    Default is ALBUM if not specified.
    
    Values match MusicBrainz/Lidarr conventions for interoperability.
    """
    
    ALBUM = "album"
    """Standard full-length album (default)."""
    
    EP = "ep"
    """Extended Play - typically 4-6 tracks, longer than single but shorter than album."""
    
    SINGLE = "single"
    """Single release - typically 1-3 tracks."""
    
    BROADCAST = "broadcast"
    """Radio broadcast recording."""
    
    OTHER = "other"
    """Anything that doesn't fit other categories."""
    
    @classmethod
    def from_string(cls, value: str) -> "PrimaryAlbumType":
        """Parse string to enum, defaulting to ALBUM if unknown.
        
        Args:
            value: String like "album", "ep", "EP", etc.
            
        Returns:
            Corresponding enum value, or ALBUM if not recognized.
        """
        if not value:
            return cls.ALBUM
            
        normalized = value.lower().strip()
        
        # Try direct match first
        try:
            return cls(normalized)
        except ValueError:
            pass
        
        # Handle common variations
        mappings = {
            "lp": cls.ALBUM,
            "full-length": cls.ALBUM,
            "studio": cls.ALBUM,
            "mini-album": cls.EP,
            "maxi-single": cls.SINGLE,
            "7\"": cls.SINGLE,
            "12\"": cls.SINGLE,
        }
        
        return mappings.get(normalized, cls.ALBUM)
    
    def __str__(self) -> str:
        return self.value


class SecondaryAlbumType(str, Enum):
    """Secondary album type - modifiers that can be combined.
    
    An album can have MULTIPLE secondary types (e.g., live + compilation).
    These modify the primary type but don't replace it.
    
    Values match MusicBrainz/Lidarr conventions.
    """
    
    COMPILATION = "compilation"
    """Various artists compilation or best-of collection."""
    
    SOUNDTRACK = "soundtrack"
    """Film, TV, or video game soundtrack."""
    
    LIVE = "live"
    """Live recording from a concert/performance."""
    
    REMIX = "remix"
    """Album consisting primarily of remixes."""
    
    DJ_MIX = "dj-mix"
    """Continuous DJ mix of multiple tracks."""
    
    MIXTAPE = "mixtape"
    """Mixtape/street album (often hip-hop)."""
    
    DEMO = "demo"
    """Demo recordings, usually unreleased or limited release."""
    
    SPOKENWORD = "spokenword"
    """Audiobook, podcast, or spoken word content."""
    
    INTERVIEW = "interview"
    """Interview recording."""
    
    AUDIOBOOK = "audiobook"
    """Audiobook (subset of spokenword)."""
    
    @classmethod
    def from_string(cls, value: str) -> "SecondaryAlbumType | None":
        """Parse string to enum, returning None if unknown.
        
        Args:
            value: String like "compilation", "live", etc.
            
        Returns:
            Corresponding enum value, or None if not recognized.
        """
        if not value:
            return None
            
        normalized = value.lower().strip()
        
        # Try direct match first
        try:
            return cls(normalized)
        except ValueError:
            pass
        
        # Handle variations
        mappings = {
            "dj mix": cls.DJ_MIX,
            "djmix": cls.DJ_MIX,
            "mixtape/street": cls.MIXTAPE,
            "street": cls.MIXTAPE,
            "audio drama": cls.SPOKENWORD,
            "audiodrama": cls.SPOKENWORD,
            "spoken word": cls.SPOKENWORD,
        }
        
        return mappings.get(normalized)
    
    @classmethod
    def from_string_list(cls, values: List[str]) -> List["SecondaryAlbumType"]:
        """Parse list of strings to list of enums, filtering unknown values.
        
        Args:
            values: List of strings like ["compilation", "live"]
            
        Returns:
            List of valid enum values (unknown strings are filtered out).
        """
        result = []
        for v in values:
            parsed = cls.from_string(v)
            if parsed is not None:
                result.append(parsed)
        return result
    
    def __str__(self) -> str:
        return self.value


# Hey future me - these are the known "Various Artists" patterns for compilation detection!
# When scanning library, if album_artist matches any of these (case-insensitive), we know
# it's a compilation. Add more patterns as needed. The patterns are in priority order -
# "Various Artists" is most common, "VA" is abbreviated version common in file tags.
VARIOUS_ARTISTS_PATTERNS = [
    "various artists",
    "various",
    "va",
    "v.a.",
    "v. a.",
    "v/a",
    "diverse",          # German
    "varios artistas",  # Spanish
    "artistes divers",  # French
    "vari",             # Italian
    "sampler",
    "compilation",
]


def is_various_artists(artist_name: str | None) -> bool:
    """Check if an artist name indicates "Various Artists" (compilation).
    
    Args:
        artist_name: The artist name to check.
        
    Returns:
        True if the name matches a Various Artists pattern.
        
    Example:
        >>> is_various_artists("Various Artists")
        True
        >>> is_various_artists("VA")
        True
        >>> is_various_artists("The Beatles")
        False
    """
    if not artist_name:
        return False
    
    normalized = artist_name.lower().strip()
    
    # Exact match check
    if normalized in VARIOUS_ARTISTS_PATTERNS:
        return True
    
    # Partial match for patterns like "Various Artists (2024)"
    for pattern in VARIOUS_ARTISTS_PATTERNS[:3]:  # Only check common ones for partial
        if normalized.startswith(pattern):
            return True
    
    return False


def detect_compilation_from_track_artists(
    album_artist: str | None,
    track_artists: List[str],
    threshold: int = 3
) -> bool:
    """Detect if an album is a compilation based on track artist diversity.
    
    Args:
        album_artist: The album-level artist (from TPE2 tag or similar).
        track_artists: List of track-level artists from the album.
        threshold: Minimum number of unique artists to consider compilation.
        
    Returns:
        True if the album appears to be a compilation.
        
    Rules:
        1. album_artist is a Various Artists pattern → True
        2. More than `threshold` unique track artists → True
        3. Otherwise → False
    """
    # Rule 1: Check album artist
    if is_various_artists(album_artist):
        return True
    
    # Rule 2: Check track artist diversity
    if not track_artists:
        return False
    
    # Normalize and dedupe track artists
    unique_artists = set(a.lower().strip() for a in track_artists if a)
    
    # If album_artist exists and differs from most tracks, might be compilation
    if album_artist and len(unique_artists) > threshold:
        return True
    
    return False
