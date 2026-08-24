// Service worker for offline support.
//
// The whole app is one self-contained HTML file (no external CSS/JS/fonts),
// so "offline support" just means: keep a copy of that one file around and
// serve it when the network is unavailable (subway, plane mode, dead zone).
//
// Strategy: network-first for navigations. Online users always get the
// freshest deploy (new vocab batches, new features); the cache is updated
// transparently on every successful fetch, so as long as the phone has a
// connection at some point, offline mode never lags far behind. Only when
// fetch() actually fails do we fall back to whatever was last cached.
//
// Bump CACHE_NAME if this file's *logic* changes, so old caches get swept.
var CACHE_NAME = "tef-vocab-v1";
var PRECACHE_URLS = ["./", "./index.html"];

self.addEventListener("install", function (event) {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) {
      // best-effort, one at a time -- a single failed URL shouldn't abort
      // caching the rest (cache.addAll is all-or-nothing)
      return Promise.all(
        PRECACHE_URLS.map(function (url) {
          return cache.add(url).catch(function () {});
        })
      );
    })
  );
});

self.addEventListener("activate", function (event) {
  event.waitUntil(
    caches
      .keys()
      .then(function (names) {
        return Promise.all(
          names
            .filter(function (name) { return name !== CACHE_NAME; })
            .map(function (name) { return caches.delete(name); })
        );
      })
      .then(function () { return self.clients.claim(); })
  );
});

self.addEventListener("fetch", function (event) {
  if (event.request.method !== "GET") return;

  event.respondWith(
    fetch(event.request)
      .then(function (response) {
        var copy = response.clone();
        caches.open(CACHE_NAME).then(function (cache) {
          cache.put(event.request, copy);
        });
        return response;
      })
      .catch(function () {
        return caches.match(event.request).then(function (cached) {
          return cached || caches.match("./index.html");
        });
      })
  );
});
