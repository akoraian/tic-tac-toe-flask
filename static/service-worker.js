const CACHE_NAME = "tic-tac-toe-v1";
const urlsToCache = [
  "/",
  "/static/style.css",
  "/static/icon-192.png",
  "/static/icon-512.png"
];

self.addEventListener("install", function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(urlsToCache);
    })
  );
});

self.addEventListener("fetch", function(event) {
  event.respondWith(
    caches.match(event.request).then(function(response) {
      return response || fetch(event.request);
    })
  );
});