# SoulSpot New UI - Prototype

## 📍 Standort

Alle neuen UI-Dateien befinden sich in `docs/feat-ui/prototype/` als **Prototyp**.

Dies ermöglicht:
- ✅ Entwicklung ohne Einfluss auf die bestehende UI
- ✅ Review und Testing vor Integration
- ✅ Einfaches Verschieben nach `src/soulspot/` wenn bereit

## 📁 Struktur

```
docs/feat-ui/prototype/
├── templates/new-ui/
│   ├── base.html
│   ├── README.md
│   └── pages/
│       ├── dashboard.html
│       ├── library-artists.html
│       ├── playlists.html
│       ├── downloads.html
│       ├── search.html
│       └── settings.html
│
└── static/new-ui/
    ├── css/
    │   ├── main.css
    │   ├── variables.css
    │   └── components.css
    └── js/
        └── app.js
```

# SoulSpot UI Prototype

This directory contains the **complete frontend prototype** for the new SoulSpot UI.
It is a standalone set of HTML, CSS, and JavaScript files that demonstrate the new design and functionality without requiring the backend.

## 🎨 Features

- **Complete Design System**: Dark theme, glassmorphism, responsive grid.
- **14 Fully Implemented Pages**: Dashboard, Library, Playlists, Settings, Onboarding, **Styleguide**, etc.
- **Interactive Components**:
  - Mobile-responsive Sidebar (with Toggle)
  - Modals & Toast Notifications
  - Context Menus
  - Tabbed Interfaces
  - Play/Download Buttons (Mock functionality)
  - Onboarding Wizard (Multi-step flow)
  - **Component Styleguide** (Developer reference)

## 🚀 How to Run

Since this is a frontend prototype using absolute paths (e.g., `/static/...`), it needs to be served via a web server.

### Option 1: Python Simple Server (Recommended)

Run this command from the `docs/feat-ui/prototype/` directory:

```bash
# Go to the prototype directory
cd docs/feat-ui/prototype

# Start a simple server on port 8000
python3 -m http.server 8000
```

Then open **[http://localhost:8000/templates/new-ui/pages/dashboard.html](http://localhost:8000/templates/new-ui/pages/dashboard.html)** in your browser.

**Note**: Since there is no backend router, you will need to manually navigate between HTML files if links like `/dashboard` don't work (they expect a backend router).
For the best experience, open the HTML files directly or configure a simple rewrite rule if possible.

### Option 2: VS Code Live Server

If you use the "Live Server" extension in VS Code:
1. Right-click on `templates/new-ui/pages/dashboard.html`
2. Select "Open with Live Server"

## 📁 Structure

- `templates/new-ui/`: HTML files (Jinja2 ready)
- `static/new-ui/`: CSS, JS, and assets
- `README.md`: This file

### Option 2: Direkt Verschieben (Wenn bereit)

Wenn die neue UI bereit für Production ist:

```bash
# Verschiebe Templates
mv docs/feat-ui/prototype/templates/new-ui src/soulspot/templates/

# Verschiebe Static files
mv docs/feat-ui/prototype/static/new-ui src/soulspot/static/

# Lösche Prototype-Ordner
rm -rf docs/feat-ui/prototype
```

## 📝 Nächste Schritte

1. **Review**: Schaue dir alle Seiten in `docs/feat-ui/prototype/` an
2. **Feedback**: Gib Feedback zu Design und Funktionalität
3. **Anpassungen**: Ich nehme Änderungen vor
4. **Integration**: Wenn alles passt, verschieben wir nach `src/`

## 📚 Dokumentation

Siehe:
- [FRONTEND_COMPLETE.md](../FRONTEND_COMPLETE.md) - Komplette Übersicht
- [README.md](templates/new-ui/README.md) - UI-Dokumentation
- [DESIGN_SYSTEM.md](../DESIGN_SYSTEM.md) - Design-System

---

**Status**: Prototyp in Entwicklung  
**Standort**: `docs/feat-ui/prototype/`  
**Bereit für**: Review und Testing
