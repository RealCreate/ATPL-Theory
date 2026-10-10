/* Offline support. Online: always fetch the latest files (revalidated, so unchanged files are cheap)
   and keep a copy. Offline: serve the saved copy. Images, which never change, are served from the copy first. */
const CACHE = "atpl-v16"
const SHELL = ["./", "index.html", "app.css", "app.js", "data/subjects.json", "manifest.webmanifest", "icons/icon-192.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE)
    .then((c) => c.addAll(SHELL.map((u) => new Request(u, { cache: "reload" }))))
    .then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys()
    .then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  const url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== location.origin) return;
  const isImage = /\.(jpe?g|png|webp|svg)$/i.test(url.pathname);
  e.respondWith(caches.open(CACHE).then(async (c) => {
    const key = req.mode === "navigate" ? "index.html" : req;
    if (isImage) {
      const hit = await c.match(req);
      if (hit) return hit;
    }
    try {
      const r = await fetch(req.mode === "navigate" ? url.href : req, { cache: "no-cache" });
      if (r.ok) c.put(key, r.clone());
      return r;
    } catch (err) {
      const hit = await c.match(key, { ignoreSearch: true });
      if (hit) return hit;
      throw err;
    }
  }));
});
