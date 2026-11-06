# Phone Assistant PTT for HMG-API

An alternative package for HMG-API 1.0.2 or newer. Its single declarative input
binding maps `ptt short` to `ptt hold`, following HMG-API's Car Check phone
assistant example. The existing NEMESIS package is a separate installation route.

The short press is recognized **on release**, rather than changing the original
ODEX timer to zero. A physical long press retains stock behavior. This requires
working HMG-API input hooks for the car and a connected phone for projection voice;
it does not add hook maps or projection connectivity. This adaptation has only
been tested off-car. Check short/long presses, duplicate activation, audio playback,
and removal while parked before relying on it.

## Install

1. Uninstall the original `hkmc.ptt-phone-assistant` NEMESIS patch, if installed,
   and fully restart. Disable competing voice-button remaps.
2. Put the signed `ptt-phone-assistant-1.0.0.zip` in `HMGAPI/updates/` on a USB stick.
3. Choose **Check USB updates** in HMG-API, install the mod, then **Apply changes**.
   A new personal author key produces HMG-API's unknown-author warning.
4. Follow any restart instruction and test while parked. Turn off/remove the mod
   and Apply changes to restore the normal button routing.

The ZIP installs on the head unit; sending it to a phone is just file transfer.
Detailed owner instructions also ship inside the ZIP as `README.txt`.

## Build locally

Needs Python 3.9+, JDK 17, Git, and the upstream HMG-API engine sources. No Android
SDK or manufacturer firmware is needed. From this repository:

```sh
git clone https://github.com/VysseCodes/HMG-API.git ../HMG-API
git -C ../HMG-API checkout 180185de2c57afb2cca4858d0be7828e8f1051d6
mkdir -p ../HMG-API/out/engine-host
javac --release 8 -d ../HMG-API/out/engine-host ../HMG-API/core/runtime/java/hmgapi/engine/*.java
mkdir -p "$HOME/hmg-private/keys"
java -cp ../HMG-API/out/engine-host hmgapi.engine.Signing keygen "$HOME/hmg-private/keys/ptt-phone-assistant.key"
python src/build_hmgapi.py --hmgapi ../HMG-API --key "$HOME/hmg-private/keys/ptt-phone-assistant.key"
python tests/test_hmgapi.py --hmgapi ../HMG-API --classes ../HMG-API/out/engine-host
```

Generate the key only once. Keep both it and its `.pub` file outside this repository
and backed up: HMG-API requires the same signing identity for future updates.
The builder stages files temporarily, uses the official upstream signer, verifies
the extracted ZIP, and writes the ZIP and SHA-256 checksum to `out/hmgapi/`.
It never includes the private key. ZIP entry ordering, permissions and timestamps
are fixed; ECDSA signatures can vary between builds.

## GitHub builds and releases

`.github/workflows/hmgapi.yml` builds on pull requests, main pushes, and manual
dispatch. It pins HMG-API to the commit above, needs no secrets for CI, checks
installation/planning/removal and tamper rejection with the real host engine,
and runs upstream button tests. The uploaded development artifact uses a disposable
key: it is for testing and **cannot update a package signed by a different key**.

For stable releases, maintainers configure repository Actions secrets:

- `HMGAPI_SIGNING_KEY`: exact text contents of the persistent private key file.
- `HMGAPI_SIGNING_PUBLIC_KEY`: exact text contents of its matching `.pub` file.

Push `hmgapi-v1.0.0` (matching `hmgapi/mod/mod.json`). The release job requires
both secrets, signs with that identity, and creates a **draft** GitHub release
with the ZIP and checksum for review. It never substitutes a disposable identity
for a missing release key. Keep that identity for all later releases; the personal
package previously sent to the phone can only be updated using its original key.
No signing secrets or release tags need to be created just to merge this PR.

API reference: https://github.com/VysseCodes/HMG-API/blob/180185de2c57afb2cca4858d0be7828e8f1051d6/docs/mod-reference.md
