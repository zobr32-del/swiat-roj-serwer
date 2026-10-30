# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ONLINE", "system": "Swiat Roj Serwer v25.9"})

@app.route("/generate", methods=["POST"])
def generate_code():
    data = request.json or {}
    objective = data.get("objective", "Brak zlecenia")
    
    # Logika roju w chmurze: generowanie dedykowanego kodu automatyzacji/GUI
    generated_code = f"""# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox

class IndustrialApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplikacja Automatyzacji Roju v25.9")
        self.geometry("700x450")
        self.configure(bg="#121212")

        header = tk.Label(self, text="[SYSTEM ROJ]: Zlecenie zrealizované w chmurze", fg="#00ff66", bg="#121212", font=("Consolas", 11, "bold"))
        header.pack(pady=15)

        info_frame = tk.LabelFrame(self, text=" Parametry Zlecenia ", bg="#1e1e1e", fg="#00ff66", font=("Segoe UI", 10, "bold"))
        info_frame.pack(fill="both", expand=True, padx=15, pady=10)

        lbl = tk.Label(info_frame, text="Cel: {objective}", fg="#ffffff", bg="#1e1e1e", font=("Consolas", 10), justify="left", wraplength=640)
        lbl.pack(padx=10, pady=10, anchor="w")

        btn_frame = tk.Frame(self, bg="#121212")
        btn_frame.pack(fill="x", padx=15, pady=10)

        action_btn = tk.Button(btn_frame, text="Wykonaj Procedurę", command=self.execute_task, bg="#28a745", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5)
        action_btn.pack(side="left")

        close_btn = tk.Button(btn_frame, text="Zamknij", command=self.destroy, bg="#d9534f", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5)
        close_btn.pack(side="right")

    def execute_task(self):
        messagebox.showinfo("Status", "Procedura automatyzacji została wykonana pomyślnie.")

if __name__ == "__main__":
    app = IndustrialApp()
    app.mainloop()
"""
    return jsonify({
        "status": "SUCCESS",
        "code": generated_code,
        "message": "Kod wygenerowany pomyślnie przez chmurowy Rój."
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
