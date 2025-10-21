import os, json, time
from pathlib import Path
import requests
from dotenv import load_dotenv
from plexapi.server import PlexServer

load_dotenv()
PLEX_URL = os.getenv("PLEX_URL","http://localhost:32400")
PLEX_TOKEN = os.getenv("PLEX_TOKEN")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MAX_ITEMS = int(os.getenv("MAX_ITEMS","25"))

assert PLEX_TOKEN, "PLEX_TOKEN missing"
assert BOT_TOKEN, "TELEGRAM_BOT_TOKEN missing"
assert CHAT_ID, "TELEGRAM_CHAT_ID missing"

def plex():
    return PlexServer(PLEX_URL, PLEX_TOKEN)

def tg_send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text[:4000]}, timeout=20)

def load_state(path):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return {}
    return {}

def save_state(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

def main():
    state_path = Path("state.json")
    state = load_state(state_path)
    seen = set(state.get("seen", []))

    p = plex()
    items = []
    for s in p.library.sections():
        if s.type in ("movie","show"):
            items.extend(s.recentlyAdded() or [])
    # newest first
    items.sort(key=lambda x: getattr(x, "addedAt", 0), reverse=True)
    items = items[:MAX_ITEMS]

    new_msgs = []
    for it in items:
        guid = getattr(it, "guid", None) or getattr(it, "ratingKey", None)
        if not guid:
            continue
        if guid in seen:
            continue
        title = getattr(it, "title", "Unknown")
        year = getattr(it, "year", "")
        kind = getattr(it, "type", "item")
        msg = f"🎬 New in Plex: {title} {f'({year})' if year else ''} [{kind}]"
        new_msgs.append((guid, msg))

    if new_msgs:
        for guid, msg in reversed(new_msgs):  # send oldest first
            tg_send(msg)
            seen.add(guid)
        save_state(state_path, {"seen": list(seen)})

if __name__ == "__main__":
    main()
