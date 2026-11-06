PHONE ASSISTANT PTT 1.0.0 - personal HMG-API package

Requires HMG-API 1.0.2 or newer, Gen5W, working HMG-API input hooks,
and a connected phone with CarPlay/Android Auto for projection voice.
This is an independent personal adaptation, not an upstream release.

INSTALL
1. If the original hkmc.ptt-phone-assistant NEMESIS patch is installed,
   uninstall it and fully restart the head unit first. Disable other
   mods claiming the voice button (including Car Check voice remaps).
2. Copy ptt-phone-assistant-1.0.0.zip, still zipped, into HMGAPI/updates/
   on a USB stick. The phone is only the download/transfer destination;
   this package installs on the car head unit, not as an Android APK.
3. In the car's HMG-API app choose Check USB updates, select the mod,
   review its personal author warning, install, then Apply changes.
4. Follow any restart instruction from HMG-API. Test while parked.

BEHAVIOR
A short press activates the phone assistant using the car's existing
long-press event. A physical long press retains the stock behavior.
The short press is recognized on release, unlike the original package's
zero-delay ODEX patch. No hold-to-talk/release-to-dismiss option is added.
Disconnected-phone behavior follows the car's stock long-press routing.
HMG-API controls input conflicts; inspect the plan if another mod wins.

TEST ON THE CAR
Connect CarPlay/Android Auto. Check a tap activates the assistant once,
holding three seconds and releasing does not double-activate it, and
other steering-wheel controls work. Check audio playback, an already
active assistant, and disconnected-phone behavior. Turn this mod off
and Apply changes to check normal voice-button behavior returns.
This package has been checked off-car only, not tested on your vehicle.

REMOVE
Turn off or remove Phone Assistant PTT in HMG-API and Apply changes.
This mod declares one input binding and ships no executable code,
system file patches, or manufacturer files.

SOURCES
Behavior inspiration (MIT):
https://github.com/dzzzy90/hkmc-ptt-phone-assistant
Reference commit: b887e8bc6cb68ffe86ab4e94052a3dcdb5d98221
HMG-API button API, signing tool, and Car Check phone remap example:
https://github.com/VysseCodes/HMG-API
Reference commit: 180185de2c57afb2cca4858d0be7828e8f1051d6
The MIT license here applies to this small declarative mod and its notes;
HMG-API itself is separately licensed AGPL-3.0.
