from flask import Flask, request, jsonify
from forwarder import handle_channel_post

app = Flask(__name__)

# ✅ এই রুট Telegram webhook (POST) ও GET দুটোই হ্যান্ডেল করবে
@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "Telegram Forwarder Bot - Running ✅", 200

    if request.method == "POST":
        data = request.get_json(force=True)
        if "channel_post" in data:
            res = handle_channel_post(data["channel_post"])
            return jsonify(res), 200
        return jsonify({"ok": True}), 200


# (Optional) আলাদা webhook route দরকার নেই, তাই এটা বাদ দেওয়া হলো
# @app.route("/webhook", methods=["POST"])
# def webhook_post():
#     data = request.get_json(force=True)
#     if "channel_post" in data:
#         res = handle_channel_post(data["channel_post"])
#         return jsonify(res)
#     return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
