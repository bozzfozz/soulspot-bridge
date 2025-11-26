/**
 * Mobile Gestures & Touch Optimizations
 * 
 * Hey future me - this adds native-feeling swipe gestures for mobile! Swipe right to open
 * sidebar, swipe left to close, swipe down to refresh, swipe on cards for actions.
 * 
 * Touch events are tricky - need to track start position, movement, and velocity.
 * We differentiate between swipes (fast movement) and pans (slow drag).
 * preventDefault() carefully to not break scrolling!
 */

class SwipeDetector {
    constructor(element, callbacks = {}) {
        this.element = element;
        this.callbacks = {
            onSwipeLeft: callbacks.onSwipeLeft || null,
            onSwipeRight: callbacks.onSwipeRight || null,
            onSwipeUp: callbacks.onSwipeUp || null,
            onSwipeDown: callbacks.onSwipeDown || null,
            onTap: callbacks.onTap || null,
            onLongPress: callbacks.onLongPress || null
        };
        
        this.startX = 0;
        this.startY = 0;
        this.startTime = 0;
        this.isLongPress = false;
        this.longPressTimer = null;
        
        this.config = {
            swipeThreshold: 50,      // Minimum distance for swipe
            swipeVelocity: 0.3,      // Minimum velocity
            longPressDuration: 500,  // Long press time (ms)
            tapTimeout: 200          // Max time for tap (ms)
        };
        
        this.init();
    }
    
    init() {
        this.element.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: false });
        this.element.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
        this.element.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: true });
        this.element.addEventListener('touchcancel', this.handleTouchCancel.bind(this), { passive: true });
    }
    
    handleTouchStart(event) {
        const touch = event.touches[0];
        this.startX = touch.clientX;
        this.startY = touch.clientY;
        this.startTime = Date.now();
        this.isLongPress = false;
        
        // Start long press timer
        this.longPressTimer = setTimeout(() => {
            this.isLongPress = true;
            if (this.callbacks.onLongPress) {
                this.callbacks.onLongPress(event, { x: this.startX, y: this.startY });
            }
        }, this.config.longPressDuration);
    }
    
    handleTouchMove(event) {
        // Cancel long press if user moves
        if (this.longPressTimer) {
            clearTimeout(this.longPressTimer);
            this.longPressTimer = null;
        }
    }
    
    handleTouchEnd(event) {
        if (this.longPressTimer) {
            clearTimeout(this.longPressTimer);
        }
        
        if (this.isLongPress) {
            return; // Already handled by long press
        }
        
        const touch = event.changedTouches[0];
        const endX = touch.clientX;
        const endY = touch.clientY;
        const endTime = Date.now();
        
        const diffX = endX - this.startX;
        const diffY = endY - this.startY;
        const diffTime = endTime - this.startTime;
        
        const absX = Math.abs(diffX);
        const absY = Math.abs(diffY);
        
        // Check for tap
        if (absX < 10 && absY < 10 && diffTime < this.config.tapTimeout) {
            if (this.callbacks.onTap) {
                this.callbacks.onTap(event, { x: endX, y: endY });
            }
            return;
        }
        
        // Check for swipe
        const velocity = Math.max(absX, absY) / diffTime;
        
        if (velocity >= this.config.swipeVelocity) {
            // Horizontal swipe
            if (absX > absY && absX > this.config.swipeThreshold) {
                if (diffX > 0 && this.callbacks.onSwipeRight) {
                    this.callbacks.onSwipeRight(event, { distance: diffX, velocity });
                } else if (diffX < 0 && this.callbacks.onSwipeLeft) {
                    this.callbacks.onSwipeLeft(event, { distance: absX, velocity });
                }
            }
            // Vertical swipe
            else if (absY > absX && absY > this.config.swipeThreshold) {
                if (diffY > 0 && this.callbacks.onSwipeDown) {
                    this.callbacks.onSwipeDown(event, { distance: diffY, velocity });
                } else if (diffY < 0 && this.callbacks.onSwipeUp) {
                    this.callbacks.onSwipeUp(event, { distance: absY, velocity });
                }
            }
        }
    }
    
    handleTouchCancel(event) {
        if (this.longPressTimer) {
            clearTimeout(this.longPressTimer);
        }
    }
    
    destroy() {
        this.element.removeEventListener('touchstart', this.handleTouchStart);
        this.element.removeEventListener('touchmove', this.handleTouchMove);
        this.element.removeEventListener('touchend', this.handleTouchEnd);
        this.element.removeEventListener('touchcancel', this.handleTouchCancel);
    }
}

/**
 * Pull to Refresh
 * Hey future me - classic mobile pattern! Pull down from top to refresh content.
 * Shows a loading indicator while pulling. Triggers refresh callback at threshold.
 */
class PullToRefresh {
    constructor(element, onRefresh) {
        this.element = element;
        this.onRefresh = onRefresh;
        
        this.startY = 0;
        this.currentY = 0;
        this.isDragging = false;
        this.threshold = 80; // Pull distance to trigger refresh
        
        this.indicator = this.createIndicator();
        this.init();
    }
    
    createIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'pull-to-refresh-indicator';
        indicator.innerHTML = `
            <div class="pull-to-refresh-spinner">
                <i class="fa-solid fa-arrow-down"></i>
            </div>
        `;
        indicator.style.cssText = `
            position: absolute;
            top: -60px;
            left: 0;
            right: 0;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--primary);
            transition: transform 0.3s ease;
            pointer-events: none;
        `;
        this.element.insertBefore(indicator, this.element.firstChild);
        return indicator;
    }
    
    init() {
        this.element.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: true });
        this.element.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
        this.element.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: true });
    }
    
    handleTouchStart(event) {
        // Only trigger at top of page
        if (window.scrollY === 0) {
            this.startY = event.touches[0].clientY;
            this.isDragging = true;
        }
    }
    
    handleTouchMove(event) {
        if (!this.isDragging) return;
        
        this.currentY = event.touches[0].clientY;
        const diff = this.currentY - this.startY;
        
        if (diff > 0 && window.scrollY === 0) {
            event.preventDefault();
            
            // Rubber band effect
            const distance = Math.min(diff * 0.5, this.threshold * 1.5);
            this.indicator.style.transform = `translateY(${distance + 60}px)`;
            
            // Change icon when threshold reached
            const icon = this.indicator.querySelector('i');
            if (distance >= this.threshold) {
                icon.className = 'fa-solid fa-rotate-right fa-spin';
            } else {
                icon.className = 'fa-solid fa-arrow-down';
            }
        }
    }
    
    async handleTouchEnd(event) {
        if (!this.isDragging) return;
        
        const diff = this.currentY - this.startY;
        const distance = Math.min(diff * 0.5, this.threshold * 1.5);
        
        if (distance >= this.threshold) {
            // Trigger refresh
            this.indicator.querySelector('i').className = 'fa-solid fa-spinner fa-spin';
            
            try {
                await this.onRefresh();
            } catch (error) {
                console.error('Refresh failed:', error);
            }
        }
        
        // Reset
        this.indicator.style.transform = 'translateY(0)';
        this.isDragging = false;
        
        setTimeout(() => {
            this.indicator.querySelector('i').className = 'fa-solid fa-arrow-down';
        }, 300);
    }
}

/**
 * Global Mobile Optimizations
 */
const MobileOptimizations = {
    init() {
        this.initSidebarSwipe();
        this.initCardSwipeActions();
        this.initPullToRefresh();
        this.initTouchTargets();
        this.preventZoom();
    },
    
    // Swipe to open/close sidebar
    initSidebarSwipe() {
        const sidebar = document.querySelector('.app-sidebar');
        if (!sidebar) return;
        
        new SwipeDetector(document.body, {
            onSwipeRight: (event, data) => {
                // Only from edge
                if (data.distance > 50 && event.changedTouches[0].clientX < 50) {
                    sidebar.classList.add('open');
                }
            },
            onSwipeLeft: () => {
                sidebar.classList.remove('open');
            }
        });
    },
    
    // Swipe actions on download cards
    initCardSwipeActions() {
        document.querySelectorAll('.download-card').forEach(card => {
            new SwipeDetector(card, {
                onSwipeLeft: () => {
                    // Show action buttons
                    card.classList.add('swiped-left');
                    setTimeout(() => card.classList.remove('swiped-left'), 3000);
                },
                onLongPress: () => {
                    // Select card
                    const checkbox = card.querySelector('.download-checkbox');
                    if (checkbox) {
                        checkbox.checked = !checkbox.checked;
                        checkbox.dispatchEvent(new Event('change'));
                        
                        // Haptic feedback\n                        if ('vibrate' in navigator) {
                            navigator.vibrate(50);
                        }
                    }
                }
            });
        });
    },
    
    // Pull to refresh on downloads page
    initPullToRefresh() {
        if (window.location.pathname.includes('/downloads')) {
            const mainContent = document.querySelector('#main-content');
            if (mainContent) {
                new PullToRefresh(mainContent, async () => {
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    window.location.reload();
                });
            }
        }
    },
    
    // Ensure touch targets are 44x44px minimum (iOS guideline)
    initTouchTargets() {
        const style = document.createElement('style');
        style.textContent = `
            @media (hover: none) {
                .btn, button, a, .nav-item {
                    min-height: 44px;
                    min-width: 44px;
                }
                
                .btn-icon {
                    width: 44px;
                    height: 44px;
                }
            }
        `;
        document.head.appendChild(style);
    },
    
    // Prevent double-tap zoom
    preventZoom() {
        let lastTouchEnd = 0;
        document.addEventListener('touchend', (event) => {
            const now = Date.now();
            if (now - lastTouchEnd <= 300) {
                event.preventDefault();
            }
            lastTouchEnd = now;
        }, { passive: false });
    }
};

// Auto-initialize on mobile devices
if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
    document.addEventListener('DOMContentLoaded', () => {
        MobileOptimizations.init();
    });
}

// Export
window.SwipeDetector = SwipeDetector;
window.PullToRefresh = PullToRefresh;
window.MobileOptimizations = MobileOptimizations;

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SwipeDetector, PullToRefresh, MobileOptimizations };
}
