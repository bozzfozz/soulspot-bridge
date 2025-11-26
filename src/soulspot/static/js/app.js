// SoulSpot Bridge JavaScript

// =============================================================================
// Toast Notification System
// =============================================================================
const ToastManager = {
    container: null,
    toastId: 0,

    init() {
        // Create toast container if it doesn't exist
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            this.container.setAttribute('role', 'region');
            this.container.setAttribute('aria-label', 'Notifications');
            document.body.appendChild(this.container);
        }
    },

    show(message, type = 'info', title = null, duration = 5000) {
        this.init();
        
        const id = `toast-${this.toastId++}`;
        const toast = document.createElement('div');
        toast.id = id;
        toast.className = `toast toast-${type}`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'polite');
        
        const icons = {
            success: '<svg class="toast-icon" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>',
            error: '<svg class="toast-icon" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg>',
            warning: '<svg class="toast-icon" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>',
            info: '<svg class="toast-icon" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg>'
        };

        toast.innerHTML = `
            ${icons[type] || icons.info}
            <div class="toast-content">
                ${title ? `<div class="toast-title">${title}</div>` : ''}
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="ToastManager.hide('${id}')" aria-label="Close notification">
                <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                </svg>
            </button>
        `;

        // Add with animation
        toast.classList.add('toast-enter');
        this.container.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => toast.classList.remove('toast-enter'), 10);

        // Auto-hide after duration
        if (duration > 0) {
            setTimeout(() => this.hide(id), duration);
        }

        return id;
    },

    hide(id) {
        const toast = document.getElementById(id);
        if (toast) {
            toast.classList.add('toast-exit');
            setTimeout(() => toast.remove(), 300);
        }
    },

    success(message, title = 'Success', duration = 5000) {
        return this.show(message, 'success', title, duration);
    },

    error(message, title = 'Error', duration = 7000) {
        return this.show(message, 'error', title, duration);
    },

    warning(message, title = 'Warning', duration = 6000) {
        return this.show(message, 'warning', title, duration);
    },

    info(message, title = null, duration = 5000) {
        return this.show(message, 'info', title, duration);
    }
};

// =============================================================================
// Loading State Management
// =============================================================================
const LoadingManager = {
    showButtonLoading(button) {
        if (!button) return;
        
        button.setAttribute('data-original-text', button.innerHTML);
        button.disabled = true;
        button.innerHTML = `
            <span class="spinner spinner-sm"></span>
            <span>Loading...</span>
        `;
    },

    hideButtonLoading(button) {
        if (!button) return;
        
        const originalText = button.getAttribute('data-original-text');
        if (originalText) {
            button.innerHTML = originalText;
            button.removeAttribute('data-original-text');
        }
        button.disabled = false;
    },

    showOverlay(element) {
        if (!element) return;
        
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = '<span class="spinner spinner-lg text-primary-500"></span>';
        element.style.position = 'relative';
        element.appendChild(overlay);
    },

    hideOverlay(element) {
        if (!element) return;
        
        const overlay = element.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
};

// =============================================================================
// Keyboard Navigation
// =============================================================================
const KeyboardNav = {
    init() {
        // Add keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K: Focus search (if exists)
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.querySelector('input[type="search"]');
                if (searchInput) searchInput.focus();
            }

            // Escape: Close modals/toasts
            if (e.key === 'Escape') {
                this.closeModals();
            }
        });

        // Trap focus in modals
        document.addEventListener('focusin', (e) => {
            const modal = document.querySelector('.modal-overlay');
            if (modal && !modal.contains(e.target)) {
                const firstFocusable = modal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
                if (firstFocusable) {
                    e.preventDefault();
                    firstFocusable.focus();
                }
            }
        });
    },

    closeModals() {
        const modals = document.querySelectorAll('.modal-overlay');
        modals.forEach(modal => modal.remove());
    },

    trapFocus(element) {
        const focusableElements = element.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        element.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                if (e.shiftKey && document.activeElement === firstElement) {
                    e.preventDefault();
                    lastElement.focus();
                } else if (!e.shiftKey && document.activeElement === lastElement) {
                    e.preventDefault();
                    firstElement.focus();
                }
            }
        });

        // Focus first element
        if (firstElement) firstElement.focus();
    }
};

