// Bomu service worker.
// Strategy (changed in v2, after accounts were added):
//   - Pages (HTML): network-only. Pages are now personal (your bar, your
//     ratings), so we never keep copies in the shared browser cache --
//     otherwise a later user of the same device could see them offline.
//   - Static assets (/static/): cache-first, they rarely change.
// Bump CACHE_VERSION whenever cached behavior needs a hard reset.

const CACHE_VERSION = "bomu-v2";

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
        // Network-only for pages: no caching of personal content. If truly
        // offline, show a tiny friendly page instead of the browser error.
        event.respondWith(
            fetch(request).catch(() => new Response(
                "<html><body style=\"background:#1a1a2e;color:#e0e0e0;" +
                "font-family:sans-serif;text-align:center;padding-top:4rem\">" +
                "<h1>Bomu</h1><p>You're offline. Reconnect and try again " +
                "&mdash; the bar's still here.</p></body></html>",
                { headers: { "Content-Type": "text/html" } }
            ))
        );
    }
});
