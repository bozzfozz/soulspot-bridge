# Spotify Auto-Sync

> **Version:** 1.1  
> **Last Updated:** 2025-11-28

---

## Übersicht

Das Spotify Auto-Sync Feature synchronisiert automatisch Daten von deinem Spotify-Konto in die lokale SoulSpot-Datenbank. Nach der Synchronisation arbeitet SoulSpot unabhängig von Spotify mit den lokalen Daten.

### Hauptfunktionen

- 🎤 **Followed Artists** - Synchronisiert Künstler, denen du auf Spotify folgst
- 📋 **Playlists** - Synchronisiert deine Spotify-Playlists
- ❤️ **Liked Songs** - Synchronisiert deine "Gefällt mir"-Songs
- 💿 **Saved Albums** - Synchronisiert gespeicherte Alben
- 🖼️ **Lokale Bilderspeicherung** - Lädt Künstler-, Album- und Playlist-Cover herunter
- ⚙️ **Background Worker** - Automatischer Sync ohne manuelles Eingreifen

---

## Architektur

```
┌─────────────────────────────────────────────────────────────────┐
│                      Settings UI (settings.html)                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │  Master  │ │  Sync    │ │ Interval │ │   Image Stats    │   │
│  │  Toggle  │ │ Toggles  │ │ Settings │ │   Disk Usage     │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Settings API (settings.py)                    │
│  GET/PUT /spotify-sync  │  POST /trigger/{type}  │  GET /disk  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Services Layer                            │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │ AppSettings     │ │ SpotifySync     │ │ SpotifyImage    │   │
│  │ Service         │ │ Service         │ │ Service         │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Infrastructure Layer                         │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │ SpotifyClient   │ │ SpotifyBrowse   │ │ Token           │   │
│  │ (Spotify API)   │ │ Repository      │ │ Manager         │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Data Storage                               │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │ app_settings    │ │ spotify_*       │ │ artwork/spotify │   │
│  │ (DB Table)      │ │ (DB Tables)     │ │ (File System)   │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Sync-Typen

### Followed Artists

Synchronisiert alle Künstler, denen du auf Spotify folgst.

| Feld | Beschreibung |
|------|--------------|
| `spotify_id` | Eindeutige Spotify-ID |
| `name` | Künstlername |
| `genres` | Genres des Künstlers |
| `popularity` | Spotify-Popularitätswert (0-100) |
| `image_url` | URL zum Spotify-Bild |
| `image_path` | Lokaler Pfad zum WebP-Bild |
| `follower_count` | Anzahl Follower auf Spotify |

**Default Cooldown:** 5 Minuten

### Playlists

Synchronisiert alle deine Spotify-Playlists (erstellt und gefolgt).

| Feld | Beschreibung |
|------|--------------|
| `spotify_playlist_id` | Eindeutige Spotify-Playlist-ID |
| `name` | Playlist-Name |
| `description` | Playlist-Beschreibung |
| `owner_id` | Spotify-ID des Erstellers |
| `track_count` | Anzahl Tracks |
| `cover_url` | URL zum Playlist-Cover |
| `cover_path` | Lokaler Pfad zum WebP-Cover |
| `is_public` | Öffentlich oder privat |
| `is_collaborative` | Kollaborative Playlist |

**Default Cooldown:** 10 Minuten

### Liked Songs

Synchronisiert deine "Gefällt mir"-Songs als spezielle Playlist.

| Eigenschaft | Wert |
|-------------|------|
| `is_liked_songs` | `true` |
| `name` | "Liked Songs" |
| `owner_id` | Deine Spotify-User-ID |

**Besonderheit:** Liked Songs werden als Playlist mit `is_liked_songs=true` gespeichert.

### Saved Albums

Synchronisiert Alben, die du in deiner Spotify-Bibliothek gespeichert hast.

| Feld | Beschreibung |
|------|--------------|
| `is_saved` | `true` wenn in Bibliothek gespeichert |
| `saved_at` | Zeitpunkt des Speicherns |

---

## Bilderspeicherung

### Format & Größen

| Typ | Format | Größe | Pfad |
|-----|--------|-------|------|
| Künstler | WebP | 300x300px | `artwork/spotify/artists/{spotify_id}.webp` |
| Alben | WebP | 500x500px | `artwork/spotify/albums/{spotify_id}.webp` |
| Playlists | WebP | 300x300px | `artwork/spotify/playlists/{spotify_id}.webp` |

### Warum WebP?

- **~30% kleiner** als JPEG bei gleicher Qualität
- **Transparenz** wird unterstützt
- **Breite Browser-Unterstützung**

### Disk Usage

Die Settings-UI zeigt Statistiken zur Speichernutzung:

```
┌────────────────────────────────────────────────────────┐
│  🎤 Artists    │  💿 Albums     │  📋 Playlists  │ 📊 Total │
│  42 images     │  156 covers    │  12 covers     │ 210      │
│  1.2 MB        │  8.4 MB        │  0.3 MB        │ 9.9 MB   │
└────────────────────────────────────────────────────────┘
```

---

## Einstellungen

### Runtime Settings (DB-gespeichert)

Diese Einstellungen werden in der `app_settings` Tabelle gespeichert und können ohne Neustart geändert werden.

| Setting | Typ | Default | Beschreibung |
|---------|-----|---------|--------------|
| `auto_sync_enabled` | boolean | `true` | Master-Toggle für Auto-Sync |
| `auto_sync_artists` | boolean | `true` | Künstler-Sync aktivieren |
| `auto_sync_playlists` | boolean | `true` | Playlist-Sync aktivieren |
| `auto_sync_liked_songs` | boolean | `true` | Liked Songs-Sync aktivieren |
| `auto_sync_saved_albums` | boolean | `true` | Saved Albums-Sync aktivieren |
| `artists_sync_interval_minutes` | int | `5` | Cooldown zwischen Artist-Syncs |
| `playlists_sync_interval_minutes` | int | `10` | Cooldown zwischen Playlist-Syncs |
| `download_images` | boolean | `true` | Bilder lokal speichern |
| `remove_unfollowed_artists` | boolean | `true` | Entfolgte Künstler entfernen |
| `remove_unfollowed_playlists` | boolean | `false` | Gelöschte Playlists entfernen |

### Setting Keys (DB)

Die Settings werden mit folgenden Keys in der `app_settings` Tabelle gespeichert:

```
spotify.auto_sync_enabled
spotify.auto_sync_artists
spotify.auto_sync_playlists
spotify.auto_sync_liked_songs
spotify.auto_sync_saved_albums
spotify.artists_sync_interval_minutes
spotify.playlists_sync_interval_minutes
spotify.download_images
spotify.remove_unfollowed_artists
spotify.remove_unfollowed_playlists
```

---

## API-Endpunkte

### GET `/api/settings/spotify-sync`

Ruft alle Spotify-Sync-Einstellungen ab.

**Response:**
```json
{
  "settings": {
    "auto_sync_enabled": true,
    "auto_sync_artists": true,
    "auto_sync_playlists": true,
    "auto_sync_liked_songs": true,
    "auto_sync_saved_albums": true,
    "artists_sync_interval_minutes": 5,
    "playlists_sync_interval_minutes": 10,
    "download_images": true,
    "remove_unfollowed_artists": true,
    "remove_unfollowed_playlists": false
  },
  "image_stats": {
    "artists_bytes": 1258291,
    "albums_bytes": 8847200,
    "playlists_bytes": 314572,
    "total_bytes": 10420063,
    "artists_count": 42,
    "albums_count": 156,
    "playlists_count": 12,
    "total_count": 210
  }
}
```

### PUT `/api/settings/spotify-sync`

Aktualisiert Spotify-Sync-Einstellungen.

**Request:**
```json
{
  "auto_sync_enabled": true,
  "auto_sync_artists": true,
  "auto_sync_playlists": true,
  "auto_sync_liked_songs": false,
  "auto_sync_saved_albums": true,
  "artists_sync_interval_minutes": 10,
  "playlists_sync_interval_minutes": 15,
  "download_images": true,
  "remove_unfollowed_artists": true,
  "remove_unfollowed_playlists": false
}
```

**Response:** Gleiche Struktur wie Request (bestätigte Settings)

### POST `/api/settings/spotify-sync/toggle/{setting_name}`

Toggled ein einzelnes Boolean-Setting.

**URL-Parameter:**
- `setting_name`: Name des Settings (ohne `spotify.` Prefix)

**Gültige Werte:**
- `auto_sync_enabled`
- `auto_sync_artists`
- `auto_sync_playlists`
- `auto_sync_liked_songs`
- `auto_sync_saved_albums`
- `download_images`
- `remove_unfollowed_artists`
- `remove_unfollowed_playlists`

**Response:**
```json
{
  "setting": "auto_sync_artists",
  "old_value": true,
  "new_value": false
}
```

### GET `/api/settings/spotify-sync/disk-usage`

Ruft Speicherstatistiken für Spotify-Bilder ab.

**Response:**
```json
{
  "artists_bytes": 1258291,
  "albums_bytes": 8847200,
  "playlists_bytes": 314572,
  "total_bytes": 10420063,
  "artists_count": 42,
  "albums_count": 156,
  "playlists_count": 12,
  "total_count": 210
}
```

### POST `/api/settings/spotify-sync/trigger/{sync_type}`

Triggert einen manuellen Sync.

**URL-Parameter:**
- `sync_type`: Art des Syncs

**Gültige Werte:**
| Wert | Beschreibung |
|------|--------------|
| `artists` | Nur Followed Artists synken |
| `playlists` | Nur Playlists synken |
| `liked` | Nur Liked Songs synken |
| `albums` | Nur Saved Albums synken |
| `all` | Alle Sync-Typen ausführen |

**Response:**
```json
{
  "success": true,
  "message": "Artists synced: 42 updated, 3 removed",
  "sync_type": "artists"
}
```

**Fehler:**
```json
{
  "detail": "Not authenticated with Spotify. Please connect your account first."
}
```

---

## UI-Komponenten

### Spotify Sync Tab

Der neue Tab in den Settings zeigt:

1. **Master Toggle** - Aktiviert/deaktiviert den gesamten Auto-Sync
2. **Sync-Typ Toggles** - Individuelle Toggles für jeden Sync-Typ
3. **Interval Settings** - Cooldown-Zeiten in Minuten
4. **Image Storage Toggle** - Aktiviert/deaktiviert lokale Bilderspeicherung
5. **Disk Usage Stats** - Zeigt Anzahl und Größe der gespeicherten Bilder
6. **Cleanup Toggles** - Steuert automatisches Entfernen von Daten

### Toggle-Farben

| Sync-Typ | Farbe | Icon |
|----------|-------|------|
| Artists | Spotify-Grün (#1DB954) | 👥 |
| Playlists | Violett (#7c3aed) | 📋 |
| Liked Songs | Rot (#ef4444) | ❤️ |
| Saved Albums | Orange (#f59e0b) | 💿 |
| Images | Blau (#3b82f6) | 🖼️ |

---

## Datenbank-Schema

### app_settings Tabelle

```sql
CREATE TABLE app_settings (
    id INTEGER PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT,
    value_type VARCHAR(50) DEFAULT 'string',
    category VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Neue Spalten in bestehenden Tabellen

**spotify_artists:**
```sql
ALTER TABLE spotify_artists ADD COLUMN image_path VARCHAR(500);
```

**spotify_albums:**
```sql
ALTER TABLE spotify_albums ADD COLUMN image_path VARCHAR(500);
ALTER TABLE spotify_albums ADD COLUMN is_saved BOOLEAN DEFAULT FALSE;
```

**playlists:**
```sql
ALTER TABLE playlists ADD COLUMN cover_path VARCHAR(500);
ALTER TABLE playlists ADD COLUMN is_liked_songs BOOLEAN DEFAULT FALSE;
ALTER TABLE playlists ADD COLUMN spotify_playlist_id VARCHAR(50);
```

---

## Services

### AppSettingsService

Verwaltet Runtime-Settings in der Datenbank.

```python
# Einstellungen abrufen
settings_service = AppSettingsService(session)
enabled = await settings_service.get_bool("spotify.auto_sync_enabled", default=True)
interval = await settings_service.get_int("spotify.artists_sync_interval_minutes", default=5)

# Einstellungen setzen
await settings_service.set("spotify.auto_sync_enabled", False, value_type="boolean")

# Spotify-Settings Summary
summary = await settings_service.get_spotify_settings_summary()
```

**Caching:**
- Settings werden für 30 Sekunden gecached
- Cache wird bei Änderungen invalidiert

### SpotifyImageService

Lädt und speichert Spotify-Bilder lokal.

```python
image_service = SpotifyImageService(settings)

# Bild herunterladen
path = await image_service.download_artist_image(spotify_id, image_url)
# Returns: "artwork/spotify/artists/abc123.webp"

# Disk Usage abrufen
usage = image_service.get_disk_usage()
# Returns: {"artists": 1234567, "albums": 8901234, "playlists": 123456, "total": 10259257}

count = image_service.get_image_count()
# Returns: {"artists": 42, "albums": 156, "playlists": 12, "total": 210}

# Cleanup
image_service.cleanup_artist_image(spotify_id)
```

### SpotifySyncService

Orchestriert die Synchronisation.

```python
sync_service = SpotifySyncService(
    spotify_client=spotify_client,
    repository=repository,
    image_service=image_service,
    settings_service=settings_service,
)

# Einzelne Syncs
result = await sync_service.sync_followed_artists(access_token, force=True)
result = await sync_service.sync_user_playlists(access_token)
result = await sync_service.sync_liked_songs(access_token)
result = await sync_service.sync_saved_albums(access_token)

# Vollständiger Sync
results = await sync_service.run_full_sync(access_token, force=True)
```

### SpotifySyncWorker

Background Worker für automatischen Sync.

```python
# Worker wird beim App-Start automatisch gestartet (lifecycle.py)
spotify_sync_worker = SpotifySyncWorker(
    db=db,
    token_manager=db_token_manager,
    settings=settings,
    check_interval_seconds=60,  # Prüft alle 60s ob ein Sync fällig ist
)
await spotify_sync_worker.start()

# Status abfragen
status = worker.get_status()
# Returns: {
#   "running": True,
#   "check_interval_seconds": 60,
#   "last_sync": {"artists": "2025-11-28T10:30:00", ...},
#   "stats": {"artists": {"count": 5, "last_result": {...}}, ...}
# }

# Force Sync (bypass cooldown)
results = await worker.force_sync("artists")  # oder None für alle
```

**Verhalten:**
- Läuft beim App-Start automatisch
- Prüft alle 60 Sekunden ob ein Sync fällig ist
- Respektiert die Cooldown-Intervalle aus Settings
- Bei Token-Fehler: Überspringt Sync bis Token wieder da
- Bei Sync-Fehler: Loggt und versucht beim nächsten Durchlauf erneut

---

## Fehlerbehandlung

### Häufige Fehler

| Fehler | Ursache | Lösung |
|--------|---------|--------|
| `401 Not authenticated` | Kein Spotify-Token | Mit Spotify verbinden |
| `429 Rate Limited` | Zu viele API-Anfragen | Cooldown erhöhen |
| `500 Sync failed` | Interner Fehler | Logs prüfen |

### Logging

Alle Sync-Operationen werden geloggt:

```
INFO  - Starting artist sync...
INFO  - Fetched 42 followed artists from Spotify
INFO  - Downloaded image for artist: Artist Name
INFO  - Artist sync complete: 42 synced, 3 removed
```

---

## Best Practices

### Empfohlene Einstellungen

| Nutzung | Artists Interval | Playlists Interval | Images |
|---------|------------------|-------------------|--------|
| Gelegentlich | 30 min | 60 min | An |
| Regelmäßig | 10 min | 30 min | An |
| Power User | 5 min | 10 min | An |
| Bandbreite sparen | 60 min | 120 min | Aus |

### Speicherplatz-Schätzung

| Bibliotheksgröße | Geschätzte Bildgröße |
|------------------|---------------------|
| Klein (50 Artists, 20 Albums) | ~5 MB |
| Mittel (200 Artists, 100 Albums) | ~25 MB |
| Groß (500 Artists, 500 Albums) | ~75 MB |

---

## Verwandte Dokumentation

- [Settings](./settings.md) - Allgemeine Settings-Dokumentation
- [Authentication](./authentication.md) - Spotify OAuth Setup
- [Followed Artists](./followed-artists.md) - Artist-Management
- [Playlist Management](./playlist-management.md) - Playlist-Features

---

## Changelog

### Version 1.1 (2025-11-28)

- ✅ **SpotifySyncWorker** - Background Worker für automatischen Sync
- ✅ Cooldown-Tracking (in-memory, respektiert Settings-Intervalle)
- ✅ Worker-Status API Endpoint (`GET /spotify-sync/worker-status`)
- ✅ Automatischer Start beim App-Start
- ✅ Graceful Shutdown

### Version 1.0 (2025-11-28)

- ✅ Initial Release
- ✅ Auto-Sync für Artists, Playlists, Liked Songs, Saved Albums
- ✅ Lokale Bilderspeicherung (WebP)
- ✅ Runtime-Settings in DB
- ✅ Settings UI mit Toggle-Controls
- ✅ Manual Sync Trigger
- ✅ Disk Usage Statistics
