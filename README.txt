BeyTV Ratings Pack (IMDb + Rotten Tomatoes via OMDb) 
---------------------------------------------------
Purpose:
- Pull latest items from Plex.
- Fetch IMDb + Rotten Tomatoes ratings using OMDb.
- Publish an RSS feed and a CSV that you can embed in BeyFlow or read in any RSS reader.

Prereqs:
1) Create a free OMDb API key: http://www.omdbapi.com/apikey.aspx  (paid plan recommended for Rotten Tomatoes in Ratings[]).
2) Get Plex details:
   - PLEX_URL  (e.g., http://localhost:32400)
   - PLEX_TOKEN (from Plex account / network inspector)
3) Python 3.9+

Setup:
1) cd ratings
2) python -m venv .venv && . .venv/bin/activate
3) pip install -r requirements.txt
4) cp .env.sample .env  &&  edit .env with your keys
5) Run:
   python rss_generator.py

Outputs:
- public/rss.xml        → RSS with latest ratings
- public/ratings.csv    → CSV for spreadsheets
- public/index.html     → Minimal viewer

Serve locally (optional):
   python -m http.server 8088 -d public
Then embed in BeyFlow iframe:
   http://<server-ip>:8088/index.html

Automation:
- Cron every 30 minutes:
  */30 * * * *  cd /path/to/ratings && . .venv/bin/activate && python rss_generator.py >/tmp/beytv_ratings.log 2>&1

Notes:
- Rotten Tomatoes appears in OMDb's Ratings[] when available.
- If an item lacks an IMDb/RT rating, the fields are blank.
