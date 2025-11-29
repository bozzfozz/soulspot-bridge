# Local Library Spotify Enrichment

> **Version:** 1.0  
> **Last Updated:** 2025-11-29

---

## Übersicht

Das Local Library Enrichment Feature reichert lokale Musikdateien mit Spotify-Metadaten an. Anders als der Spotify-Sync, der nur gefolgte Artists und Playlists importiert, durchsucht dieses Feature Spotify nach Matches für **alle** lokalen Dateien – unabhängig davon, ob du den Artist auf Spotify folgst.

### Warum ist das nützlich?

1. **Lokale Dateien ohne Spotify-Link**: Du hast MP3s auf der Festplatte, aber sie haben keine Spotify-URIs
2. **Artwork fehlt**: Lokale Dateien haben oft keine Album-Cover
3. **Genres fehlen**: ID3-Tags enthalten selten Genre-Informationen
4. **Konsistente Bibliothek**: Alle Einträge haben dieselben Metadaten-Felder

---

## Features

### Automatisches Enrichment

- **Nach jedem Library Scan**: Wenn aktiviert, startet nach jedem Scan automatisch ein Enrichment-Job
- **Batch-Verarbeitung**: Verarbeitet 50 Items pro Durchlauf (konfigurierbar)
- **Rate Limiting**: 50ms Pause zwischen Spotify-API-Aufrufen
- **Fehlertoleranz**: Einzelne Fehler stoppen nicht den gesamten Prozess

### Matching-Algorithmus

**Für Artists:**
- Fuzzy Name Matching (70% Gewichtung)
- Spotify Popularity (30% Gewichtung)
- Filtert "Various Artists" automatisch aus

**Für Alben:**
- Album-Titel Matching (50% Gewichtung)
- Artist-Name Matching (50% Gewichtung)
- Sucht über Spotify Track Search API

### Confidence Scoring

- **≥80%**: Automatische Anwendung des Matches
- **50-79%**: Kandidat wird für manuelle Überprüfung gespeichert
- **<50%**: Kein Match gefunden

### Dual Album Type System (Lidarr-kompatibel)

Das System verwendet zwei Typ-Dimensionen wie Lidarr/MusicBrainz:

**Primary Type** (exklusiv):
- `album` - Standard-Album
- `ep` - Extended Play
- `single` - Single
- `broadcast` - Radio-Aufnahme
- `other` - Sonstiges

**Secondary Types** (kombinierbar):
- `compilation` - Compilation/Various Artists
- `soundtrack` - Soundtrack
- `live` - Live-Aufnahme
- `remix` - Remix-Album
- `dj-mix` - DJ Mix
- `mixtape` - Mixtape
- `demo` - Demo
- `spokenword` - Hörbuch/Spoken Word

**Beispiel:** Ein Live-Album einer Compilation hat:
- `primary_type = "album"`
- `secondary_types = ["live", "compilation"]`

### Various Artists Detection

Das System erkennt Compilations automatisch durch:
- TPE2 Tag (Album Artist) in Audiodateien
- TCMP Flag (iTunes Compilation)
- Artist-Namen wie "Various Artists", "VA", "V.A."

---

## Konfiguration

### Settings UI

Navigiere zu **Settings** → **Library** Tab:

| Setting | Default | Beschreibung |
|---------|---------|--------------|
| Auto-Enrich Local Library | ✓ An | Enrichment nach jedem Library Scan |

### Erweiterte Settings (via API/DB)

| Setting | Default | Beschreibung |
|---------|---------|--------------|
| `library.enrichment_batch_size` | 50 | Items pro Batch |
| `library.enrichment_rate_limit_ms` | 50 | Pause zwischen API-Calls (ms) |
| `library.enrichment_match_threshold` | 80 | Min. Confidence für Auto-Match (%) |
| `library.enrichment_download_artwork` | true | Artwork auch lokal speichern |
| `library.enrich_compilations` | true | Compilations auch enrichen |

---

## API-Endpunkte

### GET `/api/settings/library/enrichment`

Gibt aktuelle Enrichment-Settings zurück.

**Response:**
```json
{
  "auto_enrichment_enabled": true
}
```

### PUT `/api/settings/library/enrichment`

Aktualisiert Enrichment-Settings.

**Request:**
```json
{
  "auto_enrichment_enabled": false
}
```

**Response:**
```json
{
  "auto_enrichment_enabled": false
}
```

---

## Datenbank-Schema

### soulspot_albums (erweitert)

```sql
-- Neue Spalten für Album Types
album_artist VARCHAR(255)   -- Album-Level Artist (z.B. "Various Artists")
primary_type VARCHAR(20)    -- 'album', 'ep', 'single', 'broadcast', 'other'
secondary_types JSON        -- Array: ["compilation", "live", ...]
```

### enrichment_candidates (neu)

