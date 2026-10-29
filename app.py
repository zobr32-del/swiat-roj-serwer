# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify

app = Flask(__name__)

cloud_workspace = {
    "karteczka": "SYSTEM ROJU - CZEKANIE NA ZLECENIE",
    "status": "IDLE",
    "ostatni_kod": ""
}

@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "ONLINE", "message": "Serwer chmurowy Roju działa."})

@app.route('/notepad', methods=['GET', 'POST'])
def manage_notepad():
    if request.method == 'POST':
        data = request.json
        if data:
            if "karteczka" in data:
                cloud_workspace["karteczka"] = data["karteczka"]
            if "status" in data:
                cloud_workspace["status"] = data["status"]
            if "ostatni_kod" in data:
                cloud_workspace["ostatni_kod"] = data["ostatni_kod"]
        return jsonify({"status": "SUCCESS", "synced": True})
    else:
        return jsonify(cloud_workspace)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
