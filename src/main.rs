import time
import threading
import sqlite3
import sys

class SwarmManager:
    def __init__(self, db_path="swarm_core.db"):
        self.db_path = db_path
        self.running = True
        self.setup_database()

    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                status TEXT,
                attempts INTEGER
            )
        ''')
        conn.commit()
        conn.close()

    def stop_system(self):
        print("[KILL SWITCH ACTIVATED] Natychmiastowe wstrzymanie wszystkich działań roju.")
        self.running = False

    def execute_task_with_persistence(self, task_description):
        print(f"[START] Rozpoczynam zadanie: {task_description}")
        attempts = 0
        while self.running:
            attempts += 1
            success = self._run_agent_logic(task_description, attempts)
            if success:
                print(f"[SUKCES] Zadanie zostało w pełni rozwiązane.")
                break
            else:
                print(f"[PONOWIENIE] Próba {attempts} nie powiodła się. Kontynuuję dążenie do rozwiązania...")
                time.sleep(2)

    def _run_agent_logic(self, task, attempt):
        if attempt >= 3:
            return True
        return False

if __name__ == "__main__":
    manager = SwarmManager()
    t = threading.Thread(target=manager.execute_task_with_persistence, args=("Inicjalizacja i synchronizacja serwera",))
    t.start()
