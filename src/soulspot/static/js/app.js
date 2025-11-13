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
// Main Application Initialization
// =============================================================================
document.addEventListener('DOMContentLoaded', function() {
    // Initialize keyboard navigation
    KeyboardNav.init();

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
