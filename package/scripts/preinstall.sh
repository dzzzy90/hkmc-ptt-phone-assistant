#!/system/bin/sh
. ./scripts/common.sh
check_live
check_device
check_backup
log "Preflight passed for exact uploaded framework: $PROFILE. Version 0.1.0-alpha; vehicle behavior unverified."
