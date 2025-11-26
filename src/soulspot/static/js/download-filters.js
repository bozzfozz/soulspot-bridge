/**
 * Advanced Download Filtering System
 * 
 * Hey future me - this ties together FilterManager and FuzzySearch for the downloads page.
 * Provides multi-criteria filtering with live search. All filters are composable (AND logic).
 */

// Initialize Filter Manager
const filterManager = new FilterManager();
let fuzzySearch = null;
let allDownloads = [];

// Collect all download cards data
function initializeDownloads() {
    allDownloads = Array.from(document.querySelectorAll('.download-card')).map(card => ({
        element: card,
        id: card.dataset.downloadId,
        status: card.dataset.status,
        priority: parseInt(card.dataset.priority) || 0,
        progress: parseFloat(card.querySelector('[data-percent-text]')?.textContent) || 0,
        trackName: card.querySelector('h3')?.textContent || '',
        errorMessage: card.querySelector('.text-danger')?.textContent || ''
    }));
    
    // Initialize fuzzy search
    fuzzySearch = new FuzzySearch(allDownloads, {
        keys: ['trackName', 'status', 'errorMessage'],
        threshold: 0.2,
        limit: 100
    });
}

// Apply all filters
function applyFilters() {
    if (allDownloads.length === 0) {
        initializeDownloads();
    }
    
    const searchQuery = document.getElementById('fuzzy-search-input')?.value || '';
    let results = allDownloads;
    
    // Fuzzy search first
    if (searchQuery.trim()) {
        results = fuzzySearch.search(searchQuery).map(r => r.item);
    }
    
    // Then apply other filters
    results = filterManager.apply(results);
    
    // Show/hide cards
    allDownloads.forEach(download => {
        const isVisible = results.includes(download);
        download.element.style.display = isVisible ? '' : 'none';
    });
    
    // Update results count
    const count = results.length;
    const countEl = document.getElementById('search-results-count');
    if (countEl) {
        if (searchQuery.trim() || filterManager.getActiveCount() > 0) {
            countEl.textContent = `Showing ${count} of ${allDownloads.length} downloads`;
            countEl.style.display = 'block';
        } else {
            countEl.style.display = 'none';
        }
    }
    
    // Update active filters badge
    updateFiltersBadge();
}

// Debounce helper
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Status filter
function toggleFilter(btn) {
    const value = btn.dataset.value;
    
    // Update button states
    const buttons = btn.parentElement.querySelectorAll('.filter-btn');
    buttons.forEach(b => {
        b.classList.remove('bg-primary', 'text-white', 'shadow-md');
        b.classList.add('text-muted', 'hover:text-white', 'hover:bg-white/5');
    });
    btn.classList.remove('text-muted', 'hover:text-white', 'hover:bg-white/5');
    btn.classList.add('bg-primary', 'text-white', 'shadow-md');
    
    // Update filter
    if (value === 'all') {
        filterManager.removeFilter('status');
    } else {
        filterManager.addFilter('status', (item) => item.status === value);
    }
    
    applyFilters();
}

// Filter chips (priority, etc.)
function toggleFilterChip(btn) {
    const filterName = btn.dataset.filter;
    const value = btn.dataset.value;
    
    btn.classList.toggle('btn-primary');
    btn.classList.toggle('btn-secondary');
    
    const isActive = btn.classList.contains('btn-primary');
    
    if (isActive) {
        if (filterName === 'priority') {
            const priorityValue = parseInt(value);
            filterManager.addFilter(`priority-${value}`, (item) => item.priority === priorityValue);
        }
    } else {
        filterManager.removeFilter(`${filterName}-${value}`);
    }
    
    applyFilters();
}

// Progress filter
function updateProgressFilter(value) {
    const label = document.getElementById('progress-value');
    if (label) {
        label.textContent = `${value}-100%`;
    }
    
    if (value > 0) {
        filterManager.addFilter('progress', (item) => item.progress >= parseFloat(value));
    } else {
        filterManager.removeFilter('progress');
    }
    
    applyFilters();
}

// Advanced filters toggle
function toggleAdvancedFilters() {
    const panel = document.getElementById('advanced-filters');
    if (panel) {
        panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    }
}

// Clear all filters
function clearAllFilters() {
    filterManager.clearAll();
    
    const searchInput = document.getElementById('fuzzy-search-input');
    if (searchInput) searchInput.value = '';
    
    const progressFilter = document.getElementById('progress-filter');
    if (progressFilter) {
        progressFilter.value = 0;
        const label = document.getElementById('progress-value');
        if (label) label.textContent = '0-100%';
    }
    
    // Reset all filter chips
    document.querySelectorAll('.filter-chip').forEach(chip => {
        chip.classList.remove('btn-primary');
        chip.classList.add('btn-secondary');
    });
    
    // Reset status to "All"
    const allBtn = document.querySelector('[data-filter="status"][data-value="all"]');
    if (allBtn) toggleFilter(allBtn);
    
    applyFilters();
}

// Update filters badge count
function updateFiltersBadge() {
    const count = filterManager.getActiveCount();
    const badge = document.getElementById('active-filters-badge');
    if (badge) {
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'block';
        } else {
            badge.style.display = 'none';
        }
    }
}

// Auto-initialize on downloads page
if (window.location.pathname.includes('/downloads')) {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => {
            initializeDownloads();
            
            // Search input handler
            const searchInput = document.getElementById('fuzzy-search-input');
            if (searchInput) {
                searchInput.addEventListener('input', debounce(applyFilters, 300));
            }
        }, 100); // Wait for DOM to be fully ready
    });
}
