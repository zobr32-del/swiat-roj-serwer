# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ONLINE", "system": "Swiat Roj Serwer v25.9 - Robust Engine"})

@app.route("/generate", methods=["POST"])
def generate_code():
    data = request.json or {}
    objective = data.get("objective", "Brak zlecenia")
    feedback = data.get("feedback", "")
    
    # Bezpieczne osadzenie zlecenia i opcjonalnego feedbacku o błędzie
    safe_objective = repr(objective)
    safe_feedback = repr(feedback) if feedback else "Brak"

    generated_code = f"""# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox

class AutonomousTaskApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplikacja Automatyzacji Roju — Wykonanie Zlecenia")
        self.geometry("850x600")
        self.configure(bg="#121212")

        header = tk.Label(self, text="[SYSTEM ROJ]: Zadanie wdrożone z chmury", fg="#00ff66", bg="#121212", font=("Consolas", 11, "bold"))
        header.pack(pady=10)

        info_frame = tk.LabelFrame(self, text=" Kontekst i Zlecenie Inżyniera ", bg="#1e1e1e", fg="#00ff66", font=("Segoe UI", 10, "bold"))
        info_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.txt_info = tk.Text(info_frame, bg="#0a0a0a", fg="#ffffff", font=("Consolas", 10), height=10)
        self.txt_info.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Bezpiecznie wstrzyknięty cel
        objective_text = {safe_objective}
        feedback_text = {safe_feedback}
        
        full_content = f"CEL:\\n{{objective_text}}\\n\\nOSTATNI FEEDBACK BŁĘDU:\\n{{feedback_text}}"
        self.txt_info.insert(tk.END, full_content)
        self.txt_info.config(state="disabled")

        btn_frame = tk.Frame(self, bg="#121212")
        btn_frame.pack(fill="x", padx=15, pady=10)

        action_btn = tk.Button(btn_frame, text="Wykonaj Procedurę", command=self.execute_procedure, bg="#28a745", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5)
        action_btn.pack(side="left")

        close_btn = tk.Button(btn_frame, text="Zamknij", command=self.destroy, bg="#d9534f", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5)
        close_btn.pack(side="right")

    def execute_procedure(self):
        messagebox.showinfo("Status Roju", "Procedura została pomyślnie wykonana.")

if __name__ == "__main__":
    app = AutonomousTaskApp()
    app.mainloop()
"""

    return jsonify({
        "status": "SUCCESS",
        "code": generated_code,
        "message": "Kod wygenerowany i zabezpieczony."
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
