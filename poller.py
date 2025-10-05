import requests, time, os
from forwarder import handle_channel_post, CONFIG

BOT_TOKEN = CONFIG.get('bot_token')
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
OFFSET = 0
print("Polling mode started...")
while True:
    try:
        res = requests.get(BASE_URL + f"/getUpdates?offset={OFFSET+1}&timeout=30")
        data = res.json()
        for upd in data.get("result", []):
            OFFSET = upd["update_id"]
            if "channel_post" in upd:
                print("New channel_post:", upd["channel_post"].get('message_id'))
                print(handle_channel_post(upd["channel_post"]))
        time.sleep(2)
    except KeyboardInterrupt:
        break
    except Exception as e:
        print("Poller error:", e)
        time.sleep(5)
