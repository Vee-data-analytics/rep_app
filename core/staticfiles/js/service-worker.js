const CACHE_NAME = 'shop-rep-cache-v1';
const urlsToCache = [
    '/track-n-trace/',
    '/static/assets/css/mobile-app.css',
    '/static/assets/css/material-dashboard.css',
    '/static/assets/css/nucleo-icons.css',
    '/static/assets/css/nucleo-svg.css',
    '/static/js/main.js',
    '/static/assets/js/core/popper.min.js',
    '/static/assets/js/core/bootstrap.min.js',
    '/static/assets/js/material-dashboard.min.js',
    '/static/images/logo.png',
    '/track-n-trace/login/'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
            .catch(error => console.error('Cache installation failed:', error))
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request).then(cachedResponse => {
            if (cachedResponse) return cachedResponse;

            return fetch(event.request)
                .then(networkResponse => {
                    if (!networkResponse || networkResponse.status !== 200) {
                        return networkResponse;
                    }

                    // Cache the fetched response
                    const responseToCache = networkResponse.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        if (event.request.url.startsWith(self.location.origin)) {
                            cache.put(event.request, responseToCache);
                        }
                    });

                    return networkResponse;
                })
                .catch(error => {
                    console.error('Fetch failed:', error);
                    if (event.request.mode === 'navigate') {
                        return caches.match('/track-n-trace/login/');
                    }
                });
        })
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames
                    .filter(cacheName => cacheName.startsWith('shop-rep-') && cacheName !== CACHE_NAME)
                    .map(cacheName => caches.delete(cacheName))
            );
        })
    );
});
