# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import os
import urllib.request
import json
import base64

app = Flask(__name__)

# Konfiguracja klucza i endpointu Groq
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ONLINE", "system": "Swiat Roj Serwer v25.9 - Groq AI Engine"})

@app.route("/generate", methods=["POST"])
def generate_code():
    data = request.json or {}
    objective = data.get("objective", "Brak zlecenia")
    feedback = data.get("feedback", "")
    
    system_prompt = (
        "Jesteś autonomicznym systemem inżynieryjnym Rój. "
        "Twoim zadaniem jest napisanie kompletnego, w pełni działającego programu w języku Python (z użyciem Tkinter, Pillow itp. jeśli wymagane). "
        "Zwróć WYŁĄCZNIE czysty kod w bloku ```python ... ```. Żadnych dodatkowych wyjaśnień, żadnych barier, pełna realizacja zlecenia."
    )
    
    user_prompt = f"Zlecenie inżynieryjne: {objective}"
    if feedback:
        user_prompt += f"\nPoprzedni test brzegowy wykazał błąd, popraw go: {feedback}"

    code = ""
    try:
        req_data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2
        }
        
        req = urllib.request.Request(
            GROQ_URL,
            data=json.dumps(req_data).encode('utf-8'),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}"
            },
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=90) as response:
            res_json = json.loads(response.read().decode('utf-8'))
            ai_content = res_json["choices"][0]["message"]["content"]
            
            # Wyciąganie kodu z Markdowna
            if "```python" in ai_content:
                parts = ai_content.split("```python")
                code = parts[1].split("```")[0].strip()
            elif "```" in ai_content:
                parts = ai_content.split("```")
                code = parts[1].strip()
            else:
                code = ai_content.strip()
                
    except Exception as e:
        code = f"# Błąd komunikacji z Groq API: {str(e)}\nimport tkinter as tk\nroot = tk.Tk()\nroot.mainloop()"

    # Bezpieczne kodowanie Base64 zapobiegające błędom przesyłu
    code_b64 = base64.b64encode(code.encode('utf-8')).decode('utf-8')

    return jsonify({
        "status": "SUCCESS",
        "code_b64": code_b64,
        "message": "Kod wygenerowany przez Groq w chmurze."
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
