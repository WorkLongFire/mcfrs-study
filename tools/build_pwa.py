"""Build the installable app at the repository root from source/shift-ready.artifact.html.

Run from anywhere:  python3 tools/build_pwa.py
Writes index.html, sw.js, manifest.webmanifest, version.json and icons/ at the repo root.
vendor/tesseract/ (the on-device photo reader) is committed and left as is."""
import os, re, json, time, shutil
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = ROOT
BUILD = time.strftime("%Y%m%d%H%M%S")
SITE = "https://worklongfire.github.io/shift-ready/"  # link previews need the full address

os.makedirs(os.path.join(OUT, "icons"), exist_ok=True)
src = open(os.path.join(ROOT, "source", "shift-ready.artifact.html"), encoding="utf-8").read()

def rep(a, b):
    global src
    assert a in src, ("missing", a[:80])
    src = src.replace(a, b)

# standalone wording for features that need claude.ai
rep('"Sign in to claude.ai and open the shared link to chat with friends. Everything else works on this device."',
    '(window.SR_STANDALONE?"Chat, sharing and the leaderboard work in the claude.ai version of Shift Ready. Everything else works here.":"Sign in to claude.ai and open the shared link to chat with friends. Everything else works on this device.")')
rep('toast(S.dbState==="loading"?"Connecting to your squad…":"Sign in to claude.ai to chat with friends")',
    'toast(S.dbState==="loading"?"Connecting to your squad…":window.SR_STANDALONE?"Squad features work in the claude.ai version":"Sign in to claude.ai to chat with friends")')
rep('${!S.sample?"Open this app on claude.ai while signed in, and allow Claude when it asks."',
    '${!S.sample?(window.SR_STANDALONE?"Photo reading works in the claude.ai version of Shift Ready.":"Open this app on claude.ai while signed in, and allow Claude when it asks.")')

title = re.search(r"<title>(.*?)</title>", src).group(1)
src = src.replace(f"<title>{title}</title>", "", 1)

head = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="TikTok-style EMT and firefighter study app.">
<meta name="theme-color" content="#000000">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Shift Ready">
<meta property="og:title" content="MCFRS Fire &amp; EMS Study">
<meta property="og:description" content="Swipe short fire and EMS lessons, then quiz yourself. Free, works offline. Unofficial study app, not run by MCFRS.">
<meta property="og:url" content="{SITE}">
<meta property="og:image" content="{SITE}og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Shift Ready: blue medical cross with a heartbeat line">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}og-image.png">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/icon-192.png" type="image/png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Shift Ready">
<style>
html{{box-sizing:border-box;height:100%;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px);background:#000;color-scheme:dark}}
body{{margin:0;font:14px/1.4 system-ui,-apple-system,sans-serif;-webkit-tap-highlight-color:transparent;overscroll-behavior:none}}
img{{max-width:100%}}
[hidden]{{display:none!important}}
#updateBar{{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(76px + env(safe-area-inset-bottom,0px));z-index:100;background:#fff;color:#000;font-weight:700;border:0;border-radius:999px;padding:11px 16px;box-shadow:0 6px 24px rgba(0,0,0,.5);font-size:14px}}
</style>
<script>window.SR_STANDALONE=true;window.SR_BUILD="{BUILD}";</script>
</head>
<body>
"""

tail = f"""
<button id="updateBar" hidden>Update ready · tap to reload</button>
<script>
(function(){{
  var bar=document.getElementById("updateBar");
  bar.onclick=function(){{location.reload()}};
  function check(){{
    if(!navigator.onLine)return;
    fetch("version.json?t="+Date.now(),{{cache:"no-store"}}).then(function(r){{return r.json()}}).then(function(v){{
      if(v&&v.build&&v.build!==window.SR_BUILD)bar.hidden=false;
    }}).catch(function(){{}});
  }}
  if("serviceWorker" in navigator){{
    navigator.serviceWorker.register("sw.js").then(function(reg){{reg.update().catch(function(){{}})}}).catch(function(){{}});
  }}
  document.addEventListener("visibilitychange",function(){{if(document.visibilityState==="visible")check()}});
  setTimeout(check,3000);setInterval(check,30*60*1000);
}})();
</script>
</body>
</html>
"""
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(head + src + tail)
json.dump({"build": BUILD}, open(os.path.join(OUT, "version.json"), "w"))

manifest = {
  "name": "Shift Ready", "short_name": "Shift Ready",
  "description": "TikTok-style EMT and firefighter study clips, quizzes and flashcards.",
  "start_url": "./", "scope": "./", "display": "standalone", "orientation": "portrait",
  "background_color": "#000000", "theme_color": "#000000",
  "icons": [
    {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
    {"src": "icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
  ]
}
json.dump(manifest, open(os.path.join(OUT, "manifest.webmanifest"), "w"), indent=1)

sw = f"""// Shift Ready service worker. Network first, so new versions load as soon as you are online; cache is the offline fallback.
const CACHE="shift-ready-{BUILD}";
const SHELL=["./","index.html","manifest.webmanifest","icons/icon-192.png","icons/icon-512.png","icons/apple-touch-icon.png"];
self.addEventListener("install",e=>{{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()))}});
self.addEventListener("activate",e=>{{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k.startsWith("shift-ready-")&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))}});
self.addEventListener("fetch",e=>{{
  const req=e.request;if(req.method!=="GET")return;
  const url=new URL(req.url);
  if(url.pathname.endsWith("version.json"))return; // always live
  const font=/fonts\\.(googleapis|gstatic)\\.com$/.test(url.hostname);
  if(url.origin!==location.origin&&!font)return;
  e.respondWith(fetch(req).then(res=>{{if(res&&(res.ok||res.type==="opaque")){{const copy=res.clone();caches.open(CACHE).then(c=>c.put(req,copy))}}return res}})
    .catch(()=>caches.match(req).then(r=>r||(req.mode==="navigate"?caches.match("index.html"):undefined))));
}});
"""
open(os.path.join(OUT, "sw.js"), "w").write(sw)
open(os.path.join(OUT, ".nojekyll"), "w").write("")
# on-device text reader: vendor/tesseract/ is committed. To refresh it, download tesseract.js@5.1.1,
# tesseract.js-core@5.1.1 (the two *-lstm.wasm.js files) and @tesseract.js-data/eng@1.0.0 (4.0.0_best_int)
# from npm and copy them into vendor/tesseract/{., core, lang}.
assert os.path.isdir(os.path.join(OUT, "vendor", "tesseract")), "vendor/tesseract is missing"

# icon: night-shift black, ECG trace that turns from EMT blue to fire orange
def icon(size, pad=0.0):
    S = 1024
    im = Image.new("RGB", (S, S), "#0b0d12")
    d = ImageDraw.Draw(im)
    m = int(S * pad)
    pts = [(0.10, 0.56), (0.34, 0.56), (0.40, 0.56), (0.45, 0.34), (0.51, 0.74), (0.57, 0.20), (0.63, 0.64), (0.67, 0.56), (0.90, 0.56)]
    pts = [(m + x * (S - 2 * m), m + y * (S - 2 * m)) for x, y in pts]
    w = int(S * 0.055 * (1 - 2 * pad))
    for i in range(len(pts) - 1):
        t = i / (len(pts) - 2)
        col = tuple(int(a + (b - a) * t) for a, b in zip((61, 139, 255), (255, 90, 31)))
        d.line([pts[i], pts[i + 1]], fill=col, width=w, joint="curve")
        r = w // 2
        d.ellipse([pts[i][0] - r, pts[i][1] - r, pts[i][0] + r, pts[i][1] + r], fill=col)
    r = w // 2
    d.ellipse([pts[-1][0] - r, pts[-1][1] - r, pts[-1][0] + r, pts[-1][1] + r], fill=(255, 90, 31))
    return im.resize((size, size), Image.LANCZOS)

icon(192).save(os.path.join(OUT, "icons/icon-192.png"))
icon(512).save(os.path.join(OUT, "icons/icon-512.png"))
icon(512, pad=0.1).save(os.path.join(OUT, "icons/icon-maskable-512.png"))
icon(180).save(os.path.join(OUT, "icons/apple-touch-icon.png"))

# link preview picture (iMessage, WhatsApp, etc.): EMS cross + heartbeat on night-shift navy
def font(size):
    for f in ("arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf", "Helvetica.ttc"):
        try: return ImageFont.truetype(f, size)
        except OSError: pass
    return ImageFont.load_default(size)
def og_image():
    W, H = 1200, 630
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(10 + 9 * t), int(26 + 10 * t), int(66 - 40 * t)))
    cx, cy, a, b = 270, 300, 75, 210  # medical cross: two bars
    d.rounded_rectangle([cx - a, cy - b, cx + a, cy + b], 24, fill=(61, 139, 255))
    d.rounded_rectangle([cx - b, cy - a, cx + b, cy + a], 24, fill=(61, 139, 255))
    pts = [(cx - 160, cy), (cx - 60, cy), (cx - 35, cy - 70), (cx - 5, cy + 80), (cx + 25, cy - 120), (cx + 55, cy + 40), (cx + 75, cy), (cx + 160, cy)]
    d.line(pts, fill="white", width=16, joint="curve")
    d.text((556, 196), "SHIFT READY", font=font(84), fill="white")
    d.text((564, 310), "EMT & Fire study", font=font(52), fill=(154, 190, 255))
    d.text((564, 390), "Short lessons · quizzes · NREMT prep", font=font(34), fill=(205, 214, 230))
    ecg = [(0, 560), (520, 560), (560, 560), (585, 520), (615, 600), (645, 490), (675, 575), (700, 560), (W, 560)]
    for i in range(len(ecg) - 1):
        t = i / (len(ecg) - 2)
        col = tuple(int(x + (y - x) * t) for x, y in zip((61, 139, 255), (255, 90, 31)))
        d.line([ecg[i], ecg[i + 1]], fill=col, width=8)
    im.save(os.path.join(OUT, "og-image.png"))
og_image()

print("built", BUILD, os.path.getsize(os.path.join(OUT, "index.html")) // 1024, "KB")
