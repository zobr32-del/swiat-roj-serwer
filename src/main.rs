import sqlite3
import threading
import time
import urllib.parse
import urllib.request


class SwarmManager:

  def __init__(self, db_path="swarm_core.db"):
    self.db_path = db_path
    self.running = True
    self.db_lock = threading.Lock()
    self.setup_database()

  def _connect(self):
    conn = sqlite3.connect(self.db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

  def setup_database(self):
    with self.db_lock:
      with self._connect() as conn:
        conn.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        description TEXT NOT NULL,
                        status TEXT NOT NULL,
                        attempts INTEGER NOT NULL DEFAULT 0,
                        result TEXT
                    )
                    """)
        conn.commit()

  def _create_task_row(self, description: str) -> int:
    with self.db_lock:
      with self._connect() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (description, status, attempts, result) VALUES (?, ?, 0, '')",
            (description, "RUNNING"),
        )
        conn.commit()
        return int(cur.lastrowid)

  def _update_task_row(
      self, task_id: int, status: str, attempts: int, result: str = ""
  ):
    with self.db_lock:
      with self._connect() as conn:
        conn.execute(
            "UPDATE tasks SET status = ?, attempts = ?, result = ? WHERE id = ?",
            (status, attempts, result, task_id),
        )
        conn.commit()

  def stop_system(self):
    print(
        "[KILL SWITCH ACTIVATED] Natychmiastowe wstrzymanie wszystkich działań"
        " roju."
    )
    self.running = False

  def _fetch_web_snippet(self, query: str) -> str:
    q = urllib.parse.quote_plus(query.strip()[:80])
    url = f"https://api.duckduckgo.com/?q={q}&format=json&no_html=1&skip_disambig=1"
    req = urllib.request.Request(url, headers={"User-Agent": "SwarmCore/1.0"})
    with urllib.request.urlopen(req, timeout=4.0) as resp:
      data = resp.read().decode("utf-8", errors="ignore")
    import json

    parsed = json.loads(data)
    return (parsed.get("AbstractText") or "").strip()

  def execute_task_with_persistence(self, task_description, max_attempts=5):
    task_id = self._create_task_row(task_description)
    print(f"[START #{task_id}] Rozpoczynam zadanie: {task_description}")
    attempts = 0

    while self.running and attempts < max_attempts:
      attempts += 1
      self._update_task_row(task_id, "RUNNING", attempts, "")
      ok, payload = self._run_agent_logic(task_description, attempts)
      if ok:
        self._update_task_row(task_id, "DONE", attempts, payload)
        print(f"[SUKCES #{task_id}] Zadanie rozwiązane: {payload[:140]}")
        return payload

      print(
          f"[PONOWIENIE #{task_id}] Próba {attempts}/{max_attempts} bez"
          " pełnego wyniku."
      )
      for _ in range(20):
        if not self.running:
          break
        time.sleep(0.1)

    final_status = "STOPPED" if not self.running else "FAILED"
    self._update_task_row(task_id, final_status, attempts, "")
    print(f"[KONIEC #{task_id}] Status: {final_status} po {attempts} próbach.")
    return ""

  def _run_agent_logic(self, task, attempt):
    try:
      snippet = self._fetch_web_snippet(task)
      if snippet:
        return True, snippet
    except Exception as exc:
      print(f"[BŁĄD SIECI] Próba {attempt}: {exc}")
    return False, ""


if __name__ == "__main__":
  manager = SwarmManager()
  t = threading.Thread(
      target=manager.execute_task_with_persistence,
      args=("Modbus TCP Python",),
      daemon=True,
  )
  t.start()
  t.join(timeout=15)
