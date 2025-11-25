# Track Management

> **Version:** 1.0  
> **Last Updated:** 2025-11-25

---

## Übersicht

Das Track Management ermöglicht die Verwaltung einzelner Tracks: Suche, Download, Metadaten-Anzeige und -Bearbeitung. Du kannst Tracks auf Spotify suchen, von Soulseek herunterladen und ihre Metadaten sowohl in der Datenbank als auch in den Dateien bearbeiten.

---

## Features

### Track-Suche

- **Spotify-Suche**: Suche nach Tracks auf Spotify
- **Flexible Queries**: Suche nach Titel, Artist, Album oder ISRC

### Track-Download

- **Soulseek-Download**: Tracks von Soulseek herunterladen
- **Qualitätsauswahl**: Bevorzugte Qualität wählen
- **Automatische Suche**: Beste verfügbare Quelle finden

### Track-Details

- **Vollständige Metadaten**: Titel, Artist, Album, Genre, Jahr, etc.
- **Technische Infos**: Dauer, Dateiformat, Dateipfad
- **IDs**: Spotify-URI, MusicBrainz-ID, ISRC

### Metadaten-Bearbeitung

- **Datenbank-Update**: Metadaten in SoulSpot aktualisieren
- **Datei-Tags**: ID3-Tags in der Audio-Datei ändern
- **Erlaubte Felder**: Titel, Artist, Album, Genre, Jahr, Track-Nr., Disc-Nr.

---

## Nutzung über die Web-UI

### Track suchen

1. Navigiere zu **Tracks** oder nutze die Suchleiste
2. Gib deinen Suchbegriff ein
3. Ergebnisse werden von Spotify geladen
4. Klicke auf einen Track für Details

### Track herunterladen

1. Öffne die Track-Details
2. Klicke auf **Download**
3. Wähle die gewünschte Qualität:
   - **Best**: Höchste verfügbare Qualität (FLAC bevorzugt, dann nach Bitrate/Dateigröße sortiert)
   - **Good**: Mindestens 256kbps oder FLAC
   - **Any**: Erste verfügbare Audio-Datei
4. Der Download wird zur Queue hinzugefügt

> **Aus Quellcode:** Die `SearchAndDownloadTrackUseCase` verwendet `AdvancedSearchService` für intelligente Dateiauswahl mit Fuzzy-Matching und Qualitätsscoring. FLAC-Dateien erhalten einen Bonus von 1000 Punkten im Ranking.

### Metadaten bearbeiten

1. Öffne die Track-Details
2. Klicke auf **Edit Metadata**
3. Ändere die gewünschten Felder
4. Klicke auf **Save**
5. Die Änderungen werden in DB und Datei gespeichert

---

## API-Endpunkte

### GET `/api/tracks/search`

Sucht nach Tracks auf Spotify.

**Query-Parameter:**
| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| `query` | string | - | Suchbegriff (erforderlich) |
| `limit` | int | 20 | Anzahl der Ergebnisse (max 100) |
| `access_token` | string | - | Spotify Access Token (erforderlich) |

**Response:**
```json
{
  "tracks": [
    {
      "id": "spotify-track-id",
      "name": "Track Title",
      "artists": [
        {"name": "Artist Name"}
      ],
      "album": {"name": "Album Name"},
      "duration_ms": 240000,
      "uri": "spotify:track:xyz"
    }
  ],
  "total": 50,
  "query": "search term",
  "limit": 20
}
```

### GET `/api/tracks/{track_id}`

Ruft Details eines Tracks ab.

**Response:**
```json
{
  "id": "track-uuid",
  "title": "Track Title",
  "artist": "Artist Name",
  "album": "Album Name",
  "album_artist": "Album Artist",
  "genre": "Electronic",
  "year": 2024,
  "artist_id": "artist-uuid",
  "album_id": "album-uuid",
  "duration_ms": 240000,
  "track_number": 5,
  "disc_number": 1,
  "spotify_uri": "spotify:track:xyz",
  "musicbrainz_id": "mbid-123",
  "isrc": "USRC12345678",
  "file_path": "/music/Artist/Album/track.flac",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-15T00:00:00Z"
}
```

### POST `/api/tracks/{track_id}/download`

Startet den Download eines Tracks.

**Query-Parameter:**
| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| `quality` | string | "best" | Qualitätspräferenz (best, good, any) |

**Response:**
```json
{
  "message": "Download started",
  "track_id": "track-uuid",
  "download_id": "download-uuid",
  "quality": "best",
  "status": "queued",
  "search_results_count": 15
}
```

### POST `/api/tracks/{track_id}/enrich`

Reichert Metadaten von MusicBrainz an.

**Query-Parameter:**
| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| `force_refresh` | bool | false | Cache umgehen |

**Response:**
```json
{
  "message": "Track enriched successfully",
  "track_id": "track-uuid",
  "enriched": true,
  "enriched_fields": ["genre", "musicbrainz_id"],
  "musicbrainz_id": "mbid-123",
  "errors": []
}
```

