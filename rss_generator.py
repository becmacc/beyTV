import os
import re
import csv
import time
import requests
from pathlib import Path
from urllib.parse import urlencode
from dotenv import load_dotenv
from plexapi.server import PlexServer
from feedgen.feed import FeedGenerator

load_dotenv()

OMDB_API_KEY = os.getenv("OMDB_API_KEY")
PLEX_URL = os.getenv("PLEX_URL", "http://localhost:32400")
PLEX_TOKEN = os.getenv("PLEX_TOKEN")
LIBRARY_TYPE = os.getenv("LIBRARY_TYPE", "both").lower()
MAX_ITEMS = int(os.getenv("MAX_ITEMS", "50"))

assert OMDB_API_KEY, "OMDB_API_KEY missing"
assert PLEX_TOKEN, "PLEX_TOKEN missing"

session = requests.Session()

def plex_connect():
    return PlexServer(PLEX_URL, PLEX_TOKEN)

def get_recent(plex):
    items = []
    sections = plex.library.sections()
    for s in sections:
        if LIBRARY_TYPE in ("both", "movie") and s.type == "movie":
            items.extend(s.recentlyAdded() or [])
        if LIBRARY_TYPE in ("both", "show") and s.type == "show":
            items.extend(s.recentlyAdded() or [])
    # sort by addedAt desc and truncate
    items.sort(key=lambda x: getattr(x, "addedAt", 0), reverse=True)
    return items[:MAX_ITEMS]

IMDB_RE = re.compile(r"(tt\d+)")

def extract_imdb_id(item):
    try:
        guids = [g.id for g in item.guids]  # e.g., 'com.plexapp.agents.imdb://tt1234567?lang=en'
        for g in guids:
            m = IMDB_RE.search(g)
            if m:
                return m.group(1)
    except Exception:
        pass
    return None

def omdb_lookup_by_id(imdb_id):
    q = {"i": imdb_id, "apikey": OMDB_API_KEY}
    r = session.get("http://www.omdbapi.com/", params=q, timeout=15)
    if r.status_code != 200:
        return None
    return r.json()

def omdb_lookup_by_title(title, year=None):
    q = {"t": title, "apikey": OMDB_API_KEY}
    if year:
        q["y"] = str(year)
    r = session.get("http://www.omdbapi.com/", params=q, timeout=15)
    if r.status_code != 200:
        return None
    return r.json()

def ratings_from_omdb(data):
    out = {"imdb":"", "rt":"", "metacritic":""}
    if not data or data.get("Response") == "False":
        return out
    # IMDb rating may appear in Ratings[] or as 'imdbRating'
    if "imdbRating" in data and data["imdbRating"] not in ("N/A", ""):
        out["imdb"] = f"{data['imdbRating']}/10"
    for r in data.get("Ratings", []):
        src = r.get("Source","")
        val = r.get("Value","")
        if src == "Internet Movie Database":
            out["imdb"] = val
        elif src == "Rotten Tomatoes":
            out["rt"] = val
        elif src == "Metacritic":
            out["metacritic"] = val
    return out

def build_feed(items, rows):
    fg = FeedGenerator()
    fg.title("BeyTV Ratings Feed")
    fg.link(href="https://example.local/beytv-rss", rel="self")
    fg.description("Latest Plex items with IMDb and Rotten Tomatoes ratings")
    now = time.strftime("%a, %d %b %Y %H:%M:%S %z")
    fg.pubDate(now)

    for row in rows:
        fe = fg.add_entry()
        title = row["title"]
        ratings = []
        if row["imdb"]: ratings.append(f"IMDb {row['imdb']}")
        if row["rt"]: ratings.append(f"RT {row['rt']}")
        if row["metacritic"]: ratings.append(f"MC {row['metacritic']}")
        rating_str = " | ".join(ratings) if ratings else "No ratings"
        fe.title(f"{title} — {rating_str}")
        fe.link(href=row.get("plex_url",""))
        fe.description(rating_str)
    return fg

def main():
    plex = plex_connect()
    items = get_recent(plex)

    rows = []
    for it in items:
        title = getattr(it, "title", "Unknown")
        year = getattr(it, "year", None)
        imdb_id = extract_imdb_id(it)
        data = omdb_lookup_by_id(imdb_id) if imdb_id else omdb_lookup_by_title(title, year)
        r = ratings_from_omdb(data)
        rows.append({
            "title": title if not year else f"{title} ({year})",
            "imdb": r["imdb"],
            "rt": r["rt"],
            "metacritic": r["metacritic"],
            "plex_url": f"{PLEX_URL}/web/index.html#!/server/{plex.machineIdentifier}/details?key={getattr(it, 'key', '')}"
        })

    outdir = Path("public")
    outdir.mkdir(parents=True, exist_ok=True)

    # CSV
    with open(outdir/"ratings.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["title","imdb","rt","metacritic","plex_url"])
        w.writeheader()
        w.writerows(rows)

    # RSS
    fg = build_feed(items, rows)
    fg.rss_file(outdir/"rss.xml")

    # Minimal HTML viewer
    html = '''<!doctype html>
<html><head><meta charset="utf-8"><title>BeyTV Ratings</title>
<style>body{font-family:system-ui, sans-serif;max-width:900px;margin:24px auto;padding:0 16px}
table{border-collapse:collapse;width:100%}th,td{border:1px solid #ddd;padding:8px}th{background:#f5f5f5;text-align:left}
</style></head><body>
<h1>BeyTV Ratings</h1>
<p>Generated from Plex + OMDb. Use the <a href="rss.xml">RSS</a> in any reader.</p>
<table><thead><tr><th>Title</th><th>IMDb</th><th>Rotten Tomatoes</th><th>Metacritic</th></tr></thead><tbody>
%s
</tbody></table></body></html>'''
    rows_html = "\n".join([f"<tr><td>{r['title']}</td><td>{r['imdb']}</td><td>{r['rt']}</td><td>{r['metacritic']}</td></tr>" for r in rows])
    with open(outdir/"index.html","w",encoding="utf-8") as f:
        f.write(html % rows_html)

    print("Done. See public/rss.xml and public/index.html")

if __name__ == "__main__":
    main()
