// Bomu service worker.
// Strategy:
//   - Pages (HTML): network-first, fall back to last cached copy when offline.
//     Recommendations depend on live DB state, so fresh wins whenever possible.
//   - Static assets (/static/): cache-first, they rarely change.
// Bump CACHE_VERSION whenever cached behavior needs a hard reset.

const CACHE_VERSION = "bomu-v1";

const PRECACHE = [
    "/static/manifest.json",
    "/static/icon-192.png",
    "/static/icon-512.png",
];

self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_VERSION)
            .then((cache) => cache.addAll(PRECACHE))
            .then(() => self.skipWaiting())
    );
});

self.addEventListener("activate", (event) => {
    // Drop caches from older versions
    event.waitUntil(
        caches.keys()
            .then((keys) => Promise.all(
                keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k))
            ))
            .then(() => self.clients.claim())
    );
});

self.addEventListener("fetch", (event) => {
    const request = event.request;
    // Only GETs are cacheable; let POSTs (ratings, checklist, scans) pass through
    if (request.method !== "GET") return;

    const url = new URL(request.url);
    if (url.origin !== self.location.origin) return;

    if (url.pathname.startsWith("/static/")) {
        // Cache-first for static assets
        event.respondWith(
            caches.match(request).then((cached) => {
                if (cached) return cached;
                return fetch(request).then((response) => {
                    const copy = response.clone();
                    caches.open(CACHE_VERSION).then((cache) => cache.put(request, copy));
                    return response;
                });
            })
        );
    } else {
        // Network-first for pages
        event.respondWith(
            fetch(request)
                .then((response) => {
                    const copy = response.clone();
                    caches.open(CACHE_VERSION).then((cache) => cache.put(request, copy));
                    return response;
                })
                .catch(() => caches.match(request))
        );
    }
});
