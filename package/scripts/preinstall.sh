#!/system/bin/sh
. ./scripts/common.sh
check_device
check_live
check_backup
log 'Preflight passed for exact uploaded framework. Version 0.1.0-alpha; vehicle behavior unverified.'
