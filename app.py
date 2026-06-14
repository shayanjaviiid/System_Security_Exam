"""
app.py
A small Flask server that drives the same crypto pipeline as the
four CLI scripts (setup_keys, sender, hacker, receiver) and exposes
it to the browser at http://127.0.0.1:5000/.

Run:
    pip install flask cryptography
    python app.py
"""

from flask import Flask, jsonify, render_template, request

import core


app = Flask(__name__, template_folder="templates", static_folder="static")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/state")
def api_state():
    return jsonify(core.project_state())


@app.route("/api/setup", methods=["POST"])
def api_setup():
    return jsonify(core.setup_keys())


@app.route("/api/send", methods=["POST"])
def api_send():
    payload = request.get_json(silent=True) or {}
    data = payload.get("data")
    return jsonify(run_safely(lambda: core.run_sender(data)))


@app.route("/api/hack", methods=["POST"])
def api_hack():
    return jsonify(run_safely(core.run_hacker))


@app.route("/api/receive", methods=["POST"])
def api_receive():
    return jsonify(run_safely(core.run_receiver))


@app.route("/api/reset", methods=["POST"])
def api_reset():
    return jsonify(core.reset())


def run_safely(fn):
    try:
        return fn()
    except FileNotFoundError as e:
        return {"error": str(e), "logs": [("fail", str(e))]}
    except Exception as e:
        return {"error": repr(e), "logs": [("fail", repr(e))]}


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
