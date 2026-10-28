#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
export LD_LIBRARY_PATH=/vendor/lib:/system/lib
LIVE=/system/framework/automotive-service.odex
STAGE=/system/framework/.hkmc-ptt-phone-assistant.stage
STATE=/data/nemesis/backup/hkmc.ptt-phone-assistant
BACKUP=$STATE/automotive-service.odex
LOCK=/data/nemesis/hkmc.ptt-phone-assistant.lock
LOG=/data/nemesis/hkmc.ptt-phone-assistant.log
ORIGINAL_MD5=23e123f1cc296943b32391a70b2f20f5
PATCHED_MD5=06f7715af79e839861e8b60a9201a99c
DELAY_OFFSET=1289088
CHECKSUM_OFFSET=48

log() { echo "$*"; echo "$*" >> "$LOG"; }
die() { log "ERROR: $*"; exit 1; }
digest() {
    [ -f "$1" ] && [ ! -L "$1" ] || return 1
    line=$(md5 "$1" 2>/dev/null) || return 1
    set -- $line
    [ "$#" -ge 1 ] || return 1
    case "$1" in *[!0123456789abcdef]*|'') return 1 ;; esac
    [ "${#1}" = 32 ] || return 1
    echo "$1"
}
check_device() {
    [ "$(getprop ro.product.device)" = wp_daudioplus_neev_us ] || die 'Unsupported head unit.'
    [ "$(getprop ro.build.version.sdk)" = 19 ] || die 'Unsupported Android version.'
    command -v md5 >/dev/null 2>&1 || die 'Required Android md5 command is missing.'
}
check_live() {
    current=$(digest "$LIVE") || die 'Cannot checksum live framework.'
    case "$current" in
      "$ORIGINAL_MD5"|"$PATCHED_MD5") ;;
      *) die "Framework differs from supported file; no change made. MD5=$current" ;;
    esac
}
check_backup() {
    [ ! -L "$STATE" ] || die 'Backup directory is a symlink.'
    if [ -e "$BACKUP" ] || [ -L "$BACKUP" ]; then
      [ "$(digest "$BACKUP")" = "$ORIGINAL_MD5" ] || die 'Existing backup failed verification; preserved.'
    elif [ "$current" = "$PATCHED_MD5" ]; then
      die 'Patched framework has no verified original backup.'
    fi
}
cleanup() {
    if [ "$STAGED" = yes ]; then rm -f "$STAGE"; fi
    rmdir "$LOCK" 2>/dev/null
}
lock_operation() {
    mkdir "$LOCK" 2>/dev/null || die 'Another operation or stale lock exists; inspect the log.'
    STAGED=no
    trap cleanup EXIT
    trap 'exit 1' HUP INT TERM
    [ ! -e "$STAGE" ] && [ ! -L "$STAGE" ] || die 'Staging file already exists; refusing to overwrite it.'
}
begin_stage() {
    nemesis remount rw || die 'Cannot remount system writable.'
    STAGED=yes
    cp "$1" "$STAGE" || die 'Staging copy failed; live framework unchanged.'
    chmod 0644 "$STAGE" || die 'Cannot set staging permissions.'
    chown 0:0 "$STAGE" || die 'Cannot set staging ownership.'
}
commit_stage() {
    want=$1
    [ "$(digest "$STAGE")" = "$want" ] || die 'Staged framework checksum mismatch; live framework unchanged.'
    # The rename replaces the inode atomically; the running process keeps its old mapping.
    sync
    mv "$STAGE" "$LIVE" || die 'Atomic replacement failed.'
    STAGED=no
    sync
    [ "$(digest "$LIVE")" = "$want" ] || die 'Post-write verification failed; use USB recovery.'
}
restore_original() {
    check_live
    if [ "$current" = "$ORIGINAL_MD5" ]; then
      log 'Original framework already present. No changes required.'
      return 0
    fi
    check_backup
    begin_stage "$BACKUP"
    commit_stage "$ORIGINAL_MD5"
    log 'Original framework restored. Perform a full head-unit restart.'
    log 'Original backup retained for recovery.'
}
