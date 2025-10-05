from flask import Flask, request, jsonify
from forwarder import handle_channel_post
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    if "channel_post" in data:
        res = handle_channel_post(data["channel_post"])
        return jsonify(res)
    return jsonify({"ok": True})

@app.route("/")
def home():
    return "Telegram Forwarder Bot - Ready"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
