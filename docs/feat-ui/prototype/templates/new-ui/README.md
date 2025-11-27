# SoulSpot New UI - MediaManager-Inspired Design

## Overview

This is a **completely new UI** for SoulSpot, heavily inspired by [MediaManager](https://github.com/maxdorninger/MediaManager) with SoulSpot's signature red accent color (#fe4155).

## Design Philosophy

- **Dark Theme**: Deep blacks and grays for a modern, premium feel
- **Card-Based**: Everything is organized in clean, modern cards
- **Sidebar Navigation**: Fixed sidebar with icon + text navigation
- **Grid Layouts**: Consistent grid system for content
- **SoulSpot Red**: Keeping the iconic #fe4155 red as the accent color

## File Structure

```
src/soulspot/
├── templates/new-ui/
│   ├── base.html                 # Base layout with sidebar
│   ├── components/               # Reusable components (TODO)
│   └── pages/
│       └── dashboard.html        # Dashboard page
│
└── static/new-ui/
    ├── css/
    │   ├── main.css             # Main CSS entry point
    │   ├── variables.css        # CSS custom properties
    │   └── components.css       # Component styles
    └── js/
        └── app.js               # Main JavaScript
```

## Color Palette

### Background Colors
- **Primary**: `#0f0f0f` - Main background
- **Secondary**: `#1a1a1a` - Cards, panels, sidebar
- **Tertiary**: `#242424` - Hover states
- **Quaternary**: `#2e2e2e` - Active states

### Accent Color (SoulSpot Red)
- **Primary**: `#fe4155` - Main accent
- **Hover**: `#ff6b7a` - Hover state
- **Active**: `#d63547` - Active/pressed state
- **Subtle**: `rgba(254, 65, 85, 0.1)` - Subtle backgrounds

### Text Colors
- **Primary**: `#ffffff` - Main text
- **Secondary**: `#a0a0a0` - Secondary text
- **Muted**: `#6b6b6b` - Muted text

## Components

### Layout Components
- **Sidebar**: Fixed left sidebar with navigation
- **Main Content**: Flexible content area

### UI Components
- **Stat Cards**: Dashboard statistics with icons
- **Media Cards**: Album/playlist cards with hover overlays
- **Buttons**: Primary, secondary, outline, and icon buttons
- **Badges**: Status indicators
- **Grid System**: Responsive grid (2-6 columns)

## Usage

### Extending the Base Template

```html
{% extends "new-ui/base.html" %}

{% block title %}Page Title - SoulSpot{% endblock %}

{% block content %}
<!-- Your content here -->
{% endblock %}
```

### Using Components

#### Stat Card
```html
<div class="stat-card">
    <div class="stat-card-icon">
        <i class="fa-solid fa-music"></i>
    </div>
    <div class="stat-card-content">
        <div class="stat-card-label">Total Tracks</div>
        <div class="stat-card-value">1,234</div>
    </div>
</div>
```

#### Media Card
```html
<div class="media-card">
    <div class="media-card-image">
        <img src="cover.jpg" alt="Album">
        <div class="media-card-overlay">
            <div class="media-card-actions">
                <button class="btn-icon btn-primary">
                    <i class="fa-solid fa-play"></i>
                </button>
            </div>
        </div>
    </div>
    <div class="media-card-content">
        <div class="media-card-title">Album Name</div>
        <div class="media-card-subtitle">Artist Name</div>
    </div>
</div>
```

#### Grid Layout
```html
<div class="grid grid-cols-4">
    <!-- 4 columns on desktop, responsive on mobile -->
</div>
```

## Next Steps

### Immediate Tasks
1. ✅ Create base layout and CSS
2. ✅ Create dashboard page
3. ⏳ Create library pages (artists, albums, tracks)
4. ⏳ Create playlists page
5. ⏳ Create downloads/queue page
6. ⏳ Create search page
7. ⏳ Create settings page

### Future Enhancements
- [ ] Add animations and transitions
- [ ] Implement toast notifications
- [ ] Add modal dialogs
- [ ] Create table component
- [ ] Add filter panels
- [ ] Implement drag-and-drop
- [ ] Add keyboard shortcuts
- [ ] Optimize for mobile

## Differences from Old UI

| Feature | Old UI | New UI |
|---------|--------|--------|
| **Theme** | Glassmorphism | Solid dark cards |
| **Accent** | Red (#fe4155) | Red (#fe4155) ✓ |
| **Layout** | Various | Consistent sidebar |
| **Cards** | Glass effects | Solid backgrounds |
| **Navigation** | Top/mixed | Fixed sidebar |
| **Grid** | Custom | Responsive grid system |

## Integration with Backend

The new UI uses the same backend API endpoints as the old UI. To use the new UI:

1. Update your route to use the new templates:
```python
@router.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "new-ui/pages/dashboard.html",  # Use new UI
        {"request": request, "stats": get_stats()}
    )
```

2. Ensure static files are served correctly:
```python
app.mount("/static", StaticFiles(directory="src/soulspot/static"), name="static")
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Credits

- **Design Inspiration**: [MediaManager](https://github.com/maxdorninger/MediaManager)
- **Icons**: [Font Awesome 6](https://fontawesome.com/)
- **Dynamic Updates**: [HTMX](https://htmx.org/)

---

**Status**: In Development  
**Last Updated**: 2025-11-26  
**Version**: 1.0.0-alpha
