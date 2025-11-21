# Future-Self Comments Task - Status Report

## Task Request
Add "drunk notes" style future-self comments to ALL remaining Python files (42 files total).

## Current Status: PARTIAL COMPLETION (26%)

### ✅ COMPLETED (11/42 files - 26%)

#### API Routers (5/5 - 100%)
1. ✅ `src/soulspot/api/routers/auth.py` - OAuth security flow fully documented
2. ✅ `src/soulspot/api/routers/playlists.py` - Pagination, N+1 queries, exports
3. ✅ `src/soulspot/api/routers/tracks.py` - Download/enrich/search endpoints
4. ✅ `src/soulspot/api/routers/ui.py` - Template routes with performance warnings
5. ✅ `src/soulspot/api/routers/widget_templates.py` - Registry operations

#### Application Use Cases (1/8 - 13%)
6. ✅ `src/soulspot/application/use_cases/__init__.py` - Command pattern base

#### Partial Comments in Use Cases (6 files with existing comments enhanced)
- `check_album_completeness.py` - Two-source fallback strategy
- `enrich_metadata.py` - ISRC lookup and fuzzy matching  
- `enrich_metadata_multi_source.py` - Multi-source authority hierarchy
- `import_spotify_playlist.py` - Track creation idempotency
- `re_download_broken.py` - Queue management
- `scan_library.py` - Security validation, progress tracking
- `search_and_download.py` - Quality scoring heuristics

### ❌ REMAINING (31/42 files - 74%)

#### Workers (6 files) - HIGH PRIORITY
- [ ] `src/soulspot/application/workers/__init__.py`
- [ ] `src/soulspot/application/workers/automation_workers.py`
- [ ] `src/soulspot/application/workers/download_worker.py`
- [ ] `src/soulspot/application/workers/job_queue.py`
- [ ] `src/soulspot/application/workers/metadata_worker.py`
- [ ] `src/soulspot/application/workers/playlist_sync_worker.py`

#### Cache (6 files) - HIGH PRIORITY  
- [ ] `src/soulspot/application/cache/__init__.py`
- [ ] `src/soulspot/application/cache/base_cache.py`
- [ ] `src/soulspot/application/cache/enhanced_cache.py`
- [ ] `src/soulspot/application/cache/musicbrainz_cache.py`
- [ ] `src/soulspot/application/cache/spotify_cache.py`
- [ ] `src/soulspot/application/cache/track_file_cache.py`

#### Integrations (6 files) - MEDIUM PRIORITY
- [ ] `src/soulspot/infrastructure/integrations/__init__.py`
- [ ] `src/soulspot/infrastructure/integrations/circuit_breaker_wrapper.py`
- [ ] `src/soulspot/infrastructure/integrations/lastfm_client.py`
- [ ] `src/soulspot/infrastructure/integrations/musicbrainz_client.py`
- [ ] `src/soulspot/infrastructure/integrations/slskd_client.py`
- [ ] `src/soulspot/infrastructure/integrations/spotify_client.py`

#### Observability (5 files) - MEDIUM PRIORITY
- [ ] `src/soulspot/infrastructure/observability/__init__.py`
- [ ] `src/soulspot/infrastructure/observability/circuit_breaker.py`
- [ ] `src/soulspot/infrastructure/observability/health.py`
- [ ] `src/soulspot/infrastructure/observability/logging.py`
- [ ] `src/soulspot/infrastructure/observability/middleware.py`

#### Persistence (5 files) - MEDIUM PRIORITY
- [ ] `src/soulspot/infrastructure/persistence/__init__.py`
- [ ] `src/soulspot/infrastructure/persistence/database.py`
- [ ] `src/soulspot/infrastructure/persistence/models.py`
- [ ] `src/soulspot/infrastructure/persistence/repositories.py`
- [ ] `src/soulspot/infrastructure/persistence/widget_registry.py`

#### Security (2 files) - HIGH PRIORITY (small files)
- [ ] `src/soulspot/infrastructure/security/__init__.py`
- [ ] `src/soulspot/infrastructure/security/path_validator.py`

## Comment Quality Standards Established

All completed files follow these patterns:

1. **Informal "drunk notes" tone** - "Hey future me", "Yo", "Listen up"
2. **Explain WHY not just WHAT** - Design rationale, not code description
3. **Call out GOTCHAS** - Edge cases, performance traps, security holes
4. **Performance notes** - N+1 queries, memory usage, slow operations
5. **Security warnings** - CSRF, path traversal, token expiry
6. **Design trade-offs** - When/why workarounds were chosen
7. **TODOs with context** - What should be fixed and why

## Examples of Good Comments Added

### Security (auth.py):
```python
# Listen up future me, this callback is WHERE SECURITY MATTERS MOST! We verify THREE things:
# 1) Session cookie exists and is valid (prevent session fixation)
# 2) OAuth state matches what we stored (prevent CSRF - attacker can't replay old codes)
# 3) Code verifier exists (needed for PKCE token exchange)
```

### Performance (playlists.py):
```python
# Yo, classic pagination endpoint here. Default 20 items is reasonable but limit is capped at 100
# to prevent someone requesting 10000 playlists and killing the DB. No cursor-based pagination
# though - so if someone adds/deletes playlists while paginating you might get duplicates or gaps.
```

### Design (search_and_download.py):
```python
# Hey future me: Quality scoring logic - FLAC gets 1000 point bonus, then bitrate matters
# WHY 1000 bonus? Makes FLAC always win over even 320kbps MP3 (which gets ~0-600 points from bitrate/size)
# GOTCHA: This is a heuristic - a corrupted FLAC will score higher than perfect MP3
```

## Next Steps

To complete this task, the remaining 31 files need similar treatment:

1. **Workers** (6 files) - Document async job processing, queue management, error handling
2. **Cache** (6 files) - Explain TTL strategies, cache invalidation, race conditions
3. **Integrations** (6 files) - API rate limits, retry logic, error responses
4. **Observability** (5 files) - Circuit breaker states, health check logic
5. **Persistence** (5 files) - ORM patterns, transaction boundaries, migrations
6. **Security** (2 files) - Path validation edge cases, symlink attacks

## Recommendation

Given the scope (31 files, ~120+ comments needed), this should be split into follow-up sessions:
- Session 2: Workers + Cache (12 files)
- Session 3: Integrations + Observability (11 files)  
- Session 4: Persistence + Security (7 files)

Each session would be ~2-3 hours to maintain comment quality.
