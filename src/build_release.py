#!/usr/bin/env python3
"""Build source, installer and recovery bundle; excludes all vendor binaries."""
from pathlib import Path
import io, zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/'hkmc-ptt-phone-assistant-0.1.0-alpha-release.zip'
buf=io.BytesIO()
with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
    for f in sorted((ROOT/'package').rglob('*')):
        if f.is_file():z.write(f,f.relative_to(ROOT/'package').as_posix())
installer='[nemesis]\nversion=0.1.0-alpha\ntype=install\npath=packages/hkmc.ptt-phone-assistant.nemesis.zip\n'
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('INSTALL-USB/NEMESIS.data',installer)
    z.writestr('INSTALL-USB/packages/hkmc.ptt-phone-assistant.nemesis.zip',buf.getvalue())
    for f in sorted((ROOT/'recovery').iterdir()):z.write(f,'RECOVERY-USB/'+f.name)
    z.write(ROOT/'package/scripts/common.sh','RECOVERY-USB/recovery-common.sh')
    for f in sorted(ROOT.rglob('*')):
        if f.is_file() and '__pycache__' not in f.parts:
            z.write(f,'SOURCE/'+f.relative_to(ROOT).as_posix())
    for n in ['README.md','VALIDATION.txt','LICENSE']:z.write(ROOT/n,n)
with zipfile.ZipFile(OUT) as z:
    assert z.testzip() is None
    for n in z.namelist():
        assert not n.endswith(('.odex','.dex','.apk','.jar'))
    with zipfile.ZipFile(io.BytesIO(z.read('INSTALL-USB/packages/hkmc.ptt-phone-assistant.nemesis.zip'))) as inner:
        assert inner.testzip() is None
        assert 'NEMESIS.data' in inner.namelist()
        assert inner.read('patch/delay.bin')==b'\0\0'
print(OUT)
