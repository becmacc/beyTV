import os, subprocess, json, requests, argparse
from dotenv import load_dotenv

load_dotenv()

SSD_PATH = os.getenv("SSD_PATH", "/mnt/ssd_media")
HDD_PATH = os.getenv("HDD_PATH", "/mnt/hdd_media")
CLOUD_PATH = os.getenv("CLOUD_PATH", "/mnt/cloud_media")
UNION_PATH = os.getenv("UNION_PATH", "/media")
QB_URL = os.getenv("QB_URL")
QB_USER = os.getenv("QB_USER")
QB_PASS = os.getenv("QB_PASS")
PLEX_URL = os.getenv("PLEX_URL")
PLEX_TOKEN = os.getenv("PLEX_TOKEN")

session = requests.Session()

def qb_login():
    r = session.post(f"{QB_URL}/api/v2/auth/login", data={"username": QB_USER, "password": QB_PASS}, timeout=10)
    return r.status_code == 200 and "Ok" in r.text

def qb_set_savepath(path):
    if not qb_login():
        print("qB login failed")
        return
    r = session.post(f"{QB_URL}/api/v2/app/setPreferences", data={"json": json.dumps({"save_path": path})})
    print("qBittorrent save_path set to", path)

def plex_refresh():
    if not PLEX_TOKEN: return
    try:
        requests.post(f"{PLEX_URL}/library/all/refresh?X-Plex-Token={PLEX_TOKEN}", timeout=10)
        print("Triggered Plex refresh.")
    except Exception as e:
        print("Plex refresh failed:", e)

def list_storages():
    for name, path in {"ssd": SSD_PATH, "hdd": HDD_PATH, "cloud": CLOUD_PATH}.items():
        print(f"{name.upper()} → {path} {'(exists)' if os.path.exists(path) else '(missing)'}")

def set_storage(target):
    path = {"ssd": SSD_PATH, "hdd": HDD_PATH, "cloud": CLOUD_PATH}.get(target)
    if not path:
        print("Invalid target")
        return
    if target == "cloud":
        # ensure cloud mounted
        subprocess.run(["rclone", "mount", os.getenv("RCLONE_REMOTE_GDRIVE", "gdrive:"), CLOUD_PATH, "--daemon"], check=False)
    qb_set_savepath(path)
    plex_refresh()
    print(f"Active storage switched to {target.upper()} ({path})")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--list", action="store_true")
    p.add_argument("--set", choices=["ssd","hdd","cloud"])
    args = p.parse_args()
    if args.list:
        list_storages()
    elif args.set:
        set_storage(args.set)
    else:
        p.print_help()
