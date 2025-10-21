BeyTV Indexer Pack (Torrent RSS Feeds)
--------------------------------------
Purpose:
  Automate the discovery and addition of new torrents (movies, shows) to qBittorrent
  using RSS and magnet links.

Sources:
  - YTS (movies) → https://yts.mx/rss
  - EZTV (shows) → https://eztv.re/ezrss.xml
  - The Pirate Bay mirror (optional) → https://thepiratebay.org/rss/top100/207

Output:
  - JSON feed of curated magnets.
  - Optional direct push to qBittorrent via Web API.

Setup:
  1) cd indexer
  2) python -m venv .venv && . .venv/bin/activate
  3) pip install -r requirements.txt
  4) cp .env.sample .env
  5) python indexer.py  # test run (prints found magnets)

Automation:
  */30 * * * *  cd /path/to/indexer && . .venv/bin/activate && python indexer.py >/tmp/beytv_indexer.log 2>&1

Files created:
  - feeds/latest.json  (list of latest magnets)
  - feeds/index.html   (human view of same feed)

Embed in BeyFlow as iframe or list.
