# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import os
import urllib.request
import json
import base64

app = Flask(__name__)

# Pobieramy klucz Gemini API ze zmiennych środowiskowych Rendera
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ONLINE", "system": "Swiat Roj Serwer v25.9 - Gemini Free Engine"})

@app.route("/generate", methods=["POST"])
def generate_code():
    data = request.json or {}
    objective = data.get("objective", "Brak zlecenia")
    feedback = data.get("feedback", "")
    
    if not GEMINI_API_KEY:
        error_code = (
            "import tkinter as tk\nfrom tkinter import messagebox\n"
            "root = tk.Tk()\nroot.withdraw()\n"
            "messagebox.showerror('Błąd Roju', 'Brak skonfigurowanego klucza GEMINI_API_KEY na serwerze Render!')\n"
            "root.destroy()"
        )
        return jsonify({"status": "SUCCESS", "code_b64": base64.b64encode(error_code.encode('utf-8')).decode('utf-8')})

    system_prompt = (
        "Jesteś bezkompromisowym systemem inżynieryjnym Rój. "
        "Twoim zadaniem jest napisanie W CAŁOŚCI zaawansowanego, kompletnego programu w języku Python (Tkinter + Pillow) "
        "zgodnego ze zleceniem użytkownika. "
        "ABSOLUTNIE ZABRONIONE jest zwracanie uproszczonych szkieletów, pustych okien typu `tk.Tk()` czy fragmentów z placeholderami. "
        "Program musi zawierać pełną logikę interfejsu, przyciski, obsługę zdarzeń i funkcje. "
        "Zwróć WYŁĄCZNIE czysty kod w bloku ```python ... ```."
    )
    
    full_prompt = f"{system_prompt}\n\nZlecenie inżynieryjne: {objective}"
    if feedback:
        full_prompt += f"\nPoprzedni test brzegowy wykazał błąd, popraw go: {feedback}"

    code = ""
    try:
        req_data = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }]
        }
        
        req = urllib.request.Request(
            GEMINI_URL,
            data=json.dumps(req_data).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=90) as response:
            res_json = json.loads(response.read().decode('utf-8'))
            ai_content = res_json["candidates"][0]["content"]["parts"][0]["text"]
            
            if "```python" in ai_content:
                parts = ai_content.split("```python")
                code = parts[1].split("```")[0].strip()
            elif "```" in ai_content:
                parts = ai_content.split("```")
                code = parts[1].strip()
            else:
                code = ai_content.strip()
                
    except Exception as e:
        err_str = str(e).replace('"', "'")
        code = (
            f"import tkinter as tk\nfrom tkinter import messagebox\n"
            f"root = tk.Tk()\nroot.withdraw()\n"
            f"messagebox.showerror('Błąd Gemini API', 'Wystąpił błąd na serwerze:\\n{err_str}')\n"
            f"root.destroy()"
        )

    code_b64 = base64.b64encode(code.encode('utf-8')).decode('utf-8')

    return jsonify({
        "status": "SUCCESS",
        "code_b64": code_b64,
        "message": "Wygenerowano kod przez darmowe API Gemini."
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
