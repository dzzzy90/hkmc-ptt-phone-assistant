# v0.1.0-alpha — Phone Assistant PTT

Routes short and held steering-wheel voice-button presses into the factory
long-press assistant path, removing its 500 ms delay.

Owner reports successful operation on a **2022 Hyundai Ioniq 5 Limited USA**,
firmware **NEEV23.USA.S5W_M.V015.012.260507**. CarPlay and Android Auto have not
been separately confirmed. This is an experimental release for exact framework
checksums, not a general Hyundai/Kia compatibility claim.

The installer now accepts a second inspected build: **Kia EV6**, firmware
**CVEV.USA.0000.V015.012.260507** (`ro.product.device` `wp_daudioplus_cvev_us`). Its
`automotive-service.odex` carries the identical six-byte patch site at identical
offsets, so only the accepted checksums differ from the Ioniq 5 pair. Installed on a US Kia
EV6 on 2026-10-31: the installer selected `ev6-cvev-us-260507`, and after a full head-unit
restart the owner reports the short press activates the phone projection assistant with long
press behaviour unchanged. CarPlay and Android Auto, and the uninstall round-trip, have not been
separately re-confirmed on that car. Uninstall before any firmware update, as with the Ioniq 5.

Download `hkmc-ptt-phone-assistant-0.1.0-alpha-release.zip` below, extract it,
and follow README.md. Copy the contents of INSTALL-USB to the USB root.
NEMESIS must already be installed. Install while parked, wait for success,
then fully restart the head unit.

Includes source, guarded installer, original-file backup, uninstall, and
independent USB restore launcher. USB restore requires a working NEMESIS
USB handler. No vendor framework binaries or vehicle diagnostic logs are shipped.

Uninstall before firmware updates. Do not bypass the compatibility checks.
