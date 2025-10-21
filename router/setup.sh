#!/usr/bin/env bash
set -e
source .env || true
mkdir -p "$SSD_PATH" "$HDD_PATH" "$CLOUD_PATH" "$UNION_PATH"
echo "Mounting cloud remotes..."
rclone mount "$RCLONE_REMOTE_GDRIVE" "$CLOUD_PATH" --daemon
echo "Combining drives with mergerfs..."
mergerfs "$SSD_PATH:$HDD_PATH:$CLOUD_PATH" "$UNION_PATH" -o defaults,allow_other,use_ino,category.create=epmfs &
echo "Storage router setup complete. Active union: $UNION_PATH"
