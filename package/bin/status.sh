#!/system/bin/sh
case "$0" in */bin/status.sh) BASE=${0%/bin/status.sh} ;; *) BASE=. ;; esac
. "$BASE/scripts/common.sh"
check_live
check_backup
log "PTT alpha current framework MD5: $current"
if [ "$current" = "$PATCHED_MD5" ]; then
  log 'Patched file present. This does not verify that it is loaded or that phone routing works.'
else
  log 'Original file present.'
fi
