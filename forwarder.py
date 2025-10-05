import re, yaml, requests, threading, time, sqlite3, os
from langdetect import detect, LangDetectException

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

CONFIG = load_config()
_last_load = os.path.getmtime(CONFIG_PATH)

def _reload_worker():
    global CONFIG, _last_load
    while True:
        try:
            m = os.path.getmtime(CONFIG_PATH)
            if m != _last_load:
                CONFIG = load_config()
                _last_load = m
                print("[config] Reloaded config.yaml")
        except Exception as e:
            print("[config] reload error:", e)
        time.sleep(CONFIG.get("config_reload_seconds", 30))

threading.Thread(target=_reload_worker, daemon=True).start()

BOT_TOKEN = lambda: CONFIG.get("bot_token")
BASE_URL = lambda: f"https://api.telegram.org/bot{BOT_TOKEN()}"

# create data dir & sqlite
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "db.sqlite3")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS forwards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER,
    from_chat INTEGER,
    to_chat TEXT,
    status TEXT,
    response TEXT,
    ts DATETIME DEFAULT CURRENT_TIMESTAMP
)""")
conn.commit()

ROUTES = lambda: CONFIG.get("routes", {})
KEYWORDS = lambda: CONFIG.get("keywords", {})
HASHTAGS = lambda: CONFIG.get("hashtags", {})
DEFAULT_ROUTES = lambda: CONFIG.get("default_routes", [])
MODERATION = lambda: CONFIG.get("moderation_mode", False)
MOD_CHAT = lambda: CONFIG.get("moderator_chat")
RETRY_ATTEMPTS = lambda: int(CONFIG.get("retry_attempts", 3))
RETRY_BACKOFF = lambda: int(CONFIG.get("retry_backoff_seconds", 2))

def extract_text(channel_post):
    return channel_post.get("text") or channel_post.get("caption") or ""

def detect_lang_safe(text):
    try:
        return detect(text)
    except LangDetectException:
        return None
    except Exception:
        return None

def find_route(text):
    if not text:
        return None
    t = text.lower()
    # hashtags
    for route, tags in (HASHTAGS() or {}).items():
        for tag in tags:
            if tag.lower() in t:
                return route
    # keywords
    for route, kws in (KEYWORDS() or {}).items():
        for kw in kws:
            if re.search(r'\b' + re.escape(kw.lower()) + r'\b', t):
                return route
    # language fallback
    lang = detect_lang_safe(text)
    if lang:
        if lang.startswith("bn"):
            return "deshi"
        if lang.startswith("hi"):
            return "indian"
        if lang.startswith("ja"):
            return "japan"
        if lang.startswith("en"):
            return "all"
    return None

def _http_post(path, data):
    url = BASE_URL() + path
    try:
        r = requests.post(url, data=data, timeout=15)
        return r.status_code, r.text, r.json() if r.headers.get('content-type','').startswith('application/json') else None
    except Exception as e:
        return None, str(e), None

def forward_message_to(chat_identifier, from_chat_id, message_id):
    attempts = RETRY_ATTEMPTS()
    backoff = RETRY_BACKOFF()
    last_resp = None
    for i in range(attempts):
        status, text, jsonp = _http_post("/forwardMessage", {
            "chat_id": str(chat_identifier),
            "from_chat_id": str(from_chat_id),
            "message_id": str(message_id)
        })
        last_resp = (status, text)
        ok = False
        if jsonp and jsonp.get("ok"):
            ok = True
        cur.execute("INSERT INTO forwards (message_id, from_chat, to_chat, status, response) VALUES (?,?,?,?,?)",
                    (message_id, from_chat_id, str(chat_identifier), "ok" if ok else "fail", text[:2000]))
        conn.commit()
        if ok:
            return jsonp
        time.sleep(backoff * (2 ** i))
    return {"ok": False, "error": last_resp}

def handle_channel_post(channel_post):
    from_chat_id = channel_post['chat']['id']
    message_id = channel_post['message_id']
    text = extract_text(channel_post)
    allowed_sources = CONFIG.get('source_channels') or []
    username = channel_post['chat'].get('username')
    if allowed_sources:
        if username and ("@" + username) not in allowed_sources and str(from_chat_id) not in [str(x) for x in allowed_sources]:
            return {"ok": False, "reason": "source not allowed"}
    route = find_route(text)
    targets = []
    if route and route in ROUTES():
        targets = ROUTES()[route]
    else:
        for r in DEFAULT_ROUTES():
            targets.extend(ROUTES().get(r, []))
    if MODERATION():
        if MOD_CHAT():
            # copy to moderator chat for review
            _http_post("/copyMessage", {"chat_id": MOD_CHAT(), "from_chat_id": str(from_chat_id), "message_id": str(message_id)})
        cur.execute("INSERT INTO moderation_queue (message_id, from_chat, suggested_routes) VALUES (?,?,?)",
                    (message_id, from_chat_id, ",".join(map(str, targets))))
        conn.commit()
        return {"ok": True, "moderation": True}
    results = []
    for tgt in set(targets):
        resp = forward_message_to(tgt, from_chat_id, message_id)
        results.append({str(tgt): resp})
    return {"ok": True, "results": results}
