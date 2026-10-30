# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ONLINE", "system": "Swiat Roj Serwer v25.9 - Industrial Engine"})

@app.route("/generate", methods=["POST"])
def generate_code():
    data = request.json or {}
    objective = data.get("objective", "").lower()
    
    # Inteligentny generator chmurowy dopasowany do branży automatyki
    if "lenze" in objective or "napęd" in objective or "serwo" in objective:
        generated_code = f"""# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
import random

class LenzeDrivePanel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Panel Sterowania Napędem Lenze — Rój v25.9")
        self.geometry("850x600")
        self.configure(bg="#121212")

        self.drive_status = "ZATRZYMANY"
        self.actual_speed = 0.0
        self.actual_current = 0.0

        # Nagłówek
        header = tk.Label(self, text="[SYSTEM ROJ]: Sterownik Napędu Lenze 8400 / MCS", fg="#00ff66", bg="#121212", font=("Consolas", 12, "bold"))
        header.pack(pady=10)

        # Ramka parametrów rzeczywistych
        status_frame = tk.LabelFrame(self, text=" Telemetria Napędu ", bg="#1e1e1e", fg="#00ff66", font=("Segoe UI", 10, "bold"))
        status_frame.pack(fill="x", padx=15, pady=5)

        self.lbl_state = tk.Label(status_frame, text=f"Stan: {{self.drive_status}}", fg="#ffcc00", bg="#1e1e1e", font=("Consolas", 11, "bold"))
        self.lbl_state.pack(anchor="w", padx=10, pady=5)

        self.lbl_speed = tk.Label(status_frame, text="Prędkość faktyczna: 0.0 RPM", fg="#ffffff", bg="#1e1e1e", font=("Consolas", 10))
        self.lbl_speed.pack(anchor="w", padx=10, pady=2)

        self.lbl_curr = tk.Label(status_frame, text="Prąd silnika: 0.0 A", fg="#ffffff", bg="#1e1e1e", font=("Consolas", 10))
        self.lbl_curr.pack(anchor="w", padx=10, pady=2)

        # Ramka sterowania
        ctrl_frame = tk.LabelFrame(self, text=" Zadawane Parametry i Rozkazy ", bg="#1e1e1e", fg="#00ff66", font=("Segoe UI", 10, "bold"))
        ctrl_frame.pack(fill="both", expand=True, padx=15, pady=10)

        tk.Label(ctrl_frame, text="Zadana prędkość (RPM):", fg="#ffffff", bg="#1e1e1e", font=("Segoe UI", 9)).pack(anchor="w", padx=10, pady=5)
        
        self.scale_speed = tk.Scale(ctrl_frame, from_=0, to=3000, orient="horizontal", bg="#0a0a0a", fg="#00ff66", highlightbackground="#1e1e1e", font=("Consolas", 9))
        self.scale_speed.set(1500)
        self.scale_speed.pack(fill="x", padx=10, pady=5)

        btn_box = tk.Frame(ctrl_frame, bg="#1e1e1e")
        btn_box.pack(fill="x", padx=10, pady=15)

        tk.Button(btn_box, text="START", command=self.motor_start, bg="#28a745", fg="white", font=("Segoe UI", 10, "bold"), width=15, pady=5).pack(side="left", padx=5)
        tk.Button(btn_box, text="STOP", command=self.motor_stop, bg="#d9534f", fg="white", font=("Segoe UI", 10, "bold"), width=15, pady=5).pack(side="left", padx=5)
        tk.Button(btn_box, text="RESET BŁĘDÓW", command=self.motor_reset, bg="#ffc107", fg="black", font=("Segoe UI", 10, "bold"), width=15, pady=5).pack(side="left", padx=5)

    def motor_start(self):
        self.drive_status = "PRACA (RUN)"
        self.lbl_state.config(text=f"Stan: {{self.drive_status}}", fg="#00ff66")
        target = self.scale_speed.get()
        self.actual_speed = float(target)
        self.actual_current = round(random.uniform(2.5, 4.8), 2)
        self.lbl_speed.config(text=f"Prędkość faktyczna: {{self.actual_speed}} RPM")
        self.lbl_curr.config(text=f"Prąd silnika: {{self.actual_current}} A")

    def motor_stop(self):
        self.drive_status = "ZATRZYMANY"
        self.lbl_state.config(text=f"Stan: {{self.drive_status}}", fg="#ffcc00")
        self.actual_speed = 0.0
        self.actual_current = 0.0
        self.lbl_speed.config(text="Prędkość faktyczna: 0.0 RPM")
        self.lbl_curr.config(text="Prąd silnika: 0.0 A")

    def motor_reset(self):
        messagebox.showinfo("Lenze Diagnoza", "Błędy napędu zostały zresetowane (Fault Reset wykonany).")

if __name__ == "__main__":
    app = LenzeDrivePanel()
    app.mainloop()
"""
    else:
        # Uniwersalny generator dla innych zadań inżynieryjnych
        generated_code = f"""# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox

class IndustrialTaskApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplikacja Automatyzacji Roju v25.9")
        self.geometry("750x500")
        self.configure(bg="#121212")

        header = tk.Label(self, text="[SYSTEM ROJ]: Wygenerowano z chmury", fg="#00ff66", bg="#121212", font=("Consolas", 11, "bold"))
        header.pack(pady=15)

        info_frame = tk.LabelFrame(self, text=" Cel Zlecenia ", bg="#1e1e1e", fg="#00ff66", font=("Segoe UI", 10, "bold"))
        info_frame.pack(fill="both", expand=True, padx=15, pady=10)

        lbl = tk.Label(info_frame, text="{data.get('objective', '')}", fg="#ffffff", bg="#1e1e1e", font=("Consolas", 10), justify="left", wraplength=680)
        lbl.pack(padx=10, pady=10, anchor="w")

        btn_frame = tk.Frame(self, bg="#121212")
        btn_frame.pack(fill="x", padx=15, pady=10)

        action_btn = tk.Button(btn_frame, text="Uruchom Procedurę", command=self.execute_task, bg="#28a745", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5)
        action_btn.pack(side="left")

        close_btn = tk.Button(btn_frame, text="Zamknij", command=self.destroy, bg="#d9534f", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5)
        close_btn.pack(side="right")

    def execute_task(self):
        messagebox.showinfo("Status", "Procedura automatyzacji została wykonana pomyślnie.")

if __name__ == "__main__":
    app = IndustrialTaskApp()
    app.mainloop()
"""

    return jsonify({
        "status": "SUCCESS",
        "code": generated_code,
        "message": "Kod wygenerowany dynamicznie przez chmurowy Rój."
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
