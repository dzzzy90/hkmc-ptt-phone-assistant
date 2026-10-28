#!/usr/bin/env python3
import hashlib, importlib.util, os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('make_patch',ROOT/'src/make_patch.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
source=Path(sys.argv[1]).resolve()

def run_case(name, action):
    with tempfile.TemporaryDirectory() as td:
        base=Path(td);pkg=base/'package';shutil.copytree(ROOT/'package',pkg)
        fw=base/'system/framework';fw.mkdir(parents=True)
        data=base/'data/nemesis';data.mkdir(parents=True)
        live=fw/'automotive-service.odex';live.write_bytes(source.read_bytes())
        bindir=base/'bin';bindir.mkdir()
        programs={
          'getprop':'#!/bin/sh\ncase "$1" in ro.product.device) echo "${TEST_DEVICE:-wp_daudioplus_neev_us}";; ro.build.version.sdk) echo 19;; esac\n',
          'nemesis':'#!/bin/sh\n[ "${TEST_REMOUNT_FAIL:-0}" = 0 ]\n',
          'chown':'#!/bin/sh\nexit 0\n',
          'md5':'#!'+sys.executable+'\nimport hashlib,sys\nprint(hashlib.md5(open(sys.argv[1],"rb").read()).hexdigest())\n'}
        for n,s in programs.items():p=bindir/n;p.write_text(s);p.chmod(0o755)
        common=pkg/'scripts/common.sh';s=common.read_text()
        s=s.replace('/system/framework',str(fw)).replace('/data/nemesis',str(data))
        s=s.replace('export PATH='+str(data)+'/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin','export PATH='+str(bindir)+':/usr/bin:/bin')
        common.write_text(s)
        def run(script,expected=0,**env):
            r=subprocess.run(['/bin/sh',script],cwd=pkg,env={**os.environ,**env},capture_output=True,text=True,timeout=15)
            assert r.returncode==expected,(name,script,r.returncode,r.stdout,r.stderr)
            return r
        action(pkg,live,data,run)
        print('PASS',name)

with tempfile.TemporaryDirectory() as td:
    manifest,patched=mod.build(source,td)
original=source.read_bytes()
assert len(manifest['changed_offsets'])==6
assert hashlib.md5(patched).hexdigest()==manifest['patched_md5']

def normal(pkg,live,data,run):
    run('scripts/preinstall.sh');run('scripts/install.sh')
    assert live.read_bytes()==patched
    backup=data/'backup/hkmc.ptt-phone-assistant/automotive-service.odex'
    assert backup.read_bytes()==original
    run('scripts/install.sh');assert backup.read_bytes()==original
    run('bin/status.sh')
    run('scripts/uninstall.sh');assert live.read_bytes()==original
    assert backup.read_bytes()==original
    run('scripts/uninstall.sh')
run_case('install, repeat install, status, uninstall, repeat uninstall',normal)

def altered(pkg,live,data,run):
    live.write_bytes(original+b'x');run('scripts/preinstall.sh',1)
    run('scripts/install.sh',1);assert live.read_bytes()==original+b'x'
run_case('wrong firmware rejected without mutation',altered)
run_case('wrong device rejected',lambda p,l,d,r:r('scripts/preinstall.sh',1,TEST_DEVICE='other'))

def corrupt(pkg,live,data,run):
    (pkg/'patch/delay.bin').write_bytes(b'xx')
    run('scripts/install.sh',1);assert live.read_bytes()==original
    assert not (live.parent/'.hkmc-ptt-phone-assistant.stage').exists()
run_case('corrupt payload rejected before replacement',corrupt)

def backup_bad(pkg,live,data,run):
    b=data/'backup/hkmc.ptt-phone-assistant';b.mkdir(parents=True)
    (b/'automotive-service.odex').write_bytes(b'wrong')
    run('scripts/install.sh',1);assert live.read_bytes()==original
run_case('bad backup rejected and retained',backup_bad)

def missing_backup(pkg,live,data,run):
    live.write_bytes(patched);run('scripts/install.sh',1);assert live.read_bytes()==patched
run_case('missing backup blocks patched reinstall',missing_backup)

def remount_bad(pkg,live,data,run):
    run('scripts/install.sh',1,TEST_REMOUNT_FAIL='1');assert live.read_bytes()==original
run_case('remount failure leaves original intact',remount_bad)

def changed_after(pkg,live,data,run):
    run('scripts/install.sh');live.write_bytes(patched+b'x')
    run('scripts/uninstall.sh',1);assert live.read_bytes()==patched+b'x'
run_case('uninstall refuses later firmware changes',changed_after)

def recovery(pkg,live,data,run):
    run('scripts/install.sh')
    recovery=pkg/'recovery';recovery.mkdir()
    shutil.copyfile(ROOT/'recovery/NEMESIS.sh',recovery/'NEMESIS.sh')
    shutil.copyfile(pkg/'scripts/common.sh',recovery/'recovery-common.sh')
    run(str(recovery/'NEMESIS.sh'));assert live.read_bytes()==original
run_case('independent USB recovery restores verified original',recovery)

for s in ROOT.rglob('*.sh'):
    subprocess.run(['/bin/sh','-n',str(s)],check=True)
print('PASS six-byte patch and shell syntax checks')
