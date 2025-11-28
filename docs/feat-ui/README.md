# SoulSpot UI Redesign

Welcome to the SoulSpot UI Redesign project! This folder contains everything you need to understand, run, and implement the new modern Web UI.

## 🚀 Quick Start

### 1. See How It Looks (Prototype)
We have built a **complete, interactive frontend prototype**. You can run it right now to see the design in action.

👉 **[Go to Prototype](./prototype/README.md)** (Instructions to run)

### 2. Know What To Do (Integration)
Ready to implement this into the main app? We have a step-by-step guide.

- **[Integration Guide](./INTEGRATION_GUIDE.md)**: Step-by-step migration plan.
- **[Backend Alignment](./BACKEND_ALIGNMENT.md)**: Mapping new UI to existing backend architecture.
- **[Frontend Agent](./frontend-agent.md)**: Rules for the AI Frontend Engineer.

---

## 📚 Documentation Index

### Core Documents

| Document | Description |
|----------|-------------|
| **[FRONTEND_COMPLETE.md](./FRONTEND_COMPLETE.md)** | **Start Here**: Overview of the completed frontend work. |
| **[NAVIGATION.md](./NAVIGATION.md)** | Map of all pages and how they connect. |
| **[DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md)** | Colors, typography, and UI rules. |
| **[COMPONENT_LIBRARY.md](./COMPONENT_LIBRARY.md)** | Reference for all UI components (Cards, Buttons, etc). |

### Technical Details

| Document | Description |
|----------|-------------|
| **[TECHNICAL_SPEC.md](./TECHNICAL_SPEC.md)** | Architecture and technical requirements. |
| **[ROADMAP.md](./ROADMAP.md)** | Project timeline and phases. |
| **[IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)** | General guide for development workflow. |

---

## 📂 Folder Structure

```
docs/feat-ui/
├── prototype/                   # ✨ THE CODE IS HERE
│   ├── templates/new-ui/       # HTML Files (Dashboard, Library, etc.)
│   └── static/new-ui/          # CSS & JS Files
│
├── INTEGRATION_GUIDE.md         # 📘 HOW TO MERGE IT
├── NAVIGATION.md                # 🗺️ SITE MAP
├── FRONTEND_COMPLETE.md         # ✅ SUMMARY
└── ... (other docs)
```

## 🎨 Design Highlights

- **Style**: Modern, Dark Theme (default), Light Theme (MediaManager-based), Glassmorphism
- **Color**: SoulSpot Red (`#fe4155`) for Dark Mode, MediaManager Gray (`#333333`) for Light Mode
- **Layout**: Fixed Sidebar + Responsive Grid
- **Tech**: HTML5, CSS3 (Variables), Vanilla JS, HTMX
- **Theming**: Full Dark/Light mode support via CSS custom properties

### Theme Support

| Mode | Primary | Background | Text | Source |
|------|---------|------------|------|--------|
| **Dark** | `#fe4155` (SoulSpot Red) | `#111827` | `#f9fafb` | SoulSpot Original |
| **Light** | `#333333` (Neutral Dark) | `#ffffff` | `#1a1a1a` | MediaManager |

See **[DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md)** for complete color palettes (Dark vs Light side-by-side).

See **[COMPONENT_LIBRARY.md](./COMPONENT_LIBRARY.md)** for Light Mode CSS for all ~20 components.

## ❓ FAQ

**Q: Do I need the backend to run the prototype?**
A: **No.** The prototype is standalone HTML/CSS/JS. Follow the [Prototype README](./prototype/README.md) to run it.

**Q: Where are the CSS files?**
A: In `docs/feat-ui/prototype/static/new-ui/css/`.

**Q: How do I add a new page?**
A: Copy `base.html` from the prototype templates and extend it. See [COMPONENT_LIBRARY.md](./COMPONENT_LIBRARY.md) for available components.

**Q: How do I enable Light Mode?**
A: Add `data-theme="light"` to your `<html>` or root element. The CSS variables will automatically switch. See [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md#light-mode-full-css-variable-set) for the full variable set.

**Q: Where do the Light Mode colors come from?**
A: Light Mode uses the [MediaManager](https://github.com/maxdorninger/MediaManager) design system (OKLCH color space). All colors are documented in [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md#neutral-colors-light-mode--mediamanager-reference).

---

**Status**: ✅ Frontend Prototype Complete (Ready for Integration)
**Theme Support**: ✅ Dark Mode (default) + ✅ Light Mode (MediaManager-based)
**Last Updated**: 2025-11-28