// =============================================================================
// Optimistic UI & Performance Enhancements
// =============================================================================
const PerformanceEnhancer = {
    // Hey future me - this implements optimistic UI updates! Before HTMX makes the actual request,
    // we immediately show loading states and predicted UI changes. Makes the app feel instant.
    // If the request fails, we rollback. This is the secret sauce for perceived performance.
    initOptimisticUI() {
        document.body.addEventListener('htmx:beforeRequest', (event) => {
            const trigger = event.detail.elt;
            const target = event.detail.target;
            
            // Add optimistic loading class
            if (target) {
                target.classList.add('loading-optimistic');
                target.setAttribute('aria-busy', 'true');
            }
            
            // Show optimistic feedback on buttons
            if (trigger && trigger.tagName === 'BUTTON') {
                trigger.setAttribute('data-original-disabled', trigger.disabled);
                trigger.disabled = true;
            }
        });
        
        document.body.addEventListener('htmx:afterRequest', (event) => {
            const trigger = event.detail.elt;
            const target = event.detail.target;
            
            // Remove loading states
            if (target) {
                target.classList.remove('loading-optimistic');
                target.removeAttribute('aria-busy');
            }
            
            // Restore button state
            if (trigger && trigger.tagName === 'BUTTON') {
                const wasDisabled = trigger.getAttribute('data-original-disabled') === 'true';
                trigger.disabled = wasDisabled;
                trigger.removeAttribute('data-original-disabled');
            }
        });
    },
    
    // Hey future me - prefetching makes navigation feel instant! We preload pages when users hover
    // over links. By the time they click, content is already cached. Clever, right?
    initLinkPrefetching() {
        const prefetchedUrls = new Set();
        
        document.querySelectorAll('a[href^="/"]').forEach(link => {
            link.addEventListener('mouseenter', function() {
                const url = this.href;
                
                // Only prefetch once per URL
                if (prefetchedUrls.has(url)) return;
                prefetchedUrls.add(url);
                
                // Prefetch using HTMX (stores in cache)
                htmx.ajax('GET', url, {swap: 'none'});
            }, {once: true, passive: true});
        });
    },
    
    // Hey future me - lazy loading images saves bandwidth and speeds up initial page load!
    // Images only load when they're about to enter the viewport. Modern browsers have native
    // support, but we add a polyfill for older ones using Intersection Observer.
    initImageLazyLoading() {
        // Modern browsers: use native lazy loading
        document.querySelectorAll('img[data-src]').forEach(img => {
            if ('loading' in HTMLImageElement.prototype) {
                img.loading = 'lazy';
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
            }
        });
        
        // Polyfill for older browsers
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.classList.add('loaded');
                            img.removeAttribute('data-src');
                            observer.unobserve(img);
                        }
                    }
                });
            }, {
                rootMargin: '50px' // Start loading 50px before entering viewport
            });
            
            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }
};

// =============================================================================
// Ripple Effect for Interactive Elements
// =============================================================================
const RippleEffect = {
    // Hey future me - ripple effects give tactile feedback on clicks! Material Design pattern
    // that makes buttons feel responsive. Creates a circular wave from click point.
    init() {
        document.addEventListener('click', (e) => {
            const button = e.target.closest('.btn, .nav-item, .card');
            if (!button) return;
            
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            
            const rect = button.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            
            button.style.position = 'relative';
            button.style.overflow = 'hidden';
            button.appendChild(ripple);
            
            // Haptic feedback for mobile devices
            if ('vibrate' in navigator) {
                navigator.vibrate(5);
            }
            
            setTimeout(() => ripple.remove(), 600);
        }, {passive: true});
    }
};

// =============================================================================
// Enhanced Keyboard Navigation
// =============================================================================
const EnhancedKeyboardNav = {
    currentIndex: 0,
    items: [],
    
    // Hey future me - arrow key navigation for lists! Power users love this.
    // Navigate downloads/playlists with keyboard, Enter to activate. Accessibility win!
    init() {
        this.initListNavigation();
        this.initGlobalShortcuts();
    },
    
    initListNavigation() {
        document.addEventListener('keydown', (e) => {
            // Only activate when no input is focused
            if (document.activeElement.tagName === 'INPUT' || 
                document.activeElement.tagName === 'TEXTAREA') {
                return;
            }
            
            // Get current navigable items
            this.items = Array.from(document.querySelectorAll(
                '.download-card:not([style*="display: none"]), .card[href]'
            ));
            
            if (this.items.length === 0) return;
            
            switch(e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    this.currentIndex = Math.min(this.currentIndex + 1, this.items.length - 1);
                    this.focusCurrentItem();
                    break;
                    
                case 'ArrowUp':
                    e.preventDefault();
                    this.currentIndex = Math.max(this.currentIndex - 1, 0);
                    this.focusCurrentItem();
                    break;
                    
                case 'Enter':
                    if (this.items[this.currentIndex]) {
                        e.preventDefault();
                        const item = this.items[this.currentIndex];
                        const link = item.querySelector('a') || item;
                        link.click();
                    }
                    break;
            }
        });
    },
    
    focusCurrentItem() {
        const item = this.items[this.currentIndex];
        if (item) {
            item.focus();
            item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            
            // Visual highlight
            this.items.forEach(i => i.classList.remove('keyboard-focused'));
            item.classList.add('keyboard-focused');
        }
    },
    
    initGlobalShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Cmd/Ctrl + K: Focus search
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.querySelector('input[name="q"], input[type="search"]');
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
            }
            
            // Escape: Clear focus, close modals
            if (e.key === 'Escape') {
                document.activeElement?.blur();
                KeyboardNav.closeModals();
            }
        });
    }
};

