// Service Worker des Creator Hub (gebaute Vue-App).
// Strategie:
//  - Navigationen (HTML): network-first mit Offline-Fallback auf die App-Shell.
//  - Statische Assets (gleicher Origin): stale-while-revalidate.
//  - /api/* wird NIE gecacht (Live-Daten + Compliance/Streaming).
// Robust gegen Vites gehashte Dateinamen, weil zur Laufzeit gecacht wird.

const CACHE = 'creator-hub-v1'

self.addEventListener('install', () => {
  self.skipWaiting()
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  )
})

self.addEventListener('fetch', (event) => {
  const req = event.request
  if (req.method !== 'GET') return

  const url = new URL(req.url)
  if (url.origin !== self.location.origin) return
  if (url.pathname.includes('/api/')) return // Live-Daten nie cachen

  // App-Navigation: frisch laden, bei Offline auf zwischengespeicherte Shell.
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone()
          caches.open(CACHE).then((c) => c.put(req, copy))
          return res
        })
        .catch(() => caches.match(req).then((m) => m || caches.match('./'))),
    )
    return
  }

  // Statische Assets: sofort aus Cache, im Hintergrund aktualisieren.
  event.respondWith(
    caches.match(req).then((cached) => {
      const network = fetch(req)
        .then((res) => {
          if (res && res.status === 200) {
            const copy = res.clone()
            caches.open(CACHE).then((c) => c.put(req, copy))
          }
          return res
        })
        .catch(() => cached)
      return cached || network
    }),
  )
})
