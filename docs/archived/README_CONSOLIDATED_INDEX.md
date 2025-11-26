# 📦 Archived Documentation - Consolidated Index

**Purpose:** This directory contains historical documentation from SoulSpot development.  
**Status:** 🗂️ Consolidated (previously split between `archive/` and `archived/`)  
**Last Updated:** 2025-11-26  
**Maintenance:** See `docs/development/DOCUMENTATION_MAINTENANCE_LOG.md`

---

## 📂 Directory Structure

```
archived/
├── README.md (this file)
├── DEPRECATED.md (files to ignore)
│
├── archive/              # Old roadmaps/planning
│   └── development-roadmap-archived.md
│   └── development-roadmap.md
│
├── ui/                   # Old UI documentation
│   ├── README_UI_1_0.md
│   └── ... (various UI docs)
│
├── sessions/             # Development session logs
│   ├── SESSION_SUMMARY.md
│   ├── QA_SESSION_SUMMARY.md
│   ├── etc.
│
├── issues/               # Old GitHub issue templates
│   ├── example-issues.md
│   └── v2.0-dynamic-views-issues.md
│
├── analysis/             # Initial project analysis
│   ├── initial-assessment.md
│   └── ... (analysis docs)
│
├── improvements/         # Improvement tracking
│   └── IMPROVEMENTS.md
│
└── history/              # Historical summaries
    ├── PHASE1_SUMMARY.md
    ├── PHASE2_SUMMARY.md
    ├── etc.
```

---

## ⚠️ Status of Each Section

### 🔴 DEPRECATED - Do Not Use

These were replaced or are outdated:

**Old Roadmaps:**
- `archive/development-roadmap-archived.md` - Superseded by `docs/development/frontend-roadmap.md`
- `archive/development-roadmap.md` - Superseded by `docs/development/backend-roadmap.md`
- `archived/frontend-development-roadmap-*.md` (multiple variants) - Old frontend planning
- All v1.0/v2.0/v3.0 planning docs - v3.0 is now planned, not v1.0/v2.0

**Old UI Docs:**
- `ui/` - Documentation for old UI versions (pre-current design system)
- All references to `/ui/*` routes (now `/`) - Routes restructured

**Why:** Created during early phases, replaced with current implementations

---

### 🟡 REFERENCE ONLY - Historical Value

These contain useful historical information but are not current:

**Session Logs:**
- `sessions/*.md` - Development session summaries
- Value: Shows decision-making process, debugging sessions
- Use: Reference for context, not implementation

**Issue Templates:**
- `issues/*.md` - Old GitHub issue templates
- Value: Historical record of planned features
- Use: Reference for feature scope definition

**Analysis Docs:**
- `analysis/initial-assessment.md` - Pre-development architecture analysis
- Value: Shows original design thinking
- Use: Learning about why decisions were made

---

### 🟢 USEFUL - Keep for Reference

These provide useful context about development:

**History Summaries:**
- `history/PHASE*_SUMMARY.md` - Phase implementation summaries
- Value: Development timeline, what was completed when
- Use: Understanding feature rollout history

**Improvement Tracking:**
- `improvements/IMPROVEMENTS.md` - Code quality improvements over time
- Value: Shows continuous improvement efforts
- Use: Understanding code quality evolution

---

## 🗂️ How to Navigate

### I want to understand the development history
→ See `history/` directory (PHASE1-7 summaries)

### I want to understand old design decisions
→ See `analysis/initial-assessment.md`

### I want to reference an old feature design
→ Check `issues/` for the original issue definition

### I need to know what was in an old version
→ See `docs/project/CHANGELOG.md` (main documentation)

### I'm looking for current roadmaps
→ **NOT HERE** - See `docs/development/` instead

---

## 🚀 Current Documentation Locations

For active documentation, see:

| Information | Location |
|-------------|----------|
| **Current Roadmaps** | `docs/development/frontend-roadmap.md`, `backend-roadmap.md` |
| **API Reference** | `docs/api/README.md` and sub-pages |
| **Release Notes** | `docs/project/CHANGELOG.md` |
| **Architecture** | `docs/project/architecture.md` |
| **Contributing** | `docs/project/contributing.md` |
| **Getting Started** | `docs/guides/user/user-guide.md` |

---

## 🧹 Consolidation Notes

**Date:** 2025-11-26

Previously, archived documentation was split between:
- `docs/archive/` (1 file) - partial archive
- `docs/archived/` (47 files) - main archive

**Action Taken:** 
- Consolidated into single `docs/archived/` directory
- Removed empty `docs/archive/`
- Created this index for navigation

**Why:** 
- Easier to locate archived files
- Clear navigation structure
- Prevents confusion with active documentation

---

## 📝 File Retention Policy

### Keep Indefinitely
- Phase summaries (show project progress)
- Session logs (show decision-making)
- Architecture analysis (shows design thinking)

### Review Quarterly
- Old roadmaps (check if planning is still relevant)
- Issue templates (check if issue types still apply)

### Delete After 1 Year
- Session logs older than 1 year (unless historically significant)
- Temporary documentation from debugging sessions

**Last Retention Review:** 2025-11-26

---

## 🤝 Contributing

If you're adding historical documentation:

1. Place in appropriate subdirectory (e.g., `sessions/`, `analysis/`)
2. Add date to filename if it's time-sensitive
3. Include **[ARCHIVED]** or **[HISTORICAL]** tag in title if it may cause confusion
4. Update this README's `Directory Structure` section
5. Specify in header: "Status: Historical, see [current-location] for active docs"

---

## 📚 Related Documentation

- **Maintenance Log:** `docs/development/DOCUMENTATION_MAINTENANCE_LOG.md`
- **Maintenance Summary:** `docs/development/DOCUMENTATION_MAINTENANCE_SUMMARY.md`
- **Contributing Guide:** `docs/project/contributing.md`

---

**Consolidation Completed:** 2025-11-26  
**Next Review:** 2025-12-26  
**Contact:** See `DOCUMENTATION_MAINTENANCE_LOG.md` for support