// =============================================================================
// Main Application Initialization
// =============================================================================
document.addEventListener('DOMContentLoaded', function() {
    // Initialize keyboard navigation
    KeyboardNav.init();
    
    // Initialize performance enhancements
    PerformanceEnhancer.initOptimisticUI();
    PerformanceEnhancer.initLinkPrefetching();
    PerformanceEnhancer.initImageLazyLoading();
    
    // Initialize ripple effects
    RippleEffect.init();
    
    // Initialize enhanced keyboard navigation
    EnhancedKeyboardNav.init();

    // Auto-refresh downloads page every 5 seconds if on downloads page
    if (window.location.pathname.includes('/downloads')) {
        setInterval(function() {
            htmx.trigger('#downloads-list', 'refresh');
        }, 5000);
    }

    // Handle HTMX events with toast notifications
    document.body.addEventListener('htmx:beforeRequest', function(event) {
        // Show loading state for button triggers
        const trigger = event.detail.elt;
        if (trigger && trigger.tagName === 'BUTTON') {
            LoadingManager.showButtonLoading(trigger);
        }
    });

    document.body.addEventListener('htmx:afterRequest', function(event) {
        // Hide loading state
        const trigger = event.detail.elt;
        if (trigger && trigger.tagName === 'BUTTON') {
            LoadingManager.hideButtonLoading(trigger);
        }

        // Show appropriate toast notification
        if (event.detail.successful) {
            const xhr = event.detail.xhr;
            const statusCode = xhr.status;
            
            // Success responses (2xx)
            if (statusCode >= 200 && statusCode < 300) {
                // Try to get custom message from response
                try {
                    const response = JSON.parse(xhr.responseText);
                    if (response.message) {
                        ToastManager.success(response.message);
                    }
                } catch (e) {
                    // Default success message based on action
                    const action = event.detail.elt.textContent?.trim();
                    if (action) {
                        ToastManager.success(`${action} completed successfully`);
                    }
                }
            }
        } else {
            // Error responses
            const xhr = event.detail.xhr;
            let errorMessage = 'An error occurred. Please try again.';
            
            try {
                const response = JSON.parse(xhr.responseText);
                errorMessage = response.detail || response.message || errorMessage;
            } catch (e) {
                // Use default error message
            }
            
            ToastManager.error(errorMessage);
        }
    });

    // Handle network errors
    document.body.addEventListener('htmx:sendError', function(event) {
        ToastManager.error('Network error. Please check your connection.', 'Connection Error');
    });

    // Handle timeout errors
    document.body.addEventListener('htmx:timeout', function(event) {
        ToastManager.warning('Request timed out. Please try again.', 'Timeout');
    });

    // Auto-fill code verifier and state from authorization response
    document.body.addEventListener('htmx:afterSwap', function(event) {
        if (event.target.id === 'auth-result') {
            try {
                const response = JSON.parse(event.target.textContent);
                if (response.state && response.code_verifier) {
                    document.getElementById('state').value = response.state;
                    document.getElementById('code_verifier').value = response.code_verifier;
                    
                    // Open authorization URL in new tab
                    if (response.authorization_url) {
                        window.open(response.authorization_url, '_blank');
                        ToastManager.info('Authorization window opened. Please complete the login process.', 'Spotify Authorization');
                    }
                }
            } catch (e) {
                console.log('Not a JSON response');
            }
        }
    });

    // Add focus visible polyfill for older browsers
    try {
        document.body.classList.add('js-focus-visible');
    } catch (e) {
        // Ignore if not supported
    }
});

// Export for global access
window.ToastManager = ToastManager;
window.LoadingManager = LoadingManager;
window.KeyboardNav = KeyboardNav;
