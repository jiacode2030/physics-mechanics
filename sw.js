/* AP Labs offline support for physics-mechanics.
   Pages: network first (so updates show up right away), the saved copy when offline or very slow.
   Google Fonts: saved after the first download. Everything else (analytics, GitHub links) is left alone. */
const CACHE = 'aplabs-physics-mechanics-v1';
const PRECACHE = ["./", "./index.html"];
const SCOPE = new URL('./', self.location).pathname;

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith('aplabs-physics-mechanics-') && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

function fromCache(req) {
  return caches.match(req, { ignoreSearch: true })
    .then(m => m || (req.mode === 'navigate' ? caches.match(SCOPE, { ignoreSearch: true }) : undefined));
}
function networkFirst(req) {
  return new Promise(resolve => {
    let done = false;
    const finish = r => { if (!done && r) { done = true; resolve(r); } };
    const slow = setTimeout(() => fromCache(req).then(finish), 4000);
    fetch(req).then(res => {
      clearTimeout(slow);
      if (res && res.ok && res.type === 'basic') caches.open(CACHE).then(c => c.put(req, res.clone()));
      finish(res);
    }).catch(() => {
      clearTimeout(slow);
      fromCache(req).then(m => { if (!done) { done = true; resolve(m || Response.error()); } });
    });
  });
}
function cacheFirst(req) {
  return caches.match(req).then(m => m || fetch(req).then(res => {
    if (res && (res.ok || res.type === 'opaque')) caches.open(CACHE).then(c => c.put(req, res.clone()));
    return res;
  }));
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin === self.location.origin && url.pathname.startsWith(SCOPE)) e.respondWith(networkFirst(req));
  else if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') e.respondWith(cacheFirst(req));
});
