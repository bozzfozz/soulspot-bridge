# Library Management API Documentation

## Overview

The Library Management API provides endpoints for scanning your music library, detecting duplicates, identifying broken files, and getting library statistics.

## Endpoints

### Start Library Scan

Start a new library scan operation.

**Endpoint:** `POST /api/library/scan`

**Request Body:**
```json
{
  "scan_path": "/path/to/music/library"
}
```

**Response:**
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "scan_path": "/path/to/music/library",
  "total_files": 1234,
  "message": "Library scan started"
}
```

**Status Codes:**
- `200 OK` - Scan started successfully
- `500 Internal Server Error` - Failed to start scan

**Example:**
```bash
curl -X POST http://localhost:8765/api/library/scan \
  -H "Content-Type: application/json" \
  -d '{"scan_path": "/mnt/music"}'
```

---

### Get Scan Status

Get the status and progress of a library scan.

**Endpoint:** `GET /api/library/scan/{scan_id}`

**Path Parameters:**
- `scan_id` (string, required) - The ID of the scan

**Response:**
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "scan_path": "/path/to/music/library",
  "total_files": 1234,
  "scanned_files": 567,
  "broken_files": 3,
  "duplicate_files": 12,
  "progress_percent": 45.9
}
```

**Status Values:**
- `pending` - Scan is queued
- `running` - Scan in progress
- `completed` - Scan finished successfully
- `failed` - Scan failed with error
- `cancelled` - Scan was cancelled

**Status Codes:**
- `200 OK` - Scan found and returned
- `404 Not Found` - Scan not found

**Example:**
```bash
curl http://localhost:8765/api/library/scan/550e8400-e29b-41d4-a716-446655440000
```

---

### Get Duplicate Files

Get a list of duplicate files detected in the library.

**Endpoint:** `GET /api/library/duplicates`

**Query Parameters:**
- `resolved` (boolean, optional) - Filter by resolved status
  - `true` - Only show resolved duplicates
  - `false` - Only show unresolved duplicates
  - Not specified - Show all duplicates

**Response:**
```json
{
  "duplicates": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "file_hash": "a1b2c3d4e5f6...",
      "duplicate_count": 3,
      "total_size_bytes": 15728640,
      "resolved": false,
      "primary_track_id": null,
      "tracks": [
        {
          "id": "track-id-1",
          "title": "Song Title",
          "file_path": "/mnt/music/artist1/album1/song.mp3",
          "file_size": 5242880,
          "is_broken": false
        },
        {
          "id": "track-id-2",
          "title": "Song Title",
          "file_path": "/mnt/music/artist1/album2/song.mp3",
          "file_size": 5242880,
          "is_broken": false
        },
        {
          "id": "track-id-3",
          "title": "Song Title",
          "file_path": "/mnt/music/copies/song.mp3",
          "file_size": 5242880,
          "is_broken": false
        }
      ]
    }
  ],
  "total_count": 15,
  "total_duplicate_files": 42,
  "total_wasted_bytes": 104857600
}
```

**Status Codes:**
- `200 OK` - Duplicates returned successfully

**Examples:**
```bash
# Get all duplicates
curl http://localhost:8765/api/library/duplicates

# Get only unresolved duplicates
curl http://localhost:8765/api/library/duplicates?resolved=false

# Get only resolved duplicates
curl http://localhost:8765/api/library/duplicates?resolved=true
```

---

### Get Broken Files

Get a list of broken or corrupted files in the library.

**Endpoint:** `GET /api/library/broken-files`

**Response:**
```json
{
  "broken_files": [
    {
      "id": "track-id-1",
      "title": "Corrupted Song",
      "artist_id": "artist-id-1",
      "album_id": "album-id-1",
      "file_path": "/mnt/music/broken/song.mp3",
      "file_size": 1024,
      "last_scanned_at": "2025-11-15T20:30:00Z"
    }
  ],
  "total_count": 5
}
```

**Status Codes:**
- `200 OK` - Broken files returned successfully

**Example:**
```bash
curl http://localhost:8765/api/library/broken-files
```

---

### Get Library Statistics

Get overall statistics about your music library.

**Endpoint:** `GET /api/library/stats`

**Response:**
```json
{
  "total_tracks": 5000,
  "tracks_with_files": 4800,
  "broken_files": 5,
  "duplicate_groups": 15,
  "total_size_bytes": 26843545600,
  "scanned_percentage": 96.0
}
```

**Fields:**
- `total_tracks` - Total number of tracks in database
- `tracks_with_files` - Number of tracks with associated files
- `broken_files` - Number of broken/corrupted files
- `duplicate_groups` - Number of duplicate file groups
- `total_size_bytes` - Total size of all files in bytes
- `scanned_percentage` - Percentage of tracks that have been scanned

**Status Codes:**
- `200 OK` - Statistics returned successfully

**Example:**
```bash
curl http://localhost:8765/api/library/stats
```

---

## Common Use Cases

### Scan Your Library

1. Start a scan:
```bash
curl -X POST http://localhost:8765/api/library/scan \
  -H "Content-Type: application/json" \
  -d '{"scan_path": "/mnt/music"}'
```

2. Monitor progress:
```bash
# Use the scan_id from the previous response
curl http://localhost:8765/api/library/scan/{scan_id}
```

3. Check results when completed:
```bash
# Get duplicates
curl http://localhost:8765/api/library/duplicates

# Get broken files
curl http://localhost:8765/api/library/broken-files

# Get statistics
curl http://localhost:8765/api/library/stats
```

### Clean Up Duplicates

1. Get unresolved duplicates:
```bash
curl http://localhost:8765/api/library/duplicates?resolved=false
```

2. Review the duplicate groups and decide which files to keep

3. Manually delete unwanted duplicates from filesystem

4. Run a new scan to update the database

### Fix Broken Files

1. Get broken files:
```bash
curl http://localhost:8765/api/library/broken-files
```

2. Review the broken files list

3. Either:
   - Replace the broken files with good copies
   - Delete broken files if unrecoverable
   - Re-download using the download API

4. Run a new scan to update the database

---

## Technical Details

### File Hash Algorithm

The library scanner uses SHA256 hashing for duplicate detection. This provides:
- Strong collision resistance
- Fast computation for large files
- Industry-standard reliability

### Audio File Validation

Files are validated using the mutagen library, which checks:
- Audio format support
- File integrity (readable audio stream)
- Audio properties (bitrate, sample rate, duration)
- Metadata tags (title, artist, album)

### Supported Audio Formats

- MP3 (`.mp3`)
- FLAC (`.flac`)
- M4A/AAC (`.m4a`, `.aac`)
- OGG Vorbis (`.ogg`)
- Opus (`.opus`)
- WAV (`.wav`)

### Performance Considerations

- Scanning is performed in the background
- Large libraries (>100k files) may take several minutes
- Progress is tracked and can be monitored in real-time
- Files are scanned in batches with periodic database commits
- Hash calculation uses efficient chunked reading for large files

---

## Error Handling

All endpoints may return error responses with the following format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common error codes:
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server-side error during processing
