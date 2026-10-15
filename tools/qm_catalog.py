import os
# coding: utf-8
from pathlib import Path
import xml.etree.ElementTree as ET

MAGIC = bytes.fromhex('3cb86418caef9c95cd211cbf60a1bddd')
def read_qm(path):
    b = Path(path).read_bytes()
    assert b[:16] == MAGIC
    blocks = {}; i=16
    while i<len(b):
        tag=b[i]; n=int.from_bytes(b[i+1:i+5],'big'); i+=5
        assert i+n <= len(b)
        blocks[tag]=b[i:i+n]; i+=n
    d=blocks[0x69]; i=0; records=[]; source=''; context=''; comment=''; trs=[]
    while i<len(d):
        tag=d[i]; i+=1
        if tag==1:
            records.append(dict(context=context, source=source, comment=comment, translations=trs))
            trs=[]; comment=''; continue
        if tag==9: i+=4; continue
        assert tag in (2,3,4,6,7,8), (tag,i)
        n=int.from_bytes(d[i:i+4],'big'); i+=4
        # QByteArray/QString serialize null as UINT32_MAX, consuming no payload.
        if n==0xffffffff: value=''
        else:
            assert i+n<=len(d), (i,n,len(d))
            raw=d[i:i+n]; i+=n
            if tag in (2,3,4): value=raw.decode('utf-16-be', errors='strict')
            else:
                try: value=raw.decode('utf-8')
                except UnicodeDecodeError: value=raw.decode('latin1')
        if tag==3: trs.append(value)
        elif tag in (2,6): source=value
        elif tag in (4,7): context=value
        elif tag==8: comment=value
    assert len(records)==len(blocks[0x42])//8, (len(records),len(blocks[0x42])//8)
    return records

def write_ts(records,path):
    root=ET.Element('TS',version='2.1',language='zh_CN',sourcelanguage='en'); contexts={}
    for r in records:
        key=r['context']
        if key not in contexts:
            ctx=ET.SubElement(root,'context'); ET.SubElement(ctx,'name').text=key; contexts[key]=ctx
        m=ET.SubElement(contexts[key],'message'); ET.SubElement(m,'source').text=r['source']
        if r['comment']: ET.SubElement(m,'comment').text=r['comment']
        t=ET.SubElement(m,'translation')
        if len(r['translations'])>1:
            m.set('numerus','yes')
            for value in r['translations']: ET.SubElement(t,'numerusform').text=value
        else: t.text=r['translations'][0] if r['translations'] else ''
    ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)

if __name__=='__main__':
    import json, collections
    folder=Path(os.environ['ORIGINAL_PATCH_DIR'])
    for name in ['proteus_zh_CN.qm','qt_zh_CN.qm']:
        rs=read_qm(folder/name)
        print(name,len(rs),'records;',sum(any(t for t in r['translations']) for r in rs),'nonempty')
        print(collections.Counter(r['context'] for r in rs).most_common(25))
        Path('work/'+name+'.full.json').write_text(json.dumps(rs,ensure_ascii=False,indent=2),encoding='utf-8')
