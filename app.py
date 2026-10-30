# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template_string
import os
import uuid
import datetime

app = Flask(__name__)

# Wirtualna tablica karteczek w pamięci serwera
# Słownik: { note_id: { "objective": "...", "status": "PENDING/DONE", "answer": "...", "timestamp": "..." } }
NOTES_BOARD = {}

@app.route("/", methods=["GET"])
def index():
    # Czytelny panel HTML do podglądu karteczek w przeglądarce
    html = """
    <!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <title>Świat Rój — Wirtualna Tablica Karteczek</title>
        <style>
            body { background: #121212; color: #00ff66; font-family: monospace; padding: 20px; }
            h1 { border-bottom: 2px solid #00ff66; padding-bottom: 10px; }
            .note { background: #1e1e1e; border: 1px solid #333; padding: 15px; margin-bottom: 15px; border-radius: 5px; }
            .pending { border-left: 5px solid #ffaa00; }
            .done { border-left: 5px solid #00ff66; }
            pre { background: #0a0a0a; padding: 10px; color: #ffffff; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>🌐 Świat Rój — Tablica Karteczek (Mailbox)</h1>
        <p>Status serwera: <b>ONLINE (Tryb Asynchroniczny)</b></p>
        <h2>Aktywne karteczki na tablicy:</h2>
        {% if notes %}
            {% for nid, note in notes.items() %}
                <div class="note {{ 'done' if note.status == 'DONE' else 'pending' }}">
                    <b>ID Karteczki:</b> {{ nid }}<br>
                    <b>Czas utworzenia:</b> {{ note.timestamp }}<br>
                    <b>Status:</b> <span style="color: {{ '#00ff66' if note.status == 'DONE' else '#ffaa00' }}">{{ note.status }}</span><br>
                    <b>Zlecenie (Zapytanie):</b> {{ note.objective }}<br>
                    <b>Odpowiedź / Wynik:</b> <pre>{{ note.answer }}</pre>
                </div>
            {% endfor %}
        {% else %}
            <p>Brak karteczek na tablicy. System oczekuje na zadania.</p>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(html, notes=NOTES_BOARD)

@app.route("/api/post_note", methods=["POST"])
def post_note():
    data = request.json or {}
    objective = data.get("objective", "").strip()
    if not objective:
        return jsonify({"status": "ERROR", "message": "Brak zlecenia na karteczce"}), 400
    
    note_id = str(uuid.uuid4())[:8]
    NOTES_BOARD[note_id] = {
        "objective": objective,
        "status": "PENDING",
        "answer": "Oczekiwanie na odpowiedź od AI / agenta...",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return jsonify({
        "status": "SUCCESS", 
        "note_id": note_id, 
        "message": "Zostawiono karteczkę na serwerze."
    })

@app.route("/api/get_notes", methods=["GET"])
def get_notes():
    return jsonify({"status": "SUCCESS", "notes": NOTES_BOARD})

@app.route("/api/check_note/<note_id>", methods=["GET"])
def check_note(note_id):
    note = NOTES_BOARD.get(note_id)
    if not note:
        return jsonify({"status": "ERROR", "message": "Nie znaleziono takiej karteczki"}), 404
    return jsonify({"status": "SUCCESS", "note": note})

@app.route("/api/answer_note/<note_id>", methods=["POST"])
def answer_note(note_id):
    data = request.json or {}
    answer = data.get("answer", "").strip()
    if not answer:
        return jsonify({"status": "ERROR", "message": "Brak treści odpowiedzi"}), 400
    
    if note_id not in NOTES_BOARD:
        return jsonify({"status": "ERROR", "message": "Nie znaleziono takiej karteczki"}), 404
    
    NOTES_BOARD[note_id]["answer"] = answer
    NOTES_BOARD[note_id]["status"] = "DONE"
    return jsonify({"status": "SUCCESS", "message": "Dopisano odpowiedź do karteczki."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
