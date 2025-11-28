# Library Artwork Implementation

## Document Information
- **Version**: 1.0
- **Last Updated**: 2025-11-28
- **Status**: Implemented
- **Related**: UI_PATTERNS.md, DATA_MODELS.md

---

## Overview

Die Library-UI zeigt Artist- und Album-Artwork direkt von Spotify CDN URLs. Keine lokale Speicherung für Library-Artwork nötig – das minimiert Speicherverbrauch und vermeidet Duplikate.

---

## Artwork-Quellen

| Entity | DB-Feld | Quelle | Format |
|--------|---------|--------|--------|
| **Artist** | `image_url` | Spotify CDN | ~320x320 JPEG |
| **Album** | `artwork_url` | Spotify CDN | ~300-640px JPEG |
| **Track** | – | Erbt von Album | – |

### Spotify CDN URLs

```
https://i.scdn.co/image/{image_id}
```

- URLs sind stabil und cachebar
- Verschiedene Größen verfügbar (64, 300, 640px)
- Keine Authentication nötig

---

## Fallback-Kette

```
1. Spotify CDN URL (artwork_url / image_url)
        ↓ (nicht vorhanden)
2. Placeholder (Icon oder Buchstaben-Avatar)
        ↓ (SPÄTER: Optional)
3. cover.jpg aus Album-Ordner
        ↓ (SPÄTER: Optional)
4. MusicBrainz / CoverArtArchive
```

**Aktuell implementiert:** Stufe 1 + 2

---

## Datenbank-Schema

### ArtistModel

```python
class ArtistModel(Base):
    __tablename__ = "artists"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # ...
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
```

### AlbumModel

```python
class AlbumModel(Base):
    __tablename__ = "albums"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    # ...
    artwork_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
```

---

## API-Routes

### GET /ui/library/artists

```python
@router.get("/library/artists")
async def library_artists(request: Request) -> Any:
    """Library artists browser page."""
    # SQL-Abfrage mit Aggregation
    stmt = (
        select(ArtistModel, track_count_subq.c.track_count, album_count_subq.c.album_count)
        .outerjoin(track_count_subq, ...)
        .outerjoin(album_count_subq, ...)
    )
    
    # Template-Daten mit image_url
    artists = [
        {
            "name": artist.name,
            "track_count": track_count or 0,
            "album_count": album_count or 0,
            "image_url": artist.image_url,  # Spotify CDN URL
        }
        for artist, track_count, album_count in rows
    ]
```

### GET /ui/library/albums

```python
@router.get("/library/albums")
async def library_albums(request: Request) -> Any:
    """Library albums browser page."""
    # SQL-Abfrage mit Track-Count Subquery
    stmt = (
        select(AlbumModel, track_count_subq.c.track_count)
        .outerjoin(track_count_subq, ...)
        .options(joinedload(AlbumModel.artist))
    )
    
    # Template-Daten mit artwork_url
    albums = [
        {
            "title": album.title,
            "artist": album.artist.name if album.artist else "Unknown Artist",
            "track_count": track_count or 0,
            "year": album.release_year,
            "artwork_url": album.artwork_url,  # Spotify CDN URL
        }
        for album, track_count in rows
    ]
```

---

## Template-Patterns

### Album-Card mit Artwork

```jinja2
<div class="album-cover">
    {% if album.artwork_url %}
    <img src="{{ album.artwork_url }}" alt="{{ album.title }}" loading="lazy">
    {% else %}
    <i class="bi bi-disc"></i>
    {% endif %}
</div>
```

### Artist-Avatar mit Bild

```jinja2
<div class="artist-avatar" {% if not artist.image_url %}style="background: linear-gradient(135deg, #a855f7, #7c3aed);"{% endif %}>
    {% if artist.image_url %}
    <img src="{{ artist.image_url }}" alt="{{ artist.name }}" loading="lazy">
    {% else %}
    {{ artist.name[0]|upper }}
    {% endif %}
</div>
```

---

## CSS-Styles

### Album-Cover Container

```css
.album-cover {
    aspect-ratio: 1;
    background: linear-gradient(135deg, #22c55e, #16a34a);
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

.album-cover img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}
```

### Artist-Avatar Container

```css
.artist-avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

.artist-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}
```

---

## Performance-Optimierungen

### Lazy Loading

Alle Artwork-Bilder nutzen `loading="lazy"`:

```html
<img src="{{ album.artwork_url }}" loading="lazy">
```

### Browser-Caching

Spotify CDN URLs haben lange Cache-TTLs. Browser cacht automatisch.

### SQL-Optimierung

- Direkte Abfrage von `ArtistModel` / `AlbumModel` statt Gruppierung über Tracks
- Subqueries für Counts statt N+1 Queries
- `joinedload()` für Artist-Relationship bei Albums

---

## Betroffene Dateien

| Datei | Änderung |
|-------|----------|
| `src/soulspot/api/routers/ui.py` | Routes refactored, artwork URLs hinzugefügt |
| `src/soulspot/templates/library_artists.html` | Artist-Bild Support |
| `src/soulspot/templates/library_albums.html` | Album-Cover Support |
| `src/soulspot/templates/library_artist_detail.html` | Artist + Album Artwork |
| `src/soulspot/templates/library_album_detail.html` | Album-Cover Support |

---

## Zukünftige Erweiterungen

### cover.jpg Fallback (Planned)

1. Library-Scanner erkennt `cover.jpg` in Album-Ordnern
2. Pfad in `artwork_path` speichern
3. API-Endpoint `/api/artwork/local/{album_id}` liefert Bild
4. Template-Fallback: `artwork_url` → `artwork_path` → Icon

### MusicBrainz Fallback (Planned)

1. Bei fehlendem Artwork → CoverArtArchive API abfragen
2. Ergebnis cachen in `/config/artwork/musicbrainz/`
3. Als dritter Fallback in Templates

---

## Abhängigkeiten

- **Spotify Sync**: Artwork URLs werden beim Playlist-Import gespeichert
- **Keine zusätzlichen Pakete** nötig – nutzt bestehende DB-Felder

---

**Status**: ✅ Implementiert  
**Getestet**: Pending (UI-Test)
