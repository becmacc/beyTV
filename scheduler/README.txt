BeyTV Scheduler Pack (Midnight-6AM)
----------------------------------
Goal:
  Run qBittorrent only between 00:00–06:00 local time. Optional: throttle by day.

Assumptions:
  - Docker container name: qbittorrent
  - Host timezone set to Asia/Beirut

Files:
  - start_qb.sh        → docker start qbittorrent
  - stop_qb.sh         → docker stop qbittorrent
  - day_throttle.sh    → optional speed limit via Web API
  - crontab.txt        → install with: crontab crontab.txt

Install:
  1) chmod +x scheduler/*.sh
  2) Edit day_throttle.sh with your qB Web username/password if used.
  3) crontab scheduler/crontab.txt

Verify:
  - docker ps  (after 00:01 should show qbittorrent up)
  - docker ps  (after 06:01 should show qbittorrent down)

Notes:
  - If using docker-compose, you can replace docker start/stop with 'docker compose start/stop qbittorrent'.
  - Throttle script uses qB Web API (port 8080). Skip if not needed.
