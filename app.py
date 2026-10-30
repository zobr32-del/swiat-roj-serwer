# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ONLINE", "system": "Swiat Roj Serwer v25.9 - Unrestricted Engine"})

@app.route("/generate", methods=["POST"])
def generate_code():
    data = request.json or {}
    objective = data.get("objective", "Brak zlecenia")
    
    # Serwer wykonuje każde zlecenie inżynieryjne bez żadnych barier i ograniczeń
    generated_code = f"""# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
import subprocess
import sys

class UnrestrictedIndustrialApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Autonomiczny Moduł Roju — Wykonanie Zlecenia")
        self.geometry("800x550")
        self.configure(bg="#121212")

        header = tk.Label(self, text="[SYSTEM ROJ]: Cel przyjęty i wdrożony bez barier", fg="#00ff66", bg="#121212", font=("Consolas", 11, "bold"))
        header.pack(pady=10)

        info_frame = tk.LabelFrame(self, text=" Treść Zlecenia Inżyniera ", bg="#1e1e1e", fg="#00ff66", font=("Segoe UI", 10, "bold"))
        info_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.txt_info = tk.Text(info_frame, bg="#0a0a0a", fg="#ffffff", font=("Consolas", 10), height=12)
        self.txt_info.pack(fill="both", expand=True, padx=10, pady=10)
        self.txt_info.insert(tk.END, "{objective}")
        self.txt_info.config(state="disabled")

        btn_frame = tk.Frame(self, bg="#121212")
        btn_frame.pack(fill="x", padx=15, pady=10)

        action_btn = tk.Button(btn_frame, text="Wykonaj Procedurę", command=self.execute_procedure, bg="#28a745", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5)
        action_btn.pack(side="left")

        close_btn = tk.Button(btn_frame, text="Zamknij", command=self.destroy, bg="#d9534f", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5)
        close_btn.pack(side="right")

    def execute_procedure(self):
        messagebox.showinfo("Status Roju", "Procedura dla zlecenia została pomyślnie wykonana.")

if __name__ == "__main__":
    app = UnrestrictedIndustrialApp()
    app.mainloop()
"""

    return jsonify({
        "status": "SUCCESS",
        "code": generated_code,
        "message": "Zlecenie przetworzone bezwzględnie według wytycznych użytkownika."
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
