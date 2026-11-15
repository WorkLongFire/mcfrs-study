// Shift Ready service worker. Network first, so new versions load as soon as you are online; cache is the offline fallback.
const CACHE="shift-ready-20261115111308";
const SHELL=["./","index.html","manifest.webmanifest","icons/icon-192.png","icons/icon-512.png","icons/apple-touch-icon.png"];
self.addEventListener("install",e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()))});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k.startsWith("shift-ready-")&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener("fetch",e=>{
  const req=e.request;if(req.method!=="GET")return;
  const url=new URL(req.url);
  if(url.pathname.endsWith("version.json"))return; // always live
  const font=/fonts\.(googleapis|gstatic)\.com$/.test(url.hostname);
  if(url.origin!==location.origin&&!font)return;
  e.respondWith(fetch(req).then(res=>{if(res&&(res.ok||res.type==="opaque")){const copy=res.clone();caches.open(CACHE).then(c=>c.put(req,copy))}return res})
    .catch(()=>caches.match(req).then(r=>r||(req.mode==="navigate"?caches.match("index.html"):undefined))));
});