### PATCH `/api/tracks/{track_id}/metadata`

Aktualisiert Track-Metadaten.

**Request:**
```json
{
  "title": "New Title",
  "artist": "New Artist",
  "album": "New Album",
  "genre": "New Genre",
  "year": 2024,
  "track_number": 1,
  "disc_number": 1
}
```

**Erlaubte Felder:**
- `title`
- `artist`
- `album`
- `album_artist`
- `genre`
- `year`
- `track_number`
- `disc_number`

**Response:**
```json
{
  "message": "Metadata updated successfully",
  "track_id": "track-uuid",
  "updated_fields": ["title", "artist", "genre"]
}
```

**Side Effects:**
- Metadaten werden in der Datenbank aktualisiert
- Wenn eine Datei existiert: ID3-Tags werden ebenfalls aktualisiert

---

## Qualitätsprofile

### "best" (Standard)

Sucht nach der höchsten verfügbaren Qualität. Das System verwendet ein Scoring-Algorithmus:

- FLAC-Dateien erhalten einen signifikanten Bonus
- Höhere Bitrate wird bevorzugt
- Größere Dateien werden bei gleicher Qualität bevorzugt

Priorität:
1. FLAC (Lossless)
2. Höhere Bitrate (z.B. 320kbps vor 256kbps)
3. Größere Dateigröße

### "good"

Akzeptiert Dateien mit mindestens 256kbps ODER FLAC-Format.

### "any"

Nimmt die erste verfügbare Audio-Datei (MP3, FLAC, M4A, OGG, OPUS, WAV).

---

## ID3-Tag-Mapping

Bei der Metadaten-Bearbeitung werden folgende ID3-Frames aktualisiert:

| Feld | ID3v2.4 Frame | Beschreibung |
|------|---------------|--------------|
| `title` | TIT2 | Track-Titel |
| `artist` | TPE1 | Ausführender Künstler |
| `album` | TALB | Album-Name |
| `album_artist` | TPE2 | Album-Künstler |
| `genre` | TCON | Genre |
| `year` | TDRC | Release-Jahr |
| `track_number` | TRCK | Track-Nummer |
| `disc_number` | TPOS | CD/Disc-Nummer |

---

## Workflow-Beispiele

### Spotify-Track finden und herunterladen

```bash
# 1. Nach Track suchen
curl "/api/tracks/search?query=Artist%20-%20Song&access_token=xyz"

# 2. Track importieren (falls nicht in DB)
# (passiert automatisch beim Playlist-Import)

# 3. Download starten
curl -X POST "/api/tracks/{track_id}/download?quality=best"

# 4. Download-Status prüfen
curl "/api/downloads/{download_id}"
```

### Metadaten korrigieren

```bash
# 1. Track-Details abrufen
curl "/api/tracks/{track_id}"

# 2. Metadaten aktualisieren
curl -X PATCH "/api/tracks/{track_id}/metadata" \
  -H "Content-Type: application/json" \
  -d '{"title": "Korrekter Titel", "genre": "Electronic"}'
```

### Track mit MusicBrainz anreichern

```bash
# Metadata von MusicBrainz holen
curl -X POST "/api/tracks/{track_id}/enrich?force_refresh=true"
```

---

## Suchsyntax

### Einfache Suche

```
Track Title
```

### Artist und Track

```
Artist Name - Track Title
```

### Album-Suche

```
album:Album Name artist:Artist Name
```

### ISRC-Suche

```
isrc:USRC12345678
```

---

## Troubleshooting

### Problem: Track wird nicht gefunden

**Mögliche Ursachen:**
1. **Rechtschreibung**: Prüfe die Schreibweise
2. **Sonderzeichen**: Entferne Sonderzeichen aus der Suche
3. **Regional**: Track ist in deiner Region nicht verfügbar

### Problem: Download findet keine Quellen

**Mögliche Ursachen:**
1. **Seltener Track**: Nicht auf Soulseek verfügbar
2. **Rechtschreibung**: Soulseek-Suche ist exakt
3. **Netzwerk**: Soulseek-Verbindung prüfen

**Lösung:** Versuche "any" Qualität für breitere Suche

### Problem: Metadaten werden nicht in Datei geschrieben

**Mögliche Ursachen:**
1. **Datei existiert nicht**: Track wurde noch nicht heruntergeladen
2. **Schreibrechte**: Keine Berechtigung für die Datei
3. **Format**: Nicht alle Formate unterstützen alle Tags

### Problem: Falsche Metadaten nach Enrichment

**Lösung:** 
1. Nutze `force_refresh=true` für neuen Versuch
2. Bearbeite manuell über PATCH-Endpoint
3. Manuelle Änderungen haben höchste Priorität

---

## Verwandte Features

- [Download Management](./download-management.md) - Für Download-Queue
- [Metadata Enrichment](./metadata-enrichment.md) - Für Multi-Source Anreicherung
- [Playlist Management](./playlist-management.md) - Für Batch-Track-Operationen
