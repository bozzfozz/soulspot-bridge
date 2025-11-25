# Download Management

> **Version:** 1.0  
> **Last Updated:** 2025-11-25

---

## Übersicht

Das Download Management steuert alle Downloads von Soulseek über den slskd-Dienst. Es bietet eine vollständige Queue-Verwaltung mit Priorisierung, Pause/Resume-Funktionen und Batch-Operationen.

---

## Features

### Download-Queue

- **Zentrale Warteschlange**: Alle Downloads werden in einer Queue verwaltet
- **Priorisierung**: Downloads können mit Prioritäten versehen werden (höher = schneller)
- **Parallel-Downloads**: Konfigurierbare Anzahl gleichzeitiger Downloads

### Einzelne Downloads

- **Status-Tracking**: Echtzeit-Fortschrittsanzeige für jeden Download
- **Pause/Resume**: Einzelne Downloads pausieren und fortsetzen
- **Cancel**: Downloads abbrechen
- **Retry**: Fehlgeschlagene Downloads erneut versuchen

### Batch-Operationen

- **Batch-Download**: Mehrere Tracks gleichzeitig zur Queue hinzufügen
- **Batch-Actions**: Mehrere Downloads gleichzeitig pausieren, fortsetzen oder abbrechen

### Queue-Kontrolle

- **Globale Pause**: Alle Downloads pausieren
- **Globale Resume**: Alle Downloads fortsetzen
- **Queue-Status**: Übersicht über aktive, wartende und abgeschlossene Downloads

---

## Download-Status

| Status | Beschreibung |
|--------|--------------|
| `pending` | Initialer Status, vor der Queue-Einreihung |
| `queued` | In der Warteschlange, wartet auf Verarbeitung |
| `downloading` | Download läuft aktuell |
| `completed` | Erfolgreich heruntergeladen |
| `failed` | Fehlgeschlagen (kann wiederholt werden) |
| `cancelled` | Vom Benutzer abgebrochen |

> **Hinweis:** Der Status `paused` existiert nicht als separater Enum-Wert. Pausierte Downloads werden auf `queued` zurückgesetzt.

---

## Nutzung über die Web-UI

### Download-Queue anzeigen

1. Navigiere zu **Downloads** im Hauptmenü
2. Die Queue zeigt alle aktiven und wartenden Downloads
3. Fortschrittsbalken zeigen den aktuellen Status

### Download priorisieren

1. Finde den Download in der Queue
2. Klicke auf das Prioritäts-Icon
3. Setze einen Wert für die Priorisierung

**Prioritätswerte (gemäß Domain-Entity):**
- `0`: P0 - Höchste Priorität
- `1`: P1 - Mittlere Priorität
- `2`: P2 - Niedrigste Priorität

### Fehlgeschlagene Downloads wiederholen

1. Filter nach Status "Failed"
2. Klicke auf das Retry-Icon
3. Der Download wird erneut zur Queue hinzugefügt

---

## API-Endpunkte

### GET `/api/downloads/`

Listet alle Downloads auf.

**Query-Parameter:**
| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| `status` | string | null | Filter nach Status (queued, downloading, completed, failed) |
| `skip` | int | 0 | Offset für Pagination |
| `limit` | int | 20 | Anzahl der Ergebnisse (max 100) |

**Response:**
```json
{
  "downloads": [
    {
      "id": "download-uuid",
      "track_id": "track-uuid",
      "status": "downloading",
      "priority": 0,
      "progress_percent": 45.5,
      "source_url": "slskd://...",
      "target_path": "/music/Artist/Album/track.mp3",
      "error_message": null,
      "started_at": "2025-01-15T10:00:00Z",
      "completed_at": null,
      "created_at": "2025-01-15T09:55:00Z",
      "updated_at": "2025-01-15T10:00:30Z"
    }
  ],
  "total": 42,
  "status": null,
  "skip": 0,
  "limit": 20
}
```

### GET `/api/downloads/status`

Gibt den Status der Download-Queue zurück.

**Response:**
```json
{
  "paused": false,
  "max_concurrent_downloads": 5,
  "active_downloads": 3,
  "queued_downloads": 15,
  "total_jobs": 42,
  "completed": 20,
  "failed": 2,
  "cancelled": 2
}
```

### GET `/api/downloads/{download_id}`

Ruft den Status eines einzelnen Downloads ab.

**Response:**
```json
{
  "id": "download-uuid",
  "track_id": "track-uuid",
  "status": "downloading",
  "priority": 10,
  "progress_percent": 75.0,
  "source_url": "slskd://user/path/to/file.flac",
  "target_path": "/music/Artist/Album/track.flac",
  "error_message": null,
  "started_at": "2025-01-15T10:00:00Z",
  "completed_at": null,
  "created_at": "2025-01-15T09:55:00Z",
  "updated_at": "2025-01-15T10:05:00Z"
}
```

### POST `/api/downloads/pause`

Pausiert die gesamte Download-Queue.

**Response:**
```json
{
  "message": "Download queue paused successfully",
  "status": "paused"
}
```

