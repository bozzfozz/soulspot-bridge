---
applyTo: "src/soulspot/templates/**/*.html,src/soulspot/static/**/*.{js,css}"
---

# Frontend Instructions

## Technology Stack
- **Templating**: Jinja2 (server-rendered HTML)
- **Interactivity**: HTMX for dynamic content
- **Styling**: Custom CSS with CSS variables (design system in `/static/new-ui/css/main.css`)
- **Icons**: Font Awesome 6.4

## Template Structure

### Base Template
All pages extend `base.html`:
```html
{% extends "base.html" %}

{% block title %}Page Title - SoulSpot{% endblock %}

{% block content %}
    <h1>Page Content</h1>
{% endblock %}
```

### Partials
Reusable components go in `templates/partials/`. Use `{% include %}`:
```html
{% include "partials/track_card.html" %}
```

## HTMX Patterns

### Loading Content
```html
<div hx-get="/api/tracks" 
     hx-trigger="load"
     hx-swap="innerHTML">
    Loading...
</div>
```

### Form Submission
```html
<form hx-post="/api/playlists" 
      hx-swap="outerHTML"
      hx-target="#playlist-list">
    <input type="text" name="name" required>
    <button type="submit">Create</button>
</form>
```

### Polling for Updates
```html
<div hx-get="/api/status" 
     hx-trigger="every 30s"
     hx-swap="innerHTML">
    <!-- Status updates automatically -->
</div>
```

## Design System

### CSS Variables (from main.css)
```css
--bg-primary: #0f0f0f;
--bg-secondary: #1a1a1a;
--accent-color: #fe4155;
--text-primary: #ffffff;
--text-secondary: #8a8a8a;
--border-primary: #2a2a2a;
--space-4: 1rem;
```

### Button Styles
```html
<button class="btn btn-primary">Primary Action</button>
<button class="btn btn-secondary">Secondary</button>
<button class="btn-icon"><i class="fas fa-play"></i></button>
```

### Layout
```html
<div class="app-layout">
    {% include "includes/sidebar.html" %}
    <main class="app-main">
        <!-- Page content -->
    </main>
</div>
```

## Accessibility
- Use semantic HTML (`<nav>`, `<main>`, `<article>`)
- Provide `alt` text for images
- Ensure keyboard navigation works
- Use ARIA labels where needed:
```html
<button aria-label="Play track" class="btn-icon">
    <i class="fas fa-play"></i>
</button>
```

## Template Comments
Use Jinja2 comments for future-self notes:
```html
{# Hey future me - this banner polls the token status every 30 seconds.
   If needs_reauth=true, it shows a warning for the user to re-authenticate.
   Without this, background sync fails silently! #}
```

## Mobile Responsiveness
The design is mobile-first. Use CSS media queries for desktop enhancements.
Mobile sidebar is hidden by default; toggle with JavaScript.

## PWA Support
The app supports PWA installation. Manifest is at `/static/manifest.json`.
Icons are in `/static/icons/`.
