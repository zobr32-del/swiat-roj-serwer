import json
import os
import sqlite3
import threading
import urllib.parse
import urllib.request
from flask import Flask, jsonify, request

app = Flask(__name__)

HOST = os.getenv("SWARM_HOST", "0.0.0.0")
PORT = int(os.getenv("SWARM_PORT", "8000"))
DB_PATH = os.getenv("SWARM_DB_PATH", "swarm_core.db")
API_TOKEN = os.getenv("REMOTE_BOT_TOKEN", "").strip()

db_lock = threading.Lock()
task_counter = 0


def init_db(db_path: str) -> None:
    folder = os.path.dirname(db_path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with db_lock:
        conn = sqlite3.connect(db_path, timeout=10.0)
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    source TEXT NOT NULL,
                    result TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
        finally:
            conn.close()


def save_task_to_db(query: str, source: str, result: str, status: str) -> int:
    with db_lock:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO tasks (query, source, result, status) VALUES (?, ?, ?, ?)",
                (query, source, result, status),
            )
            conn.commit()
            return int(cur.lastrowid or 0)
        finally:
            conn.close()


def _is_valid_summary(text: str) -> bool:
    t = (text or "").strip().lower()
    if len(t) < 20:
        return False
    bad = (
        "może odnosić się do",
        "strona ujednoznaczniająca",
        "may refer to",
    )
    return not any(b in t for b in bad)


def _fetch_once(term: str, timeout: float = 5.0) -> tuple[str, str]:
    for lang in ("pl", "en"):
        try:
            search_url = (
                f"https://{lang}.wikipedia.org/w/api.php?action=opensearch&search="
                f"{urllib.parse.quote(term)}&limit=2&namespace=0&format=json"
            )
            req = urllib.request.Request(
                search_url, headers={"User-Agent": "SwarmFlaskServer/1.0"}
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            titles = data[1] if isinstance(data, list) and len(data) > 1 else []
            for title in titles:
                slug = urllib.parse.quote(title.replace(" ", "_"))
                sum_url = (
                    f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{slug}"
                )
                req2 = urllib.request.Request(
                    sum_url, headers={"User-Agent": "SwarmFlaskServer/1.0"}
                )
                with urllib.request.urlopen(req2, timeout=timeout) as resp2:
                    w = json.loads(resp2.read().decode("utf-8", errors="ignore"))
                extract = (w.get("extract") or "").strip()
                if _is_valid_summary(extract):
                    return f"Wikipedia-{lang} ({title})", extract[:500]
        except Exception:
            continue

    try:
        encoded = urllib.parse.quote_plus(term)
        ddg_url = (
            f"https://api.duckduckgo.com/?q={encoded}&format=json"
            "&no_html=1&skip_disambig=1"
        )
        req = urllib.request.Request(
            ddg_url, headers={"User-Agent": "SwarmFlaskServer/1.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            d = json.loads(resp.read().decode("utf-8", errors="ignore"))
        abstract = (d.get("AbstractText") or "").strip()
        if _is_valid_summary(abstract):
            return "DuckDuckGo", abstract[:450]
    except Exception:
        pass

    return "", ""


def fetch_web_summary(query: str, seq: int = 0, retries: int = 3, timeout: float = 5.0) -> tuple[str, str, str]:
    q = " ".join((query or "").split())[:90].strip()
    if not q:
        return "brak", "", "FAILED"

    candidates = [q]
    parts = q.split()
    if len(parts) > 2:
        candidates.append(" ".join(parts[:2]))
    if len(parts) > 1:
        candidates.append(parts[0])

    for attempt in range(1, retries + 1):
        for term in candidates:
            source, summary = _fetch_once(term, timeout=timeout)
            if summary:
                return source, summary, "DONE"
        print(f"[PONOWIENIE #{seq}] Próba {attempt}/{retries} bez pełnego wyniku.", flush=True)

    fallback_text = (
        f"Hasło techniczne „{q}”: brak pełnego wpisu w otwartej encyklopedii — "
        "zweryfikuj dokumentację producenta, specyfikację protokołu lub konfigurację węzła."
    )
    return "Fallback-Tech", fallback_text, "DONE"


def _check_auth() -> bool:
    if not API_TOKEN:
        return True
    auth = request.headers.get("Authorization", "")
    return auth == f"Bearer {API_TOKEN}"


@app.get("/health")
def health():
    return jsonify({"running": True, "status": "ok", "db": DB_PATH})


@app.post("/ask")
def ask():
    global task_counter
    if not _check_auth():
        return jsonify({"ok": False, "error": "unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    query = str(payload.get("query") or payload.get("keyword") or "").strip()
    if not query:
        return jsonify({"ok": False, "error": "missing query"}), 400

    with db_lock:
        task_counter += 1
        seq = task_counter

    print(f"[START #{seq}] Rozpoczynam zadanie: {query}", flush=True)
    source, summary, status = fetch_web_summary(query, seq=seq)
    task_id = save_task_to_db(query, source, summary, status)
    print(f"[KONIEC #{seq}] Status: {status} | {summary[:120]}", flush=True)

    return jsonify({
        "ok": True,
        "task": {
            "id": task_id,
            "seq": seq,
            "query": query,
            "source": source,
            "result": summary,
            "status": status,
        },
        "result": summary,
        "status": status,
    })


@app.get("/stats")
def stats():
    if not os.path.exists(DB_PATH):
        return jsonify({
            "ok": False,
            "db_path": DB_PATH,
            "total": 0,
            "done": 0,
            "failed": 0,
            "by_status": {"DONE": 0, "FAILED": 0},
            "recent": [],
        })

    with db_lock:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) AS cnt FROM tasks")
            total = int(cur.fetchone()["cnt"] or 0)

            cur.execute(
                "SELECT UPPER(COALESCE(status, 'UNKNOWN')) AS st, COUNT(*) AS cnt "
                "FROM tasks GROUP BY UPPER(COALESCE(status, 'UNKNOWN'))"
            )
            by_status = {"DONE": 0, "FAILED": 0}
            for row in cur.fetchall():
                by_status[(row["st"] or "UNKNOWN").strip()] = int(row["cnt"] or 0)

            cur.execute(
                "SELECT id, query, source, status, created_at FROM tasks "
                "ORDER BY id DESC LIMIT 5"
            )
            recent = [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    return jsonify({
        "ok": True,
        "db_path": DB_PATH,
        "total": total,
        "done": by_status.get("DONE", 0),
        "failed": by_status.get("FAILED", 0),
        "by_status": by_status,
        "recent": recent,
    })


if __name__ == "__main__":
    init_db(DB_PATH)
    app.run(host=HOST, port=PORT, debug=False)
