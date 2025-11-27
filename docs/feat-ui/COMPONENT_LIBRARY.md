# SoulSpot UI - Component Library

## Document Information
- **Version**: 1.0
- **Last Updated**: 2025-11-26
- **Status**: Draft
- **Related**: [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md), [TECHNICAL_SPEC.md](./TECHNICAL_SPEC.md)

---

## Introduction

This document provides a comprehensive reference for all UI components in the SoulSpot redesign. Each component includes:
- Purpose and usage
- Props/parameters
- HTML structure
- CSS classes
- JavaScript behavior (if applicable)
- Accessibility considerations
- Examples

---

## Table of Contents

### Layout Components
1. [Sidebar](#sidebar)
2. [TopBar](#topbar)
3. [PageHeader](#pageheader)
4. [Container](#container)

### Navigation Components
5. [Breadcrumbs](#breadcrumbs)
6. [Tabs](#tabs)
7. [Pagination](#pagination)

### Data Display Components
8. [Card](#card)
9. [Table](#table)
10. [Grid](#grid)
11. [List](#list)
12. [Badge](#badge)

### Input Components
13. [Button](#button)
14. [Input](#input)
15. [Select](#select)
16. [Checkbox](#checkbox)
17. [Radio](#radio)
18. [FilterPanel](#filterpanel)
19. [SearchBar](#searchbar)

### Feedback Components
20. [Alert](#alert)
21. [Toast](#toast)
22. [Modal](#modal)
23. [Loading](#loading)
24. [ProgressBar](#progressbar)

### Specialized Components
25. [LibraryView](#libraryview)
26. [QueueManager](#queuemanager)
27. [ActivityFeed](#activityfeed)
28. [AlbumArt](#albumart)

---

## Layout Components

### Sidebar

**Purpose**: Main navigation sidebar with collapsible sections

**Location**: `templates/components/layout/Sidebar.html`

**Props**:
```python
{
  'active_section': str,  # Currently active section
  'collapsed': bool,      # Sidebar collapsed state
  'user': dict           # User data
}
```

**HTML Structure**:
```html
<aside class="sidebar" data-collapsed="false">
  <!-- Logo -->
  <div class="sidebar-header">
    <a href="/" class="sidebar-logo">
      <i class="fa-solid fa-music"></i>
      <span class="sidebar-logo-text">SoulSpot</span>
    </a>
    <button class="sidebar-toggle" aria-label="Toggle sidebar">
      <i class="fa-solid fa-bars"></i>
    </button>
  </div>

  <!-- Navigation -->
  <nav class="sidebar-nav">
    <a href="/dashboard" class="sidebar-item active">
      <i class="fa-solid fa-home"></i>
      <span>Dashboard</span>
    </a>
    
    <div class="sidebar-section">
      <div class="sidebar-section-title">Library</div>
      <a href="/library/artists" class="sidebar-item">
        <i class="fa-solid fa-user-music"></i>
        <span>Artists</span>
      </a>
      <a href="/library/albums" class="sidebar-item">
        <i class="fa-solid fa-compact-disc"></i>
        <span>Albums</span>
      </a>
      <a href="/library/tracks" class="sidebar-item">
        <i class="fa-solid fa-music"></i>
        <span>Tracks</span>
      </a>
    </div>

    <a href="/playlists" class="sidebar-item">
      <i class="fa-solid fa-list"></i>
      <span>Playlists</span>
    </a>

    <a href="/downloads" class="sidebar-item">
      <i class="fa-solid fa-download"></i>
      <span>Downloads</span>
      <span class="sidebar-badge">3</span>
    </a>

    <a href="/search" class="sidebar-item">
      <i class="fa-solid fa-search"></i>
      <span>Search</span>
    </a>
  </nav>

  <!-- Footer -->
  <div class="sidebar-footer">
    <a href="/settings" class="sidebar-item">
      <i class="fa-solid fa-cog"></i>
      <span>Settings</span>
    </a>
    
    <div class="sidebar-user">
      <img src="{{ user.avatar }}" alt="{{ user.name }}" class="sidebar-user-avatar">
      <div class="sidebar-user-info">
        <div class="sidebar-user-name">{{ user.name }}</div>
        <div class="sidebar-user-status">Online</div>
      </div>
    </div>
  </div>
</aside>
```

**CSS Classes**:
```css
.sidebar {
  width: 280px;
  height: 100vh;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-normal);
}

.sidebar[data-collapsed="true"] {
  width: 80px;
}

.sidebar-header {
  padding: var(--space-lg);
  border-bottom: 1px solid var(--color-border);
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
  text-decoration: none;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-md);
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  text-decoration: none;
  transition: all var(--transition-fast);
}

.sidebar-item:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}

.sidebar-item.active {
  background: var(--color-primary);
  color: white;
}

.sidebar-section {
  margin: var(--space-md) 0;
}

.sidebar-section-title {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: var(--space-sm) var(--space-md);
}

.sidebar-badge {
  margin-left: auto;
  background: var(--color-primary);
  color: white;
  font-size: var(--font-size-xs);
  padding: 2px 6px;
  border-radius: var(--radius-full);
}

.sidebar-footer {
  border-top: 1px solid var(--color-border);
  padding: var(--space-md);
}

.sidebar-user {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm);
  border-radius: var(--radius-md);
  background: var(--color-surface-alt);
}

.sidebar-user-avatar {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
}

.sidebar-user-name {
  font-weight: var(--font-weight-medium);
  color: var(--color-text);
}

.sidebar-user-status {
  font-size: var(--font-size-xs);
  color: var(--color-success);
}
```

**JavaScript Behavior**:
```javascript
// Toggle sidebar
document.querySelector('.sidebar-toggle').addEventListener('click', () => {
  const sidebar = document.querySelector('.sidebar');
  const isCollapsed = sidebar.dataset.collapsed === 'true';
  sidebar.dataset.collapsed = !isCollapsed;
  
  // Save state
  localStorage.setItem('sidebarCollapsed', !isCollapsed);
});

// Restore state on load
const savedState = localStorage.getItem('sidebarCollapsed');
if (savedState === 'true') {
  document.querySelector('.sidebar').dataset.collapsed = 'true';
}
```

**Accessibility**:
- Semantic `<nav>` element
- ARIA labels for toggle button
- Keyboard navigation support
- Focus indicators on all items

---

### TopBar

**Purpose**: Top navigation bar with search and user menu

**Location**: `templates/components/layout/TopBar.html`

**Props**:
```python
{
  'page_title': str,     # Current page title
  'show_search': bool,   # Show search bar
  'user': dict          # User data
}
```

**HTML Structure**:
```html
<header class="topbar">
  <div class="topbar-left">
    <button class="topbar-menu-toggle" aria-label="Toggle menu">
      <i class="fa-solid fa-bars"></i>
    </button>
    
    <div class="topbar-breadcrumbs">
      <a href="/">Home</a>
      <i class="fa-solid fa-chevron-right"></i>
      <span>{{ page_title }}</span>
    </div>
  </div>

  <div class="topbar-center">
    {% if show_search %}
    <div class="topbar-search">
      <i class="fa-solid fa-search"></i>
      <input type="text" placeholder="Search..." class="topbar-search-input">
      <kbd class="topbar-search-shortcut">Ctrl+K</kbd>
    </div>
    {% endif %}
  </div>

  <div class="topbar-right">
    <button class="topbar-icon-btn" aria-label="Notifications">
      <i class="fa-solid fa-bell"></i>
      <span class="topbar-badge">3</span>
    </button>

    <button class="topbar-icon-btn" aria-label="Toggle theme">
      <i class="fa-solid fa-moon"></i>
    </button>

    <div class="topbar-user-menu">
      <button class="topbar-user-btn">
        <img src="{{ user.avatar }}" alt="{{ user.name }}">
        <span>{{ user.name }}</span>
        <i class="fa-solid fa-chevron-down"></i>
      </button>
      
      <div class="topbar-user-dropdown">
        <a href="/profile">Profile</a>
        <a href="/settings">Settings</a>
        <hr>
        <a href="/logout">Logout</a>
      </div>
    </div>
  </div>
</header>
```

**CSS Classes**:
```css
.topbar {
  height: 64px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-lg);
  gap: var(--space-lg);
}

.topbar-left,
.topbar-center,
.topbar-right {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.topbar-center {
  flex: 1;
  max-width: 600px;
}

.topbar-search {
  position: relative;
  width: 100%;
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  background: var(--color-surface-alt);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-sm) var(--space-md);
}

.topbar-search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--color-text);
}

.topbar-search-shortcut {
  font-size: var(--font-size-xs);
  padding: 2px 6px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
}

.topbar-icon-btn {
  position: relative;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.topbar-icon-btn:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}

.topbar-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  background: var(--color-primary);
  color: white;
  font-size: 10px;
  padding: 2px 4px;
  border-radius: var(--radius-full);
  min-width: 16px;
  text-align: center;
}
```

---

## Data Display Components

### Card

**Purpose**: Reusable card component for displaying content

**Location**: `templates/components/data-display/Card.html`

**Props**:
```python
{
  'title': str,          # Card title
  'image': str,          # Image URL
  'metadata': dict,      # Additional metadata
  'actions': list,       # Action buttons
  'status': str,         # Status badge
  'variant': str         # 'default' | 'glass' | 'hover'
}
```

**HTML Structure**:
```html
<div class="card {% if variant == 'glass' %}card-glass{% endif %} {% if variant == 'hover' %}card-hover{% endif %}">
  {% if image %}
  <div class="card-image">
    <img src="{{ image }}" alt="{{ title }}">
    {% if status %}
    <span class="card-status badge badge-{{ status }}">{{ status }}</span>
    {% endif %}
  </div>
  {% endif %}

  <div class="card-content">
    {% if title %}
    <h3 class="card-title">{{ title }}</h3>
    {% endif %}

    {% if metadata %}
    <div class="card-metadata">
      {% for key, value in metadata.items() %}
      <div class="card-meta-item">
        <span class="card-meta-label">{{ key }}:</span>
        <span class="card-meta-value">{{ value }}</span>
      </div>
      {% endfor %}
    </div>
    {% endif %}
  </div>

  {% if actions %}
  <div class="card-actions">
    {% for action in actions %}
    <button class="btn btn-{{ action.variant or 'primary' }}">
      {% if action.icon %}<i class="{{ action.icon }}"></i>{% endif %}
      {{ action.label }}
    </button>
    {% endfor %}
  </div>
  {% endif %}
</div>
```

**Variants**:

**Album Card**:
```html
<div class="card card-album card-hover">
  <div class="card-image">
    <img src="{{ album.cover_url }}" alt="{{ album.name }}">
    <div class="card-overlay">
      <button class="btn btn-primary btn-icon">
        <i class="fa-solid fa-play"></i>
      </button>
    </div>
  </div>
  <div class="card-content">
    <h3 class="card-title">{{ album.name }}</h3>
    <p class="card-subtitle">{{ album.artist }}</p>
    <div class="card-metadata">
      <span>{{ album.year }}</span>
      <span>{{ album.track_count }} tracks</span>
    </div>
  </div>
</div>
```

**Artist Card**:
```html
<div class="card card-artist card-hover">
  <div class="card-image card-image-circle">
    <img src="{{ artist.image_url }}" alt="{{ artist.name }}">
  </div>
  <div class="card-content text-center">
    <h3 class="card-title">{{ artist.name }}</h3>
    <p class="card-subtitle">{{ artist.genre }}</p>
    <div class="card-stats">
      <div class="card-stat">
        <span class="card-stat-value">{{ artist.album_count }}</span>
        <span class="card-stat-label">Albums</span>
      </div>
      <div class="card-stat">
        <span class="card-stat-value">{{ artist.track_count }}</span>
        <span class="card-stat-label">Tracks</span>
      </div>
    </div>
  </div>
</div>
```

---

## Specialized Components

### LibraryView

**Purpose**: Unified library view with multiple display modes

**Location**: `templates/components/specialized/LibraryView.html`

**Props**:
```python
{
  'items': list,         # Items to display
  'view_mode': str,      # 'grid' | 'list' | 'table'
  'filters': dict,       # Active filters
  'sort': dict,          # Sort configuration
  'total': int,          # Total item count
  'page': int,           # Current page
  'per_page': int        # Items per page
}
```

**HTML Structure**:
```html
<div class="library-view">
  <!-- Header -->
  <div class="library-header">
    <div class="library-title">
      <h1>{{ title }}</h1>
      <span class="library-count">{{ total }} items</span>
    </div>

    <div class="library-controls">
      <!-- View Mode Toggle -->
      <div class="view-toggle">
        <button class="view-toggle-btn {% if view_mode == 'grid' %}active{% endif %}" 
                data-view="grid" aria-label="Grid view">
          <i class="fa-solid fa-grid"></i>
        </button>
        <button class="view-toggle-btn {% if view_mode == 'list' %}active{% endif %}" 
                data-view="list" aria-label="List view">
          <i class="fa-solid fa-list"></i>
        </button>
        <button class="view-toggle-btn {% if view_mode == 'table' %}active{% endif %}" 
                data-view="table" aria-label="Table view">
          <i class="fa-solid fa-table"></i>
        </button>
      </div>

      <!-- Sort -->
      <div class="library-sort">
        <select class="form-select" name="sort">
          <option value="name">Name</option>
          <option value="date">Date Added</option>
          <option value="artist">Artist</option>
          <option value="year">Year</option>
        </select>
      </div>

      <!-- Filter Toggle -->
      <button class="btn btn-outline" id="filter-toggle">
        <i class="fa-solid fa-filter"></i>
        Filters
        {% if filters|length > 0 %}
        <span class="badge badge-primary">{{ filters|length }}</span>
        {% endif %}
      </button>
    </div>
  </div>

  <!-- Content -->
  <div class="library-content">
    <!-- Filter Panel (Sidebar) -->
    <aside class="library-filters" id="filter-panel">
      {% include 'components/specialized/FilterPanel.html' %}
    </aside>

    <!-- Items -->
    <div class="library-items">
      {% if view_mode == 'grid' %}
      <div class="library-grid">
        {% for item in items %}
        {% include 'components/data-display/Card.html' with item %}
        {% endfor %}
      </div>
      {% elif view_mode == 'list' %}
      <div class="library-list">
        {% for item in items %}
        {% include 'components/data-display/ListItem.html' with item %}
        {% endfor %}
      </div>
      {% elif view_mode == 'table' %}
      <div class="library-table">
        {% include 'components/data-display/Table.html' with items %}
      </div>
      {% endif %}

      <!-- Pagination -->
      {% if total > per_page %}
      <div class="library-pagination">
        {% include 'components/navigation/Pagination.html' %}
      </div>
      {% endif %}
    </div>
  </div>
</div>
```

**CSS Classes**:
```css
.library-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  height: 100%;
}

.library-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-lg);
}

.library-title {
  display: flex;
  align-items: baseline;
  gap: var(--space-sm);
}

.library-count {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.library-controls {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.view-toggle {
  display: flex;
  gap: var(--space-xs);
  background: var(--color-surface-alt);
  border-radius: var(--radius-md);
  padding: var(--space-xs);
}

.view-toggle-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.view-toggle-btn:hover {
  color: var(--color-text);
}

.view-toggle-btn.active {
  background: var(--color-primary);
  color: white;
}

.library-content {
  display: flex;
  gap: var(--space-lg);
  flex: 1;
  overflow: hidden;
}

.library-filters {
  width: 280px;
  flex-shrink: 0;
  overflow-y: auto;
}

.library-items {
  flex: 1;
  overflow-y: auto;
}

.library-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--space-lg);
}

.library-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}
```

**JavaScript Behavior**:
```javascript
// View mode toggle
document.querySelectorAll('.view-toggle-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const viewMode = btn.dataset.view;
    
    // Update active state
    document.querySelectorAll('.view-toggle-btn').forEach(b => {
      b.classList.remove('active');
    });
    btn.classList.add('active');
    
    // Save preference
    localStorage.setItem('libraryViewMode', viewMode);
    
    // Update view (HTMX or page reload)
    htmx.ajax('GET', `/library?view=${viewMode}`, {
      target: '.library-items',
      swap: 'innerHTML'
    });
  });
});

// Filter toggle
document.getElementById('filter-toggle').addEventListener('click', () => {
  const panel = document.getElementById('filter-panel');
  panel.classList.toggle('hidden');
});
```

---

### QueueManager

**Purpose**: Download queue management interface

**Location**: `templates/components/specialized/QueueManager.html`

**Props**:
```python
{
  'queue_items': list,       # Queue items
  'active_downloads': int,   # Active download count
  'max_concurrent': int      # Max concurrent downloads
}
```

**HTML Structure**:
```html
<div class="queue-manager">
  <!-- Header -->
  <div class="queue-header">
    <div class="queue-stats">
      <div class="queue-stat">
        <span class="queue-stat-value">{{ active_downloads }}</span>
        <span class="queue-stat-label">Active</span>
      </div>
      <div class="queue-stat">
        <span class="queue-stat-value">{{ queue_items|length }}</span>
        <span class="queue-stat-label">In Queue</span>
      </div>
    </div>

    <div class="queue-actions">
      <button class="btn btn-outline" id="pause-all">
        <i class="fa-solid fa-pause"></i>
        Pause All
      </button>
      <button class="btn btn-outline" id="clear-completed">
        <i class="fa-solid fa-check"></i>
        Clear Completed
      </button>
    </div>
  </div>

  <!-- Queue Items -->
  <div class="queue-items" id="queue-items">
    {% for item in queue_items %}
    <div class="queue-item" data-id="{{ item.id }}" data-status="{{ item.status }}">
      <div class="queue-item-info">
        <img src="{{ item.album_art }}" alt="{{ item.title }}" class="queue-item-image">
        <div class="queue-item-details">
          <div class="queue-item-title">{{ item.title }}</div>
          <div class="queue-item-artist">{{ item.artist }}</div>
        </div>
      </div>

      <div class="queue-item-progress">
        <div class="progress-bar">
          <div class="progress-bar-fill" style="width: {{ item.progress }}%"></div>
        </div>
        <div class="progress-text">{{ item.progress }}%</div>
      </div>

      <div class="queue-item-status">
        <span class="badge badge-{{ item.status }}">{{ item.status }}</span>
      </div>

      <div class="queue-item-actions">
        {% if item.status == 'active' %}
        <button class="btn-icon" data-action="pause">
          <i class="fa-solid fa-pause"></i>
        </button>
        {% elif item.status == 'paused' %}
        <button class="btn-icon" data-action="resume">
          <i class="fa-solid fa-play"></i>
        </button>
        {% elif item.status == 'failed' %}
        <button class="btn-icon" data-action="retry">
          <i class="fa-solid fa-rotate"></i>
        </button>
        {% endif %}
        <button class="btn-icon" data-action="cancel">
          <i class="fa-solid fa-times"></i>
        </button>
      </div>
    </div>
    {% endfor %}
  </div>
</div>
```

**Real-Time Updates (SSE)**:
```javascript
// Connect to SSE endpoint
const eventSource = new EventSource('/api/downloads/stream');

eventSource.addEventListener('download_progress', (event) => {
  const data = JSON.parse(event.data);
  updateQueueItem(data.id, data.progress, data.status);
});

function updateQueueItem(id, progress, status) {
  const item = document.querySelector(`[data-id="${id}"]`);
  if (!item) return;

  // Update progress bar
  const progressBar = item.querySelector('.progress-bar-fill');
  progressBar.style.width = `${progress}%`;

  // Update progress text
  const progressText = item.querySelector('.progress-text');
  progressText.textContent = `${progress}%`;

  // Update status badge
  const statusBadge = item.querySelector('.badge');
  statusBadge.className = `badge badge-${status}`;
  statusBadge.textContent = status;
}
```

---

## Usage Examples

### Complete Page Example

```html
{% extends "base.html" %}

{% block title %}Library - Artists{% endblock %}

{% block content %}
<div class="page-container">
  <!-- Page Header -->
  {% include 'components/layout/PageHeader.html' with {
    'title': 'Artists',
    'subtitle': 'Browse your music library',
    'actions': [
      {'label': 'Add Artist', 'icon': 'fa-solid fa-plus', 'variant': 'primary'}
    ]
  } %}

  <!-- Library View -->
  {% include 'components/specialized/LibraryView.html' with {
    'items': artists,
    'view_mode': view_mode,
    'filters': filters,
    'sort': sort,
    'total': total,
    'page': page,
    'per_page': per_page
  } %}
</div>
{% endblock %}
```

---

## Best Practices

### 1. **Component Reusability**
- Keep components generic and configurable
- Use props for customization
- Avoid hardcoding values

### 2. **Accessibility**
- Use semantic HTML
- Provide ARIA labels
- Ensure keyboard navigation
- Maintain focus management

### 3. **Performance**
- Lazy-load images
- Use virtual scrolling for long lists
- Minimize re-renders
- Optimize CSS selectors

### 4. **Consistency**
- Follow design system guidelines
- Use standard spacing and colors
- Maintain consistent naming conventions

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-26  
**Status**: Draft - Awaiting Approval
