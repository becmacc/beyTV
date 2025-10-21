import os, time, json, requests, feedparser
from pathlib import Path
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()

QB_URL = os.getenv("QB_URL", "http://localhost:8080")
QB_USER = os.getenv("QB_USER", "admin")
QB_PASS = os.getenv("QB_PASS", "adminadmin")
FEEDS = [f.strip() for f in os.getenv("FEEDS","https://yts.mx/rss").split(",") if f.strip()]
CATEGORY = os.getenv("CATEGORY", "auto")
LIMIT = int(os.getenv("LIMIT", "30"))

def qb_login(session):
    url = f"{QB_URL}/api/v2/auth/login"
    r = session.post(url, data={"username": QB_USER, "password": QB_PASS}, timeout=10)
    if r.status_code == 200 and r.text == "Ok.":
        return True
    print("Login failed")
    return False

def qb_add(session, magnet):
    url = f"{QB_URL}/api/v2/torrents/add"
    data = {"urls": magnet, "category": CATEGORY}
    session.post(url, data=data, timeout=15)

def fetch_feeds():
    all_items = []
    for f in FEEDS:
        print(f"Fetching {f}")
        d = feedparser.parse(f)
        for e in d.entries[:LIMIT]:
            title = e.get("title", "unknown")
            link = e.get("link", "")
            if "magnet:?" in link:
                magnet = link
            else:
                # fallback for rss with magnet link in enclosure
                magnet = e.get("enclosures", [{}])[0].get("url", "")
            if not magnet.startswith("magnet:"):
                continue
            all_items.append({"title": title, "magnet": magnet, "source": f})
    return all_items

def main():
    Path("feeds").mkdir(exist_ok=True)
    items = fetch_feeds()
    if not items:
        print("No items found")
        return
    with open("feeds/latest.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    rows = "\n".join([f"<tr><td>{i['title']}</td><td><a href='{i['magnet']}'>Magnet</a></td><td>{i['source']}</td></tr>" for i in items])
    html = f"""<!doctype html><html><head><meta charset='utf-8'><title>BeyTV Indexer</title>
    <style>body{{font-family:sans-serif;max-width:900px;margin:auto}}table{{width:100%;border-collapse:collapse}}td,th{{border:1px solid #ddd;padding:6px}}</style></head>
    <body><h1>BeyTV Indexer</h1><table><tr><th>Title</th><th>Magnet</th><th>Source</th></tr>{rows}</table></body></html>"""
    Path("feeds/index.html").write_text(html, encoding="utf-8")

    # Optionally push to qBittorrent
    try:
        s = requests.Session()
        if qb_login(s):
            for i in items[:5]:  # add top 5
                qb_add(s, i["magnet"])
    except Exception as e:
        print("qB push failed:", e)

    print(f"Saved {len(items)} items to feeds/latest.json")

if __name__ == "__main__":
    main()
