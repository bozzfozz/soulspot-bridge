/**
 * Service Worker for SoulSpot PWA
 * 
 * Hey future me - this is the heart of offline functionality! Service Worker intercepts
 * network requests and can serve cached responses. Three caching strategies used here:
 * 
 * 1. Cache First (static assets) - Try cache, fallback to network
 * 2. Network First (API/dynamic) - Try network, fallback to cache
 * 3. Stale While Revalidate (images) - Serve cache immediately, update in background
 * 
 * Critical: Service Worker runs in a separate thread, NO access to DOM or window!
 * Use postMessage() to communicate with main thread.
 */

const CACHE_NAME = 'soulspot-v1.0.0';
const RUNTIME_CACHE = 'soulspot-runtime-v1.0.0';

// Assets to cache immediately on install
const STATIC_ASSETS = [
    '/',
    '/static/css/variables.css',
    '/static/css/layout.css',
    '/static/css/components.css',
    '/static/js/app.js',
    '/static/js/circular-progress.js',
    '/static/js/fuzzy-search.js',
    '/static/js/notifications.js',
    '/static/js/sse-client.js',
    '/offline.html',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png'
];

// Routes that should always try network first
const NETWORK_FIRST_ROUTES = [
    '/api/',
    '/auth/'
];

// Routes that should be cached
const CACHE_FIRST_ROUTES = [
    '/static/',
    '/fonts/',
    '.woff2',
    '.woff',
    '.ttf'
];

/**
 * Install Event - Cache static assets
 */
self.addEventListener('install', (event) => {
    console.log('[ServiceWorker] Installing...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[ServiceWorker] Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => {
                console.log('[ServiceWorker] Installation complete');
                // Skip waiting to activate immediately
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('[ServiceWorker] Installation failed:', error);
            })
    );
});

/**
 * Activate Event - Clean up old caches
 */
self.addEventListener('activate', (event) => {
    console.log('[ServiceWorker] Activating...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE) {
                            console.log('[ServiceWorker] Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('[ServiceWorker] Activation complete');
                // Take control of all pages immediately
                return self.clients.claim();
            })
    );
});

/**
 * Fetch Event - Intercept network requests
 */
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Skip chrome-extension and other non-http(s) requests
    if (!url.protocol.startsWith('http')) {
        return;
    }
    
    // Choose strategy based on route
    if (shouldUseNetworkFirst(url.pathname)) {
        event.respondWith(networkFirstStrategy(request));
    } else if (shouldUseCacheFirst(url.pathname)) {
        event.respondWith(cacheFirstStrategy(request));
    } else {
        event.respondWith(staleWhileRevalidateStrategy(request));
    }
});

/**
 * Network First Strategy
 * Try network, fallback to cache, fallback to offline page
 */
async function networkFirstStrategy(request) {
    try {
        const networkResponse = await fetch(request);
        
        // Cache successful responses
        if (networkResponse.ok) {
            const cache = await caches.open(RUNTIME_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('[ServiceWorker] Network failed, trying cache:', request.url);
        
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline page for navigation requests
        if (request.mode === 'navigate') {
            return caches.match('/offline.html');
        }
        
        throw error;
    }
}

/**
 * Cache First Strategy
 * Try cache, fallback to network
 */
async function cacheFirstStrategy(request) {
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
        return cachedResponse;
    }
    
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(RUNTIME_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.error('[ServiceWorker] Cache and network both failed:', error);
        throw error;
    }
}

/**
 * Stale While Revalidate Strategy
 * Serve from cache immediately, update cache in background
 */
async function staleWhileRevalidateStrategy(request) {
    const cachedResponse = await caches.match(request);
    
    const networkPromise = fetch(request).then((networkResponse) => {
        if (networkResponse.ok) {
            const cache = caches.open(RUNTIME_CACHE);
            cache.then((c) => c.put(request, networkResponse.clone()));
        }
        return networkResponse;
    }).catch(() => {
        // Network failed, but we might have cache
        return cachedResponse;
    });
    
    // Return cached response immediately, network response will update cache
    return cachedResponse || networkPromise;
}

/**
 * Route matching helpers
 */
function shouldUseNetworkFirst(pathname) {
    return NETWORK_FIRST_ROUTES.some(route => pathname.startsWith(route));
}

function shouldUseCacheFirst(pathname) {
    return CACHE_FIRST_ROUTES.some(route => 
        pathname.startsWith(route) || pathname.endsWith(route)
    );
}

/**
 * Background Sync - Retry failed requests
 */
self.addEventListener('sync', (event) => {
    console.log('[ServiceWorker] Background sync:', event.tag);
    
    if (event.tag === 'sync-downloads') {
        event.waitUntil(syncDownloads());
    }
});

async function syncDownloads() {
    // Implementation would sync pending downloads when back online
    console.log('[ServiceWorker] Syncing downloads...');
}

/**
 * Push Notifications
 */
self.addEventListener('push', (event) => {
    console.log('[ServiceWorker] Push notification received');
    
    const data = event.data ? event.data.json() : {};
    
    const options = {
        body: data.body || 'You have a new notification',
        icon: '/static/icons/icon-192.png',
        badge: '/static/icons/badge-96.png',
        vibrate: [200, 100, 200],
        data: data
    };
    
    event.waitUntil(
        self.registration.showNotification(data.title || 'SoulSpot', options)
    );
});

/**
 * Notification Click Handler
 */
self.addEventListener('notificationclick', (event) => {
    console.log('[ServiceWorker] Notification clicked:', event.notification.tag);
    
    event.notification.close();
    
    // Open or focus the app
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then((clientList) => {
                // Check if app is already open
                for (const client of clientList) {
                    if (client.url.includes(self.location.origin) && 'focus' in client) {
                        return client.focus();
                    }
                }
                
                // Open new window
                if (clients.openWindow) {
                    return clients.openWindow('/');
                }
            })
    );
});

/**
 * Message Handler - Communication with main thread
 */
self.addEventListener('message', (event) => {
    console.log('[ServiceWorker] Message received:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CLEAR_CACHE') {
        event.waitUntil(
            caches.keys().then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => caches.delete(cacheName))
                );
            })
        );
    }
});

console.log('[ServiceWorker] Loaded successfully');
