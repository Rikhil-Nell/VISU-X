from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allows frontend to make API requests


# Serve the HTML page
@app.route("/")
def home():
    return render_template("index.html")


# API to handle blinking
@app.route("/api/blink", methods=["POST"])
def blink():
    return jsonify({"status": "success", "message": "Blinking triggered!"})


# API to handle expressions (happy, sad, angry, etc.)
@app.route("/api/express", methods=["POST"])
def express():
    data = request.json
    emotion = data.get("type", "neutral")
    return jsonify({"status": "success", "expression": emotion})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