### POST `/api/downloads/resume`

Setzt die Download-Queue fort.

**Response:**
```json
{
  "message": "Download queue resumed successfully",
  "status": "active"
}
```

### POST `/api/downloads/batch`

Startet Batch-Downloads für mehrere Tracks.

**Request:**
```json
{
  "track_ids": ["track-uuid-1", "track-uuid-2", "track-uuid-3"],
  "priority": 0
}
```

**Response:**
```json
{
  "message": "Batch download initiated for 3 tracks",
  "job_ids": ["job-1", "job-2", "job-3"],
  "total_tracks": 3
}
```

### POST `/api/downloads/{download_id}/cancel`

Bricht einen Download ab.

**Response:**
```json
{
  "message": "Download cancelled",
  "download_id": "download-uuid",
  "status": "cancelled"
}
```

### POST `/api/downloads/{download_id}/retry`

Wiederholt einen fehlgeschlagenen Download.

**Response:**
```json
{
  "message": "Download retry initiated",
  "download_id": "download-uuid",
  "status": "queued"
}
```

### POST `/api/downloads/{download_id}/priority`

Ändert die Priorität eines Downloads.

**Request:**
```json
{
  "priority": 0
}
```

> **Hinweis:** Prioritätswerte sind 0-2 (0=P0 höchste, 1=P1 mittel, 2=P2 niedrig) gemäß Domain-Entity-Validierung.

**Response:**
```json
{
  "message": "Priority updated successfully",
  "download_id": "download-uuid",
  "priority": 0
}
```

### POST `/api/downloads/{download_id}/pause`

Pausiert einen einzelnen Download.

### POST `/api/downloads/{download_id}/resume`

Setzt einen pausierten Download fort.

### POST `/api/downloads/batch-action`

Führt eine Aktion auf mehreren Downloads gleichzeitig aus.

**Request:**
```json
{
  "download_ids": ["download-1", "download-2", "download-3"],
  "action": "pause"
}
```

**Verfügbare Actions:**
- `cancel`: Downloads abbrechen
- `pause`: Downloads pausieren
- `resume`: Downloads fortsetzen
- `priority`: Priorität ändern (erfordert zusätzlich `priority` Feld)

**Response:**
```json
{
  "message": "Batch action 'pause' completed",
  "total": 3,
  "successful": 3,
  "failed": 0,
  "results": [...],
  "errors": []
}
```

---

## Konfiguration

Die Download-Einstellungen können in der Anwendungskonfiguration angepasst werden:

| Einstellung | Beschreibung | Default |
|-------------|--------------|---------|
| `max_concurrent_downloads` | Maximale parallele Downloads | 5 |
| `default_max_retries` | Automatische Wiederholungsversuche | 3 |
| `enable_priority_queue` | Priorisierung aktivieren | true |

---

## Workflow-Beispiele

### Track herunterladen

```mermaid
graph TD
    A[Track auswählen] --> B[POST /tracks/{id}/download]
    B --> C[Download in Queue]
    C --> D{Soulseek-Suche}
    D -->|Gefunden| E[Download startet]
    D -->|Nicht gefunden| F[Status: failed]
    E --> G{Download komplett?}
    G -->|Ja| H[Status: completed]
    G -->|Nein| I[Fortschritt aktualisieren]
    I --> G
```

### Batch-Download mit Priorisierung

```bash
# 1. Tracks zur Queue hinzufügen mit hoher Priorität
curl -X POST "/api/downloads/batch" \
  -H "Content-Type: application/json" \
  -d '{"track_ids": ["id1", "id2"], "priority": 100}'

# 2. Status überwachen
curl "/api/downloads/status"

# 3. Bei Bedarf pausieren
curl -X POST "/api/downloads/pause"
```

---

## Troubleshooting

### Problem: Downloads starten nicht

**Mögliche Ursachen:**
1. **Queue ist pausiert**: Prüfe mit `GET /api/downloads/status` ob `paused: true`
2. **slskd nicht erreichbar**: Prüfe die Verbindung zum slskd-Dienst
3. **Keine Soulseek-Quellen**: Der Track ist auf Soulseek nicht verfügbar

### Problem: Downloads schlagen immer fehl

**Mögliche Ursachen:**
1. **Soulseek-Account**: Prüfe ob dein Soulseek-Account aktiv ist
2. **Speicherplatz**: Prüfe ob genügend Platz im Download-Ordner ist
3. **Netzwerk**: Prüfe die Netzwerkverbindung

### Problem: Downloads sind langsam

**Lösungen:**
1. Erhöhe `max_concurrent_downloads` in den Einstellungen
2. Prüfe ob andere Anwendungen Bandbreite verbrauchen
3. Wähle Quellen mit schnelleren Upload-Raten

---

## Verwandte Features

- [Playlist Management](./playlist-management.md) - Für Batch-Downloads von Playlists
- [Track Management](./track-management.md) - Für einzelne Track-Downloads
- [Automation & Watchlists](./automation-watchlists.md) - Für automatische Downloads
- [Settings](./settings.md) - Für Download-Konfiguration
