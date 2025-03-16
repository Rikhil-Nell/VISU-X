from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

latest_emotion = {"type": "neutral"}
last_update_time = time.time()  # Track the last emotion update time

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/express", methods=["POST"])
def express():
    global latest_emotion, last_update_time
    data = request.json
    latest_emotion = {"type": data.get("type", "neutral")}
    last_update_time = time.time()  # Reset the timer when emotion updates
    return jsonify({"status": "success", "expression": latest_emotion})

@app.route("/api/get_emotion", methods=["GET"])
def get_emotion():
    global latest_emotion, last_update_time
    # If no emotion update for 10s, return "neutral"
    if time.time() - last_update_time > 15:
        latest_emotion = {"type": "neutral"}
    return jsonify(latest_emotion)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
