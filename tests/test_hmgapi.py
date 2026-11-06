#!/usr/bin/env python3
"""Exercise the signed ZIP with the real HMG-API host engine, without a car."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--hmgapi', type=Path, required=True)
p.add_argument('--classes', type=Path, required=True)
a = p.parse_args()
cp = str(a.classes.resolve())
meta = json.loads((ROOT / 'hmgapi/mod/mod.json').read_text())
package = ROOT / 'out/hmgapi' / ('%s-%s.zip' % (meta['id'], meta['version']))
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp) / 'root'
    (root / 'system').mkdir(parents=True)
    env = dict(os.environ, HMGAPI_HOST='1', HMGAPI_ROOT=str(root),
               HMGAPI_PRODUCT='NEEV23.USA.S5W_M.V015.012.260507', HMGAPI_ONEBIN='neev_us')

    def engine(*args, ok=True):
        # Upstream LiveState uses File.renameTo over an existing file, which
        # works on the Linux head unit/CI but fails on Windows host JVMs.
        if os.name == 'nt':
            (root / 'data/hmgapi/public/state.json').unlink(missing_ok=True)
            (root / 'actions.log').unlink(missing_ok=True)
        result = subprocess.run(['java', '-cp', cp, 'hmgapi.engine.Engine', *map(str, args)],
                                env=env, text=True, capture_output=True, timeout=30)
        print(result.stdout, end='')
        assert (result.returncode == 0) == ok, result.stdout + result.stderr
        return result.stdout

    engine('install', package)
    plan = engine('plan')
    assert "ptt short (instead of the car's) -> the car gets ptt hold" in plan
    assert not (root / 'system/framework').exists(), 'Declarative mod must not patch the framework'
    bad = Path(tmp) / 'tampered.zip'
    with zipfile.ZipFile(package) as src, zipfile.ZipFile(bad, 'w') as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            dst.writestr(item, data + b' ' if item.filename == 'mod.json' else data)
    assert 'refused:' in engine('install', bad, ok=False)
    engine('remove', 'ptt-phone-assistant')
    assert 'button   ptt short' not in engine('plan')

subprocess.run(['javac', '--release', '8', '-d', cp,
                str(a.hmgapi / 'core/runtime/java/hmgapi/hook/KeyPresses.java'),
                str(a.hmgapi / 'core/runtime/test/hmgapi/hook/KeyPressesTest.java')], check=True)
subprocess.run(['java', '-cp', cp, 'hmgapi.hook.KeyPressesTest'], check=True)
print('PASS signed install, remap plan, tamper rejection, removal, upstream button tests')
