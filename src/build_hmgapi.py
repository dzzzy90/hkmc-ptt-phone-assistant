#!/usr/bin/env python3
"""Build a signed HMG-API mod using the upstream Java signing implementation."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def build(upstream, key, output):
    upstream, key, output = upstream.resolve(), key.resolve(), output.resolve()
    if not key.is_file() or not Path(str(key) + '.pub').is_file():
        raise ValueError('Provide an author private key and matching <key>.pub; see hmgapi/README.md')
    sources = sorted((upstream / 'core/runtime/java/hmgapi/engine').glob('*.java'))
    if not sources:
        raise ValueError('No HMG-API engine sources found')
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        cp = work / 'classes'
        cp.mkdir()
        subprocess.run(['javac', '--release', '8', '-Xlint:-options', '-nowarn', '-d', str(cp),
                        *map(str, sources)], check=True)
        mod = work / 'mod'
        shutil.copytree(ROOT / 'hmgapi/mod', mod)
        signer = ['java', '-cp', str(cp), 'hmgapi.engine.Signing']
        subprocess.run([*signer, 'sign', str(mod), str(key)], check=True)
        subprocess.run([*signer, 'verify', str(mod)], check=True)
        meta = json.loads((mod / 'mod.json').read_text())
        output.mkdir(parents=True, exist_ok=True)
        target = output / ('%s-%s.zip' % (meta['id'], meta['version']))
        with zipfile.ZipFile(target, 'w') as archive:
            for path in sorted(mod.rglob('*')):
                if path.is_file():
                    entry = zipfile.ZipInfo(path.relative_to(mod).as_posix(), (2026, 1, 1, 0, 0, 0))
                    entry.compress_type = zipfile.ZIP_DEFLATED
                    entry.external_attr = 0o100644 << 16
                    archive.writestr(entry, path.read_bytes())
        # Verify the actual ZIP contents, including extraction and signatures.
        extracted = work / 'extracted'
        with zipfile.ZipFile(target) as archive:
            assert archive.testzip() is None
            archive.extractall(extracted)
        subprocess.run([*signer, 'verify', str(extracted)], check=True)
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        (output / 'SHA256SUMS.txt').write_text(digest + '  ' + target.name + '\n', encoding='utf-8')
        print(target)
        return target


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hmgapi', type=Path, required=True, help='Pinned HMG-API source checkout')
    parser.add_argument('--key', type=Path, required=True, help='Author key; matching .pub must exist')
    parser.add_argument('--output', type=Path, default=ROOT / 'out/hmgapi')
    args = parser.parse_args()
    build(args.hmgapi, args.key, args.output)
