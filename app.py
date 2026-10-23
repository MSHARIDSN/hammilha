import json
import os
import re
import tempfile
import urllib.parse
import urllib.request
import uuid

from flask import Flask, request, send_file, jsonify, Response, after_this_request
import yt_dlp

app = Flask(__name__)
DOWNLOAD_DIR = tempfile.mkdtemp(prefix="tt_")
TIKTOK_RE = re.compile(r"^https?://([a-z0-9-]+\.)*tiktok\.com/", re.I)

PAGE = r"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>حمّلها — محمّل تيك توك</title>
<meta name="description" content="حمّل مقاطع تيك توك مجاناً بصيغة MP4 من جوالك بدون تسجيل.">
<meta name="theme-color" content="#F1F3F6">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lalezar&family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap">
<style>
  :root {
    --bg:#F1F3F6; --card:#FFFFFF; --ink:#14172B; --muted:#4A5068; --line:#DDE1EA;
    --accent:#E8462A; --accent-soft:#FFD3C8; --soft:#EEF0F5;
    --display:'Lalezar','IBM Plex Sans Arabic',Tahoma,sans-serif;
    --body:'IBM Plex Sans Arabic',Tahoma,sans-serif;
  }
  * { box-sizing:border-box; }
  [hidden] { display:none !important; }
  html,body { margin:0; }
  body { font-family:var(--body); color:var(--ink); background:var(--bg); min-height:100vh;
         display:flex; flex-direction:column; -webkit-text-size-adjust:100%; }
  a { color:var(--ink); text-decoration:none; } a:hover { color:var(--accent); }
  button:focus-visible, a:focus-visible, summary:focus-visible { outline:3px solid var(--ink); outline-offset:3px; }
  .wrap { width:100%; max-width:1080px; margin:0 auto; }
  header { padding:20px max(20px, env(safe-area-inset-right)) 20px max(20px, env(safe-area-inset-left)); }
  header .wrap { display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap; }
  .logo { display:flex; align-items:center; gap:10px; }
  .logo-mark { width:40px; height:40px; border-radius:12px; background:var(--accent); display:flex; align-items:center; justify-content:center; }
  .logo-text { font-family:var(--display); font-size:30px; line-height:1; }
  nav { display:flex; gap:20px; font-size:15px; font-weight:500; }
  main { flex:1; display:flex; flex-direction:column; align-items:center; gap:72px;
         padding:32px max(20px, env(safe-area-inset-right)) 64px max(20px, env(safe-area-inset-left)); }
  .hero { width:100%; max-width:760px; display:flex; flex-direction:column; align-items:center; gap:28px; text-align:center; }
  .pill { background:var(--card); border:1px solid var(--line); border-radius:999px; padding:6px 14px; font-size:14px; font-weight:600; color:var(--muted); }
  h1 { margin:0; font-family:var(--display); font-weight:400; font-size:clamp(40px,9vw,72px); line-height:1.15; text-wrap:balance; }
  h1 span { color:var(--accent); }
  .lead { margin:0; font-size:18px; line-height:1.8; color:var(--muted); max-width:560px; }
  form { width:100%; }
  .field { display:flex; flex-wrap:wrap; gap:8px; background:var(--card); border:2px solid var(--line); border-radius:20px; padding:8px; }
  .field:focus-within { border-color:var(--accent); box-shadow:0 0 0 3px var(--accent-soft); }
  .field input { flex:999 1 240px; min-width:0; border:0; background:transparent; font-family:inherit; font-size:17px;
                 padding:14px 12px; color:var(--ink); direction:ltr; text-align:left; outline:none; }
  .field input::placeholder { color:#8A90A6; }
  .actions { flex:1 1 auto; display:flex; gap:8px; }
  .btn { min-height:52px; border:0; border-radius:14px; font-family:inherit; font-size:16px; font-weight:700; cursor:pointer;
         display:flex; align-items:center; justify-content:center; gap:8px; padding:0 20px; }
  .btn-soft { background:var(--soft); color:var(--ink); font-weight:600; flex:0 0 auto; }
  .btn-main { background:var(--accent); color:#fff; flex:1 1 auto; font-size:17px; padding:0 28px; }
  .btn-dark { background:var(--ink); color:#fff; flex:1 1 200px; }
  .btn-line { background:var(--card); color:var(--ink); border:2px solid var(--line); font-weight:600; flex:0 1 auto; }
  .btn:disabled { opacity:.7; cursor:wait; }
  .spin { animation:spin .9s linear infinite; }
  @keyframes spin { to { transform:rotate(360deg); } }
  @media (prefers-reduced-motion: reduce) { .spin { animation:none; } }
  .alert { width:100%; display:flex; align-items:center; gap:10px; background:#FFF1EE; border:1px solid #F6B8AA; color:#A3260F;
           border-radius:14px; padding:14px 16px; font-size:15px; font-weight:500; text-align:right; }
  .result { width:100%; display:flex; flex-wrap:wrap; gap:20px; background:var(--card); border:1px solid var(--line);
            border-radius:24px; padding:16px; text-align:right; box-shadow:0 12px 32px rgba(20,23,43,.08); }
  .thumb { flex:0 0 132px; height:200px; max-width:100%; border-radius:16px; background:var(--ink); object-fit:cover; }
  .result-body { flex:999 1 220px; min-width:0; display:flex; flex-direction:column; gap:12px; justify-content:center; }
  .ready { align-self:flex-start; background:#E6F6EC; color:#17663A; font-size:13px; font-weight:700; border-radius:999px; padding:4px 12px; }
  .title { font-size:18px; font-weight:700; line-height:1.6; overflow-wrap:anywhere; }
  .author { font-size:15px; color:var(--muted); direction:ltr; text-align:right; }
  .row { display:flex; flex-wrap:wrap; gap:10px; margin-top:4px; }
  h2 { margin:0; font-family:var(--display); font-weight:400; font-size:36px; text-align:center; }
  .steps-sec { width:100%; max-width:1080px; display:flex; flex-direction:column; gap:28px; }
  .steps { display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:16px; }
  .step { background:var(--card); border-radius:20px; padding:24px; display:flex; flex-direction:column; gap:10px; }
  .step b { font-family:var(--display); font-weight:400; font-size:40px; line-height:1; color:var(--accent); }
  .step strong { font-size:18px; }
  .step p, details p { margin:0; font-size:15px; line-height:1.8; color:var(--muted); }
  .faq { width:100%; max-width:760px; display:flex; flex-direction:column; gap:12px; }
  .faq h2 { margin-bottom:12px; }
  details { background:var(--card); border-radius:16px; padding:18px 20px; }
  summary { cursor:pointer; font-size:17px; font-weight:700; }
  details p { margin-top:12px; }
  footer { border-top:1px solid var(--line); padding:28px max(20px, env(safe-area-inset-right)) calc(28px + env(safe-area-inset-bottom)) max(20px, env(safe-area-inset-left)); }
  footer .wrap { display:flex; flex-wrap:wrap; justify-content:space-between; gap:12px; font-size:14px; color:var(--muted); }
  footer strong { color:var(--ink); direction:ltr; unicode-bidi:isolate; }
  .sr { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
</style>
</head>
<body>
<header>
  <div class="wrap">
    <div class="logo">
      <div class="logo-mark" aria-hidden="true">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v11"/><path d="M7 10l5 5 5-5"/><path d="M5 20h14"/></svg>
      </div>
      <span class="logo-text">حمّلها</span>
    </div>
    <nav>
      <a href="#how">طريقة الاستخدام</a>
      <a href="#faq">أسئلة شائعة</a>
    </nav>
  </div>
</header>

<main>
  <section class="hero">
    <span class="pill">مجاني · بدون تسجيل · يعمل من الجوال</span>
    <h1>حمّل مقاطع تيك توك <span>بضغطة وحدة</span></h1>
    <p class="lead">انسخ رابط المقطع من التطبيق، الصقه هنا، ويوصلك ملف MP4 جاهز تحفظه في جوالك.</p>

    <form id="form" novalidate>
      <label for="url" class="sr">رابط مقطع تيك توك</label>
      <div class="field">
        <input id="url" type="url" inputmode="url" autocomplete="off" placeholder="https://www.tiktok.com/@user/video/…">
        <div class="actions">
          <button type="button" class="btn btn-soft" id="paste">لصق</button>
          <button type="submit" class="btn btn-main" id="go">
            <svg id="spinner" class="spin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" style="display:none" aria-hidden="true"><path d="M21 12a9 9 0 1 1-9-9"/></svg>
            <span id="goLabel">تحميل</span>
          </button>
        </div>
      </div>
    </form>

    <div class="alert" id="alert" role="alert" hidden>
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#A3260F" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 8v5"/><path d="M12 16.5v.01"/></svg>
      <span id="alertText"></span>
    </div>

    <div class="result" id="result" hidden>
      <img class="thumb" id="thumb" alt="" referrerpolicy="no-referrer" hidden>
      <div class="result-body">
        <span class="ready">جاهز للتحميل</span>
        <div class="title" id="rTitle"></div>
        <div class="author" id="rAuthor"></div>
        <div class="row">
          <button type="button" class="btn btn-dark" id="save">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11"/><path d="M7 10l5 5 5-5"/><path d="M5 20h14"/></svg>
            <span id="saveLabel">حفظ الفيديو MP4</span>
          </button>
          <button type="button" class="btn btn-line" id="again">مقطع آخر</button>
          <a class="btn btn-line" id="openLink" target="_blank" rel="noopener" hidden>افتح الفيديو</a>
        </div>
      </div>
    </div>
  </section>

  <section class="steps-sec" id="how">
    <h2>ثلاث خطوات وبس</h2>
    <div class="steps">
      <div class="step"><b>١</b><strong>انسخ الرابط</strong><p>في تيك توك اضغط «مشاركة» ثم «نسخ الرابط».</p></div>
      <div class="step"><b>٢</b><strong>الصقه هنا</strong><p>ضع الرابط في الخانة أعلى الصفحة واضغط «تحميل».</p></div>
      <div class="step"><b>٣</b><strong>احفظ المقطع</strong><p>يتحمّل الملف بصيغة MP4 مباشرة في جوالك.</p></div>
    </div>
  </section>

  <section class="faq" id="faq">
    <h2>أسئلة شائعة</h2>
    <details><summary>هل الموقع مجاني؟</summary><p>نعم، مجاني بالكامل وما يحتاج تسجيل.</p></details>
    <details><summary>وين ينحفظ المقطع في الآيفون؟</summary><p>في تطبيق «الملفات» داخل مجلد التنزيلات، ومنه تقدر تحفظه في الصور.</p></details>
    <details><summary>ليش ما تحمّل بعض المقاطع؟</summary><p>المقاطع الخاصة أو المحذوفة ما يمكن تحميلها. تأكد أن الحساب عام وأن الرابط صحيح.</p></details>
  </section>
</main>

<footer>
  <div class="wrap">
    <span>صُمّم بواسطة <strong>MSHARIDSN</strong></span>
    <span>حمّل فقط مقاطعك أو المقاطع التي لديك إذن بها.</span>
  </div>
</footer>

<script>
const $ = (id) => document.getElementById(id);
const form = $('form'), urlIn = $('url'), go = $('go'), spinner = $('spinner'), goLabel = $('goLabel');
const alertBox = $('alert'), alertText = $('alertText'), result = $('result');
let current = null;

function showError(msg) { alertText.textContent = msg; alertBox.hidden = false; result.hidden = true; }
function clearError() { alertBox.hidden = true; }
function busy(on, label) { go.disabled = on; spinner.style.display = on ? '' : 'none'; goLabel.textContent = on ? (label || 'جارٍ التحقق…') : 'تحميل'; }

$('paste').onclick = async () => {
  try { urlIn.value = (await navigator.clipboard.readText()).trim(); } catch (e) { urlIn.focus(); }
};

$('again').onclick = () => { urlIn.value = ''; result.hidden = true; clearError(); current = null; urlIn.focus(); };

const TIKWM = 'https://www.tikwm.com';
const absUrl = (u) => (u && u.startsWith('/')) ? TIKWM + u : (u || '');
const postForm = (path, obj) => fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams(obj) });

// Look the video up from the visitor's own connection (cloud servers get blocked).
async function lookupInBrowser(url) {
  const res = await postForm(TIKWM + '/api/', { url, hd: '1' });
  const j = await res.json();
  if (j.code !== 0 || !j.data) throw new Error(j.msg || 'no data');
  const d = j.data;
  if (d.images && d.images.length) {
    const e = new Error('هذا المنشور صور وليس فيديو، والموقع يحمّل الفيديوهات فقط.'); e.final = true; throw e;
  }
  return { title: d.title || '', author: (d.author || {}).unique_id || '', thumbnail: absUrl(d.cover || d.origin_cover),
           video: absUrl(d.hdplay || d.play), id: String(d.id || 'video') };
}

async function lookupOnServer(url) {
  const res = await postForm('/info', { url });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'حدث خطأ، حاول مرة أخرى.');
  return data;
}

form.onsubmit = async (e) => {
  e.preventDefault();
  clearError();
  $('openLink').hidden = true;
  const url = urlIn.value.trim();
  if (!url) return showError('الصق رابط المقطع أولاً.');
  if (!/tiktok\.com\//i.test(url)) return showError('هذا ليس رابط تيك توك. انسخ الرابط من زر «مشاركة» في التطبيق.');
  busy(true);
  try {
    let data;
    try { data = await lookupInBrowser(url); }
    catch (err) { if (err.final) throw err; data = await lookupOnServer(url); }
    current = { url, video: data.video || '', id: data.id || 'video' };
    $('rTitle').textContent = data.title || 'مقطع تيك توك';
    $('rAuthor').textContent = data.author ? '@' + data.author : '';
    const t = $('thumb');
    if (data.thumbnail) { t.src = data.thumbnail; t.hidden = false; } else { t.hidden = true; }
    result.hidden = false;
  } catch (err) {
    showError(err.message);
  } finally {
    busy(false);
  }
};

async function fetchVideoBlob() {
  if (current.video) {
    try { const r = await fetch(current.video); if (r.ok) return await r.blob(); } catch (_) {}
    try { const r = await fetch('/proxy?u=' + encodeURIComponent(current.video)); if (r.ok) return await r.blob(); } catch (_) {}
  }
  const r = await postForm('/download', { url: current.url });
  if (!r.ok) {
    let msg = 'تعذّر التحميل، حاول مرة أخرى.';
    try { msg = (await r.json()).error || msg; } catch (_) {}
    throw new Error(msg);
  }
  return await r.blob();
}

$('save').onclick = async () => {
  if (!current) return;
  const btn = $('save'), label = $('saveLabel');
  btn.disabled = true; label.textContent = 'جارٍ التحميل…';
  try {
    const blob = await fetchVideoBlob();
    const name = 'hammilha_' + current.id + '.mp4';
    const file = new File([blob], name, { type: 'video/mp4' });
    if (navigator.canShare && navigator.canShare({ files: [file] })) {
      try { await navigator.share({ files: [file] }); label.textContent = 'تم ✓'; return; } catch (_) {}
    }
    const a = document.createElement('a');
    a.href = URL.createObjectURL(file); a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 10000);
    label.textContent = 'تم التحميل ✓';
  } catch (err) {
    if (current.video) {
      const link = $('openLink'); link.href = current.video; link.hidden = false;
      showError('ما قدرنا نحفظه تلقائياً. اضغط «افتح الفيديو» ثم زر المشاركة ← «حفظ الفيديو».');
      result.hidden = false;
    } else {
      showError(err.message);
    }
    label.textContent = 'حفظ الفيديو MP4';
  } finally {
    btn.disabled = false;
    setTimeout(() => { label.textContent = 'حفظ الفيديو MP4'; }, 3000);
  }
};
</script>
</body>
</html>"""


UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
TIKWM = "https://www.tikwm.com"
BAD_URL = "الرابط غير صحيح، تأكد أنه رابط من تيك توك."
NOT_FOUND = "ما قدرنا نوصل للمقطع. قد يكون خاصاً أو محذوفاً، أو الرابط غير صالح."


class SlideshowError(Exception):
    pass


def _check_url():
    url = (request.form.get("url") or "").strip()
    if not TIKTOK_RE.match(url):
        return None
    return url


def _abs(u):
    if u and u.startswith("/"):
        return TIKWM + u
    return u or ""


def tikwm_info(url):
    """Look the video up through tikwm.com (works where TikTok blocks cloud servers)."""
    q = urllib.parse.urlencode({"url": url, "hd": 1})
    req = urllib.request.Request(f"{TIKWM}/api/?{q}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        payload = json.load(r)
    d = payload.get("data")
    if payload.get("code") != 0 or not d:
        raise ValueError(payload.get("msg") or "tikwm: no data")
    if d.get("images"):
        raise SlideshowError()
    video = _abs(d.get("hdplay") or d.get("play"))
    if not video:
        raise ValueError("tikwm: no video url")
    return {
        "id": str(d.get("id") or "video"),
        "title": (d.get("title") or "")[:200],
        "author": (d.get("author") or {}).get("unique_id", ""),
        "thumbnail": _abs(d.get("cover") or d.get("origin_cover")),
        "video": video,
    }


def ytdlp_info(url):
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "noplaylist": True}) as ydl:
        meta = ydl.extract_info(url, download=False)
    return {
        "id": str(meta.get("id") or "video"),
        "title": (meta.get("description") or meta.get("title") or "")[:200],
        "author": meta.get("uploader") or meta.get("creator") or "",
        "thumbnail": meta.get("thumbnail") or "",
    }


@app.get("/")
def index():
    return Response(PAGE, mimetype="text/html")


@app.post("/info")
def info():
    url = _check_url()
    if not url:
        return jsonify(error=BAD_URL), 400
    try:
        meta = tikwm_info(url)
    except SlideshowError:
        return jsonify(error="هذا المنشور صور وليس فيديو، والموقع يحمّل الفيديوهات فقط."), 400
    except Exception:
        app.logger.exception("tikwm info failed, trying yt-dlp")
        try:
            meta = ytdlp_info(url)
        except Exception:
            app.logger.exception("yt-dlp info failed")
            return jsonify(error=NOT_FOUND), 500
    return jsonify(title=meta["title"], author=meta["author"], thumbnail=meta["thumbnail"])


PROXY_HOSTS = ("tikwm.com", "tiktokcdn.com", "tiktokcdn-us.com", "tiktokv.com", "tiktokv.us", "muscdn.com")


def _stream(upstream):
    try:
        while True:
            chunk = upstream.read(64 * 1024)
            if not chunk:
                break
            yield chunk
    finally:
        upstream.close()


@app.get("/proxy")
def proxy():
    """Relay a video file the browser found but couldn't save itself (only TikTok video hosts)."""
    target = request.args.get("u", "")
    parts = urllib.parse.urlparse(target)
    host = (parts.hostname or "").lower()
    if parts.scheme != "https" or not any(host == h or host.endswith("." + h) for h in PROXY_HOSTS):
        return jsonify(error=BAD_URL), 400
    try:
        req = urllib.request.Request(target, headers={"User-Agent": UA, "Referer": TIKWM + "/"})
        upstream = urllib.request.urlopen(req, timeout=60)
    except Exception:
        app.logger.exception("proxy fetch failed")
        return jsonify(error="تعذّر تحميل المقطع."), 502
    headers = {}
    length = upstream.headers.get("Content-Length")
    if length:
        headers["Content-Length"] = length
    return Response(_stream(upstream), mimetype="video/mp4", headers=headers)


@app.post("/download")
def download():
    url = _check_url()
    if not url:
        return jsonify(error=BAD_URL), 400

    # First choice: stream the file through tikwm.
    try:
        meta = tikwm_info(url)
        req = urllib.request.Request(meta["video"], headers={"User-Agent": UA, "Referer": TIKWM + "/"})
        upstream = urllib.request.urlopen(req, timeout=60)

        def stream():
            try:
                while True:
                    chunk = upstream.read(64 * 1024)
                    if not chunk:
                        break
                    yield chunk
            finally:
                upstream.close()

        headers = {"Content-Disposition": f'attachment; filename="hammilha_{meta["id"]}.mp4"'}
        length = upstream.headers.get("Content-Length")
        if length:
            headers["Content-Length"] = length
        return Response(stream(), mimetype="video/mp4", headers=headers)
    except SlideshowError:
        return jsonify(error="هذا المنشور صور وليس فيديو، والموقع يحمّل الفيديوهات فقط."), 400
    except Exception:
        app.logger.exception("tikwm download failed, trying yt-dlp")

    # Fallback: yt-dlp straight from TikTok.

    file_id = uuid.uuid4().hex
    opts = {
        "outtmpl": os.path.join(DOWNLOAD_DIR, file_id + ".%(ext)s"),
        "format": "best[ext=mp4]/best",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            meta = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(meta)
    except Exception:
        app.logger.exception("yt-dlp download failed")
        return jsonify(error="تعذّر تحميل المقطع. قد يكون خاصاً أو محذوفاً، أو الرابط غير صالح."), 500

    if not os.path.exists(path):
        return jsonify(error="لم يُعثر على الملف بعد التحميل."), 500

    @after_this_request
    def cleanup(response):
        try:
            os.remove(path)
        except OSError:
            pass
        return response

    ext = os.path.splitext(path)[1] or ".mp4"
    return send_file(path, as_attachment=True, download_name=f"hammilha_{meta.get('id', 'video')}{ext}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
