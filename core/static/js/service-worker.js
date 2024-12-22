const CACHE_NAME = 'shop-rep-cache-v1';
const urlsToCache = [
    '/track-n-trace/',  // Update this to your actual home URL
    '/static/assets/css/mobile-app.css',  // Update based on your actual CSS files
    '/static/assets/css/material-dashboard.css',
    '/static/assets/css/nucleo-icons.css',
    '/static/assets/css/nucleo-svg.css',
    '/static/js/main.js',
    '/static/assets/js/core/popper.min.js',
    '/static/assets/js/core/bootstrap.min.js',
    '/static/assets/js/material-dashboard.min.js',
    '/static/images/logo.png',
    '/track-n-trace/login/'  // Add your login page URL
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
            .catch(error => {
                console.error('Cache installation failed:', error);
            })
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // If cached response exists, return it
                if (response) {
                    return response;
                }

                // Clone the request because it can only be used once
                const fetchRequest = event.request.clone();

                return fetch(fetchRequest)
                    .then(response => {
                        // Check if we received a valid response
                        if (!response || response.status !== 200) {
                            return response;
                        }

                        // Clone the response because it can only be used once
                        const responseToCache = response.clone();

                        caches.open(CACHE_NAME)
                            .then(cache => {
                                // Only cache same-origin requests
                                if (event.request.url.startsWith(self.location.origin)) {
                                    cache.put(event.request, responseToCache);
                                }
                            });

                        return response;
                    })
                    .catch(error => {
                        console.error('Fetch failed:', error);
                        // Only return offline page for navigation requests
                        if (event.request.mode === 'navigate') {
                            return caches.match('/track-n-trace/login/');
                        }
                        throw error;
                    });
            })
    );
});

// Add activate event to clean up old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});