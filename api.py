from flask import Flask, jsonify, request

app = Flask(__name__)

events = [
    {
        "id": 1,
        "title": "Quizaften",
        "date": "2026-11-13",
        "capacity": 3,
        "participants": ["Anna", "Bo"]
    },
    {
        "id": 2,
        "title": "Brætspilsaften",
        "date": "2026-11-20",
        "capacity": 8,
        "participants": []
    }
]

@app.get("/events")
def get_events():
    return jsonify(events)

@app.get("/events/<int:event_id>")
def get_event(event_id):
    for event in events:
        if event["id"] == event_id:
            return jsonify(event)

    return jsonify({"error": "Eventet findes ikke."}), 404

@app.post("/events")
def create_event():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Body skal være et JSON-objekt."}), 400

    title = data.get("title")
    event_date = data.get("date")
    capacity = data.get("capacity")
    
    if not title or not event_date or capacity is None:
        return jsonify({"error": "title, date og capacity skal udfyldes."}), 400

    if type(capacity) is not int or capacity <= 0:
        return jsonify({"error": "capacity skal være et positivt heltal."}), 400
   
    new_id = 1
    for event in events:
        if event["id"] >= new_id:
            new_id = event["id"] + 1

    new_event = {
        "id": new_id,
        "title": title,
        "date": event_date,
        "capacity": capacity,
        "participants": []
    }

    events.append(new_event)

    return jsonify(new_event), 201

@app.post("/events/<int:event_id>/signups")
def signup(event_id):
    for event in events:
        if event["id"] == event_id:
            data = request.get_json(silent=True)

            if not isinstance(data, dict):
                return jsonify({"error": "Body skal være et JSON-objekt."}), 400

            name = data.get("name")

            if not isinstance(name, str) or not name.strip():
                return jsonify({"error": "Du skal angive et navn."}), 400

            name = name.strip()

            if name in event["participants"]:
                return jsonify({"error": "Personen er allerede tilmeldt."}), 409

            if len(event["participants"]) >= event["capacity"]:
                return jsonify({"error": "Eventet er fuldt."}), 409

            event["participants"].append(name)
            return jsonify(event), 201

    return jsonify({"error": "Eventet findes ikke."}), 404

@app.delete("/events/<int:event_id>/signups/<name>")
def cancel_signup(event_id, name):
    for event in events:
        if event["id"] == event_id:
            if name not in event["participants"]:
                return jsonify({"error": "Tilmeldingen findes ikke."}), 404

            event["participants"].remove(name)
            return "", 204

    return jsonify({"error": "Eventet findes ikke."}), 404

@app.delete("/events/<int:event_id>")
def delete_event(event_id):
    for event in events:
        if event["id"] == event_id:
            events.remove(event)
            return "", 204

    return jsonify({"error": "Eventet findes ikke."}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=False, threaded=False)
