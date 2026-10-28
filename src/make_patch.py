#!/usr/bin/env python3
"""Locate a named DEX method in the supplied ODEX; emit only changed bytes.
No vendor binary is included in the release. Standard-library only.
"""
import hashlib, json, struct, sys, zlib
from pathlib import Path

def build(source, output):
    original = Path(source).read_bytes()
    assert original[:8] == b'dey\n036\0', 'Unexpected ODEX format'
    dexoff, dexlen = struct.unpack_from('<II', original, 8)
    d = original[dexoff:dexoff+dexlen]
    assert d[:8] == b'dex\n035\0', 'Unexpected DEX format'
    def u32(off): return struct.unpack_from('<I', d, off)[0]
    def uleb(off):
        value = shift = 0
        for _ in range(5):
            b = d[off]; off += 1; value |= (b & 127) << shift
            if b < 128: return value, off
            shift += 7
        raise ValueError('Bad ULEB128')
    strings = []
    for i in range(u32(56)):
        off = u32(u32(60)+4*i); _, off = uleb(off)
        strings.append(d[off:d.index(0,off)].decode('utf-8',errors='replace'))
    types = [strings[u32(u32(68)+4*i)] for i in range(u32(64))]
    methods = []
    for i in range(u32(88)):
        c,p,n = struct.unpack_from('<HHI',d,u32(92)+8*i)
        methods.append((types[c],strings[n],p))
    matches = []
    for i in range(u32(96)):
        row = struct.unpack_from('<8I',d,u32(100)+32*i)
        if types[row[0]] != 'Lcom/hkmc/micom/ModeKeyDispatcher;': continue
        off = row[6]; counts=[]
        for _ in range(4): val,off=uleb(off);counts.append(val)
        for _ in range(counts[0]+counts[1]):
            _,off=uleb(off);_,off=uleb(off)
        for count in counts[2:]:
            index=0
            for _ in range(count):
                diff,off=uleb(off);index+=diff
                _,off=uleb(off);code,off=uleb(off)
                if methods[index][1]=='interceptPttKey':matches.append(code)
    assert len(matches)==1, 'Named method not unique'
    code=matches[0]
    registers,ins,outs,tries,debug,n=struct.unpack_from('<4H2I',d,code)
    assert (registers,ins,tries,n)==(5,1,0,21), 'Method shape changed'
    # Disassembly verified: code-unit 0xf is const-wide/16 v2, 500.
    instruction=d[code+16+30:code+16+34]
    assert instruction==bytes.fromhex('1602f401'), 'Delay instruction changed'
    assert zlib.adler32(d[12:]) & 0xffffffff == u32(8), 'Invalid source DEX checksum'
    offset=dexoff+code+16+32
    patched=bytearray(original);patched[offset:offset+2]=b'\0\0'
    checksum=zlib.adler32(patched[dexoff+12:dexoff+dexlen]) & 0xffffffff
    struct.pack_into('<I',patched,dexoff+8,checksum)
    # ODEX retains the pre-optimization DEX signature used by dependency records.
    # Optimized DEX bytes already do not match that signature in the source.
    assert patched[dexoff+12:dexoff+32]==original[dexoff+12:dexoff+32]
    assert patched[dexoff+dexlen:]==original[dexoff+dexlen:]
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    (out/'delay.bin').write_bytes(b'\0\0')
    (out/'checksum.bin').write_bytes(struct.pack('<I',checksum))
    manifest={'method':'Lcom/hkmc/micom/ModeKeyDispatcher;->interceptPttKey()V',
      'delay_offset':offset,'checksum_offset':dexoff+8,'size':len(original),
      'original_md5':hashlib.md5(original).hexdigest(),'patched_md5':hashlib.md5(patched).hexdigest(),
      'original_sha256':hashlib.sha256(original).hexdigest(),'patched_sha256':hashlib.sha256(patched).hexdigest(),
      'old_delay_ms':500,'new_delay_ms':0,'code_offset':dexoff+code,
      'changed_offsets':[i for i,(a,b) in enumerate(zip(original,patched)) if a!=b]}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (out/'values.sh').write_text('ORIGINAL_MD5='+manifest['original_md5']+'\nPATCHED_MD5='+manifest['patched_md5']+'\nDELAY_OFFSET='+str(offset)+'\nCHECKSUM_OFFSET='+str(dexoff+8)+'\n')
    return manifest,bytes(patched)

if __name__=='__main__':
    manifest,_=build(sys.argv[1],sys.argv[2]);print(json.dumps(manifest,indent=2))
