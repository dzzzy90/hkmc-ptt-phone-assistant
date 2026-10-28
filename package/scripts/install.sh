#!/system/bin/sh
. ./scripts/common.sh
check_device
lock_operation
check_live
check_backup
if [ "$current" = "$PATCHED_MD5" ]; then
  log 'Patch already present; verified backup retained. Full restart required if not yet performed.'
  exit 0
fi
mkdir -p "$STATE" || die 'Cannot create backup directory.'
if [ ! -e "$BACKUP" ]; then
  [ ! -e "$STATE/original.tmp" ] && [ ! -L "$STATE/original.tmp" ] || die 'Backup staging file exists.'
  cp "$LIVE" "$STATE/original.tmp" || die 'Backup copy failed; live framework unchanged.'
  [ "$(digest "$STATE/original.tmp")" = "$ORIGINAL_MD5" ] || die 'Backup verification failed.'
  mv "$STATE/original.tmp" "$BACKUP" || die 'Cannot finalize backup.'
  sync
fi
begin_stage "$LIVE"
dd if=./patch/delay.bin of="$STAGE" bs=1 seek="$DELAY_OFFSET" count=2 conv=notrunc || die 'Delay patch failed.'
dd if=./patch/checksum.bin of="$STAGE" bs=1 seek="$CHECKSUM_OFFSET" count=4 conv=notrunc || die 'DEX checksum patch failed.'
commit_stage "$PATCHED_MD5"
log 'Installed 0.1.0-alpha. PTT delay changed from 500 ms to 0 ms.'
log 'Full head-unit restart required. No reboot is performed automatically.'
