BeyTV Notifier Pack (Telegram)
------------------------------
Goal:
  Send a Telegram message when new items appear in Plex.

Approach:
  Poll Plex recently added, track last seen GUID in state.json, notify on new ones.

Prereqs:
  - Telegram bot token (BotFather)
  - Telegram chat ID (send a message to the bot and query via https://api.telegram.org/bot<TOKEN>/getUpdates once)
  - Plex token and base URL

Setup:
  1) cd notifier
  2) python -m venv .venv && . .venv/bin/activate
  3) pip install -r requirements.txt
  4) cp .env.sample .env  # fill values
  5) python notify.py     # test run

Automate:
  */5 * * * *  cd /path/to/notifier && . .venv/bin/activate && python notify.py >/tmp/beytv_notify.log 2>&1

Customize message template in notify.py if needed.
