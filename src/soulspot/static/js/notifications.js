/**
 * Native Browser Notifications Manager
 * 
 * Hey future me - this handles native OS notifications! These appear outside the browser,
 * even when the tab is not focused. Perfect for download completions, errors, etc.
 * We gracefully degrade to Toast notifications if permission is denied or not supported.
 * 
 * Important: User must grant permission first (we ask nicely on first use).
 * Notifications persist in OS notification center and can have actions (buttons).
 */

class NotificationManager {
    constructor() {
        this.permission = 'default';
        this.isSupported = 'Notification' in window;
        this.queue = [];
        
        if (this.isSupported) {
            this.permission = Notification.permission;
        }
    }
    
    /**
     * Request notification permission from user
     * @returns {Promise<string>} Permission status
     */
    async requestPermission() {
        if (!this.isSupported) {
            console.warn('Notifications not supported in this browser');
            return 'denied';
        }
        
        if (this.permission === 'granted') {
            return 'granted';
        }
        
        try {
            this.permission = await Notification.requestPermission();
            
            if (this.permission === 'granted') {
                this.showWelcomeNotification();
            }
            
            return this.permission;
        } catch (error) {
            console.error('Failed to request notification permission:', error);
            return 'denied';
        }
    }
    
    /**
     * Show a notification
     * @param {string} title - Notification title
     * @param {Object} options - Notification options
     * @returns {Notification|null} Notification instance
     */
    show(title, options = {}) {
        const config = {
            icon: '/static/icons/icon-192.png',
            badge: '/static/icons/badge-96.png',
            vibrate: [200, 100, 200],
            requireInteraction: false,
            silent: false,
            ...options
        };
        
        // Check if we have permission
        if (this.permission !== 'granted') {
            console.log('No notification permission, falling back to toast');
            this.fallbackToToast(title, options);
            return null;
        }
        
        try {
            const notification = new Notification(title, config);
            
            // Click handler - focus window
            notification.onclick = (event) => {
                event.preventDefault();
                window.focus();
                notification.close();
                
                // Custom click handler if provided
                if (options.onClick) {
                    options.onClick(event);
                }
            };
            
            // Auto-close after duration (if specified)
            if (options.duration) {
                setTimeout(() => notification.close(), options.duration);
            }
            
            return notification;
            
        } catch (error) {
            console.error('Failed to show notification:', error);
            this.fallbackToToast(title, options);
            return null;
        }
    }
    
    /**
     * Show download completed notification
     */
    downloadCompleted(trackName, count = 1) {
        const title = count === 1 
            ? '✅ Download Complete'
            : `✅ ${count} Downloads Complete`;
        
        const body = count === 1
            ? `${trackName} has been downloaded successfully`
            : `${count} tracks downloaded successfully`;
        
        return this.show(title, {
            body: body,
            tag: 'download-complete',
            icon: '/static/icons/download-complete.png',
            requireInteraction: false,
            vibrate: [200, 100, 200, 100, 200],
            onClick: () => {
                // Navigate to downloads page
                window.location.href = '/downloads';
            }
        });
    }
    
    /**
     * Show download failed notification
     */
    downloadFailed(trackName, error) {
        return this.show('❌ Download Failed', {
            body: `Failed to download ${trackName}: ${error}`,
            tag: 'download-failed',
            icon: '/static/icons/error.png',
            requireInteraction: true,
            onClick: () => {
                window.location.href = '/downloads';
            }
        });
    }
    
    /**
     * Show playlist synced notification
     */
    playlistSynced(playlistName, newTracks) {
        return this.show('🎵 Playlist Synced', {
            body: `${playlistName} updated with ${newTracks} new tracks`,
            tag: 'playlist-sync',
            icon: '/static/icons/playlist.png'
        });
    }
    
    /**
     * Show welcome notification after permission granted
     * @private
     */
    showWelcomeNotification() {
        this.show('🎉 Notifications Enabled', {
            body: 'You\'ll receive updates about downloads and syncs',
            tag: 'welcome',
            duration: 5000
        });
    }
    
    /**
     * Fallback to toast notification
     * @private
     */
    fallbackToToast(title, options) {
        if (typeof ToastManager !== 'undefined') {
            const type = options.body?.includes('Failed') || options.body?.includes('Error') 
                ? 'error' 
                : 'info';
            
            ToastManager.show(options.body || title, type, title);
        }
    }
    
    /**
     * Check if notifications are supported and permitted
     */
    isEnabled() {
        return this.isSupported && this.permission === 'granted';
    }
    
    /**
     * Close all notifications with specific tag
     */
    static closeByTag(tag) {
        // Note: Only works for notifications created by this page
        // Browser limitation - can't access all notifications
        console.log(`Closing notifications with tag: ${tag}`);
    }
}

// Create global instance
const notificationManager = new NotificationManager();

// Auto-request permission on first user interaction
let permissionRequested = false;
document.addEventListener('click', async () => {
    if (!permissionRequested && notificationManager.permission === 'default') {
        permissionRequested = true;
        // Wait a bit to not interrupt the user's action
        setTimeout(() => {
            notificationManager.requestPermission();
        }, 1000);
    }
}, { once: true });

// Export
window.NotificationManager = notificationManager;

if (typeof module !== 'undefined' && module.exports) {
    module.exports = NotificationManager;
}