```sql
CREATE TABLE enrichment_candidates (
    id VARCHAR(36) PRIMARY KEY,
    entity_type VARCHAR(20),        -- 'artist' oder 'album'
    entity_id VARCHAR(36),          -- FK zu soulspot_artists/albums
    spotify_uri VARCHAR(255),       -- Spotify URI des Kandidaten
    spotify_name VARCHAR(255),      -- Name für Anzeige
    spotify_image_url VARCHAR(512), -- Preview Image
    confidence_score FLOAT,         -- 0.0 - 1.0
    is_selected BOOLEAN,            -- User hat diesen gewählt
    is_rejected BOOLEAN,            -- User hat diesen abgelehnt
    extra_info JSON,                -- Zusatzinfos (Genres, Followers, etc.)
    created_at DATETIME,
    updated_at DATETIME
);
```

---

## Workflow

### Automatischer Flow

```mermaid
graph TD
    A[Library Scan startet] --> B[Scan importiert Dateien]
    B --> C{Neue Items?}
    C -->|Nein| D[Ende]
    C -->|Ja| E{Auto-Enrichment aktiv?}
    E -->|Nein| D
    E -->|Ja| F[Enrichment Job gequeued]
    F --> G[Worker holt Spotify Token]
    G --> H[Batch Artists enrichen]
    H --> I[Batch Albums enrichen]
    I --> J{Mehr Items?}
    J -->|Ja| H
    J -->|Nein| K[Stats loggen]
    K --> D
```

### Matching-Prozess

```mermaid
graph LR
    A[Lokaler Artist] --> B[Spotify Search]
    B --> C[Top 5 Kandidaten]
    C --> D[Score berechnen]
    D --> E{Score >= 80%?}
    E -->|Ja| F[Auto-Apply]
    E -->|Nein| G{Score >= 50%?}
    G -->|Ja| H[Als Kandidat speichern]
    G -->|Nein| I[Kein Match]
```

---

## Architektur

### Komponenten

| Komponente | Pfad | Funktion |
|------------|------|----------|
| LocalLibraryEnrichmentService | `application/services/local_library_enrichment_service.py` | Hauptlogik |
| LibraryEnrichmentWorker | `application/workers/library_enrichment_worker.py` | Job-Handler |
| AppSettingsService | `application/services/app_settings_service.py` | Settings |
| EnrichmentCandidateModel | `infrastructure/persistence/models.py` | DB Model |

### Dependencies

```
LocalLibraryEnrichmentService
├── ArtistRepository (get_unenriched, count_unenriched)
├── AlbumRepository (get_unenriched, count_unenriched)
├── AppSettingsService (enrichment settings)
├── SpotifyImageService (artwork download)
├── SpotifyClient (search API)
└── rapidfuzz (fuzzy matching)
```

---

## Migration

Die Migration `nn25010ppr58_add_album_types_and_enrichment.py` fügt hinzu:

1. **Album-Spalten**: `album_artist`, `primary_type`, `secondary_types`
2. **Enrichment Candidates Table**: Speichert potenzielle Matches
3. **Data Migration**: Markiert existierende "Various Artists" Alben als Compilations

### Migration ausführen

```bash
alembic upgrade head
```

### Rollback

```bash
alembic downgrade -1
```

---

## Troubleshooting

### Enrichment läuft nicht

**Prüfe:**
1. Ist `auto_enrichment_enabled` aktiviert? (Settings → Library)
2. Hat der letzte Scan neue Items importiert?
3. Ist ein gültiger Spotify-Token vorhanden?

**Logs prüfen:**
```bash
grep -i "enrichment" logs/soulspot.log
```

### Falsche Matches

**Problem:** Ein lokaler Artist wurde mit dem falschen Spotify-Artist verknüpft.

**Lösung:**
1. In DB: Setze `spotify_uri = NULL` für den Artist
2. Der nächste Enrichment-Lauf findet ihn erneut
3. Falls wieder falsch: Prüfe `enrichment_candidates` Tabelle

### Keine Artwork heruntergeladen

**Prüfe:**
1. Ist `spotify.download_images` aktiviert?
2. Ist `library.enrichment_download_artwork` aktiviert?
3. Hat der Spotify-Artist/Album ein Bild?

---

## Best Practices

### Vor dem ersten Enrichment

1. **Bibliothek organisieren**: Saubere Ordnerstruktur hilft beim Matching
2. **ID3-Tags prüfen**: Korrekte Artist/Album-Namen verbessern Matches
3. **Backup erstellen**: Falls etwas schiefgeht

### Nach dem Enrichment

1. **Candidates prüfen**: Schau in der DB nach `is_selected = false` Einträgen
2. **Statistiken prüfen**: Wie viele Items wurden enriched?
3. **Artwork prüfen**: Sind die Bilder korrekt?

### Performance-Tipps

- **Batch Size**: 50 ist ein guter Kompromiss
- **Rate Limit**: Nicht unter 50ms gehen (Spotify Rate Limit)
- **Nachts laufen lassen**: Große Bibliotheken brauchen Zeit

---

## Verwandte Features

- [Library Management](./library-management.md) - Library Scan triggert Enrichment
- [Spotify Sync](./spotify-sync.md) - Synct gefolgte Artists (anderer Ansatz)
- [Metadata Enrichment](./metadata-enrichment.md) - MusicBrainz Enrichment
- [Settings](./settings.md) - Konfigurationsübersicht
