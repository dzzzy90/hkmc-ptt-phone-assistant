#!/system/bin/sh
case "$0" in /*) BASE=${0%/*} ;; *) BASE=$(pwd) ;; esac
. "$BASE/recovery-common.sh"
lock_operation
restore_original
