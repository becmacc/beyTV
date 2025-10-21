BeyTV Storage Router Pack
-------------------------
Purpose:
  Unified storage routing layer that allows you to dynamically choose
  where downloads and media reside — SSD, HDD, or cloud (Google Drive, S3).

Core features:
  - Detects available local drives.
  - Mounts cloud remotes via rclone.
  - Uses mergerfs to combine drives into a single /media pool for Plex.
  - Updates qBittorrent save path and Plex library automatically.

Prerequisites:
  - Linux host with Docker, Python 3.9+
  - rclone configured with cloud remotes (rclone config)
  - mergerfs installed (apt install mergerfs)

Structure:
  router/
    ├─ router.py         → dynamic storage routing daemon
    ├─ setup.sh          → mounts drives + configures mergerfs union
    ├─ .env.sample       → tokens and paths
    └─ requirements.txt  → dependencies

Usage:
  1) cp .env.sample .env  and edit your local/cloud paths.
  2) bash setup.sh
  3) python3 router.py --list   # list storages
  4) python3 router.py --set hdd   # switch active drive
  5) python3 router.py --set gdrive # mount cloud storage and redirect downloads

Optional automation:
  - Cron job to move older files from SSD → HDD after X days.
  - BeyFlow toggle UI (REST call → /api/router/set?target=hdd).

Result:
  Seamless space management between local drives and cloud, keeping Plex + qBittorrent synced.
