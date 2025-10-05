# Telegram Forwarder Bot (Customized for your channels)

This package is pre-configured with your channel IDs:
- Source: -1002856470667 (DeshiviralHubLink(Bot))
- Targets: -1003172610238 (DeshiviralHub_All), -1003116951675 (DeshiviralHub (Latest))

How to use:
1. Update config.yaml: set bot_token to your token.
2. Add more routes in config.yaml under 'routes' as needed.
3. For local testing, run:
   pip install -r requirements.txt
   python poller.py

4. For production (Render.com), push to GitHub and create a Web Service. Start command: gunicorn app:app

Adding filters later:
- Edit config.yaml -> add 'keywords' or 'hashtags' for new routes.
- The bot auto-reloads config.yaml every 30 seconds (no restart needed).

Security:
- Keep bot token secret. Do NOT commit it to public repo.

