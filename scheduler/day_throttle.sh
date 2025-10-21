#!/usr/bin/env bash
# Optional: set low daytime speed limits, and remove at night.
# Requires qBittorrent Web UI enabled on http://localhost:8080
# Fill credentials below.
QB_URL="http://localhost:8080"
QB_USER="admin"
QB_PASS="adminadmin"
# day limits in KiB/s (e.g. 2000 = ~2 MiB/s). Set 0 to disable.
DL_LIMIT_DAY=2000
UP_LIMIT_DAY=500

login() {
  curl -s -c /tmp/qb_cookies.txt -d "username=$QB_USER&password=$QB_PASS" "$QB_URL/api/v2/auth/login" >/dev/null
}
set_limits() {
  local dl="$1"; local up="$2"
  [[ "$dl" -gt 0 ]] && curl -s -b /tmp/qb_cookies.txt "$QB_URL/api/v2/transfer/setDownloadLimit?limit=$dl" >/dev/null
  [[ "$up" -gt 0 ]] && curl -s -b /tmp/qb_cookies.txt "$QB_URL/api/v2/transfer/setUploadLimit?limit=$up" >/dev/null
}
clear_limits() {
  curl -s -b /tmp/qb_cookies.txt "$QB_URL/api/v2/transfer/setDownloadLimit?limit=0" >/dev/null
  curl -s -b /tmp/qb_cookies.txt "$QB_URL/api/v2/transfer/setUploadLimit?limit=0" >/dev/null
}
main() {
  login
  HOUR=$(date +%H)
  if [[ "$HOUR" -ge 6 && "$HOUR" -lt 24 ]]; then
    set_limits "$DL_LIMIT_DAY" "$UP_LIMIT_DAY"
  else
    clear_limits
  fi
}
main "$@"
