# Phone Assistant PTT — 0.1.0-alpha

Experimental NEMESIS package for the supplied 2022 Ioniq 5 Limited USA firmware,
`NEEV23.USA.S5W_M.V015.012.260507`. **Owner-tested on one vehicle; experimental alpha release.**

## Vehicle test report

The owner reports that this package works on a 2022 Ioniq 5 Limited USA with
`NEEV23.USA.S5W_M.V015.012.260507`. The report does not separately identify
CarPlay versus Android Auto or confirm every test below. Compatibility with
other vehicles or firmware has not been established.

## Intended behavior

A short voice-button press enters Hyundai's existing long-press path immediately.
A held press enters that same path without waiting half a second. The connected
projection session determines Siri versus the Android Auto assistant. Existing
call, camera, voice-memo and connection-state handling remains in the firmware.
This does not add projection connectivity or force an assistant when none is connected.

Implementation: `ModeKeyDispatcher.interceptPttKey()` posts `mPttLongPress` using
`Handler.postDelayed(..., 500)`. This patch changes only that delay to zero and
updates the optimized DEX Adler-32 checksum. It does not replace the routing code.
Only six file bytes change: the two-byte delay and four checksum bytes.

**Limitations:** a zero-delay Handler callback is queued, not synchronous. Very
fast taps or a busy handler may still race with key-up cancellation. Avoiding
duplicate activation, release behavior, active-assistant behavior, and both
projection platforms require in-car testing. These are not claimed as verified.

## Before installation

This replaces one core infotainment framework file. An incompatible change can prevent
infotainment from starting. Keep the supplied recovery USB files available and a
copy of the original extracted framework on your computer. USB recovery requires
NEMESIS's USB handler to remain functional; it is not a guaranteed boot recovery.

The installer rejects any framework file other than the exact original supplied
for this release or this release's exact patched version. Matching the software
version label alone is insufficient. Do not bypass the checks for another car or
firmware. Do not install another package modifying this file while this alpha is
installed. Uninstall this alpha before updating firmware.

## Install

1. Extract the release ZIP and open `INSTALL-USB`.
2. Put its `NEMESIS.data` and `packages` folder at the USB root. Move the diagnostic
   `NEMESIS.sh` and previous launcher off the drive to avoid running the wrong tool.
3. With the car parked and infotainment running, insert USB and approve install.
4. Wait for success. Installation does not reboot the head unit automatically.
5. Perform a full head-unit restart. A normal car off/on may resume QuickBoot and
   retain the old process. Use the head unit's reset/restart procedure.
6. Test while parked with an active CarPlay or Android Auto connection.

The package is `hkmc.ptt-phone-assistant` in NEMESIS Manager. Launch shows file
status in its output/log; that status does not prove the patched code is loaded.

## Validation to perform on the car

- Short press: assistant activates once; Hyundai VR does not open.
- Hold for three seconds: assistant activates once; release does not activate it again.
- Repeat with the assistant already active and during audio playback.
- Repeat on CarPlay and Android Auto separately; report which was actually tested.
- Disconnect projection and record factory long-press behavior.
- Confirm normal operation of the other steering-wheel controls.
- Uninstall and restart; confirm original short/long behavior returns.

Record outcome and connection type. If behavior is wrong, uninstall; do not treat
installation success as proof that the remap works.

## Uninstall and recovery

Normal: NEMESIS Manager > Packages > hkmc.ptt-phone-assistant > Uninstall, then
fully restart the head unit. The preuninstall hook restores the verified original.

USB recovery: copy the contents of the release's `RECOVERY-USB` folder onto
a USB drive. Its `NEMESIS.data`, `NEMESIS.sh`, and `recovery-common.sh` must all be
at root. Insert and approve execution if prompted. This restores the original
file from the on-car backup and requires a full restart. It does not remove the
package registration; uninstall in Manager afterward when available.

Both restore paths refuse to overwrite an unexpected framework file or restore
an invalid backup. Backups remain at `/data/nemesis/backup/hkmc.ptt-phone-assistant/`.
Log: `/data/nemesis/hkmc.ptt-phone-assistant.log`.
No personal data or general system logs are collected.

## Engineering evidence

- Supplied input events: code 40, approximately 0.18 s and 2.67 s presses.
- Relevant key layouts map code 40 to `SHORTCUT_PTT`.
- Decompiled framework: `generateLongKeyEventForPtt()` injects key code 0x108,
  scan code 0x28, flag 0x80 and repeat count 1. The existing routing distinguishes
  CarPlay, GPM (Android Auto), Bluetooth Siri and Hyundai voice recognition.
- Successful deodex used Baksmali 2.5.2 with API 18 layout and the uploaded
  framework dependencies. API 19 layout produced incorrect field resolution;
  the build label is Android 4.4.2/API 19, but that is not the decoder layout here.
- The ODEX source signature already does not match its optimized DEX code. That
  original signature is retained for dependency identity; the code checksum is
  recalculated. Dependency/optimization sections are untouched.
- Full hashes and exact offsets are in `package/patch/manifest.json`.

No Hyundai/Kia framework binaries or decompiled source are shipped. The package
contains our scripts and six replacement bytes only. The original is copied and
patched locally on the car. Pre/post full-file MD5 checks identify the expected
bytes, not an adversarial authenticity guarantee. SHA-256 values are also supplied
for offline auditing. Installation stages and verifies the whole file before an
atomic rename, preserving the currently running process's old mapped inode.

## Rebuild

Python 3.9+ is sufficient for the release tooling. Run:

```
python3 src/make_patch.py /path/to/automotive-service.odex package/patch
```

The supported MD5 values and offsets in `package/scripts/common.sh` are pinned
to this release. Updating `manifest.json` does not automatically enable a new
firmware. Review the actual method and tests before making any port.

Package-format reference: https://github.com/xwtk/hmg_nemesis/blob/main/04-Packages.md
Decoder-layout reference: https://github.com/VysseCodes/HMG-Leafia-Plus/blob/08f4436cf12a9edfdd575748c693c7240c7bdc4d/tools/port.py

## Acknowledgments

- [NEMESIS](https://github.com/xwtk/hmg_nemesis) provides the package framework.
- [hkmc-track-button-swap](https://github.com/dibble9012/hkmc-track-button-swap) inspired this project; this package uses a different mechanism.
- [HMG-Leafia-Plus](https://github.com/VysseCodes/HMG-Leafia-Plus) documents the required decoder layout.
