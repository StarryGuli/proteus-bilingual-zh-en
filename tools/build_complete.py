import os
# coding: utf-8
from pathlib import Path
import json, re, struct, copy, hashlib, zipfile, xml.etree.ElementTree as ET, html, collections
from qm_catalog import read_qm, MAGIC
from qscintilla_zh import translate as editor_translate
from new_labels_zh import ZH as NEW_ZH

ROOT=Path(__file__).resolve().parent.parent
SOURCE=Path(os.environ['ORIGINAL_PATCH_DIR'])
OUT=ROOT/'outputs/Proteus-8.17-Bilingual-v2'
DEST=OUT/'Translations'
DEST.mkdir(parents=True,exist_ok=True)
HAN=re.compile('[\u3400-\u9fff]')
PRINTF=re.compile(r'%(?!%)(?:\d+\$)?[-+#0 ]*(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|ll|[hljztL])?[diuoxXfFeEgGaAcspn]')
def canon(s):return re.sub('[^a-z0-9]','',s.lower())
def key(r):return (r['context'],r['source'],r['comment'])

def bilingual(en,zh):
    if not zh or not HAN.search(zh):return en
    if not en:return zh
    zh=re.sub(r'[（(]\s*&[A-Za-z]\s*[）)]','',zh)
    zh=re.sub(r'&(?!#\d+;|[a-zA-Z]+;)','',zh)
    # printf-style tokens must occur only in the original English half.
    if PRINTF.search(en) and not re.search(r'%[1-9]',en):
        zh=PRINTF.sub('〔同前〕',zh)
        zh=zh.replace('%%','％')
    if '\t' in en:
        label,shortcut=en.split('\t',1)
        return label+' '+zh.split('\t',1)[0].strip()+'\t'+shortcut
    # Preserve filter syntax instead of duplicating the wildcard list.
    if re.search(r'\([^)]*\*[^)]*\)',en):
        en_parts=en.split(';;'); zh_parts=zh.split(';;')
        if len(en_parts)==len(zh_parts):
            parts=[]
            for a,b in zip(en_parts,zh_parts):
                match=re.search(r'\s*(\([^)]*\*[^)]*\))\s*$',a)
                if not match:return en+' '+zh
                label=re.sub(r'\s*\([^)]*\*[^)]*\)\s*$','',b).strip()
                parts.append(a[:match.start()].strip()+' '+label+' '+match.group(1))
            return ';;'.join(parts)
    if re.search(r'<(?:html|body|qt)\b',en,re.I):
        body=re.search(r'<body[^>]*>(.*?)</body>',zh,re.I|re.S)
        addition=body.group(1) if body else re.sub(r'</?(?:html|qt)[^>]*>','',zh,flags=re.I)
        for ending in ['</body>','</qt>','</html>']:
            pos=en.lower().rfind(ending)
            if pos>=0:return en[:pos]+'<hr/>'+addition+en[pos:]
    return en+ ('\n' if '\n' in en else ' ')+zh.strip()

def elfhash(data):
    h=0
    for ch in data:
        h=(h<<4)+ch;g=h&0xf0000000
        if g:h^=g>>24
        h&=~g
    return h or 1

def encode_field(tag,value,encoding='utf-8'):
    raw=value.encode(encoding)
    return bytes([tag])+struct.pack('>I',len(raw))+raw

def patch_qm(path,records,extra,target):
    """Change only translation payloads and hash offsets; preserve original lookup bytes."""
    b=path.read_bytes();blocks=[];i=16
    while i<len(b):
        tag=b[i];n=int.from_bytes(b[i+1:i+5],'big');i+=5
        blocks.append((tag,b[i:i+n]));i+=n
    blocks_dict=dict(blocks);d=blocks_dict[0x69];new=bytearray();i=0;index=0;ti=0
    offsets={0:0}
    while i<len(d):
        start=i;tag=d[i];i+=1
        if tag==1:
            new.append(tag);index+=1;ti=0;offsets[i]=len(new);continue
        if tag==9:
            i+=4;new.extend(d[start:i]);continue
        n=int.from_bytes(d[i:i+4],'big');i+=4
        if n!=0xffffffff:i+=n
        if tag==3:
            values=records[index]['translations']
            value=values[ti] if ti<len(values) else '';ti+=1
            new.extend(encode_field(3,value,'utf-16-be'))
        else:new.extend(d[start:i])
    assert index==len(records)
    hashes=[]
    old=blocks_dict[0x42]
    for i in range(0,len(old),8):
        h,offset=struct.unpack_from('>II',old,i)
        hashes.append((h,offsets[offset]))
    for r in extra:
        assert len(r['translations'])==1
        offset=len(new)
        new.extend(encode_field(3,r['translations'][0],'utf-16-be'))
        new.extend(encode_field(8,r['comment']))
        new.extend(encode_field(6,r['source']))
        new.extend(encode_field(7,r['context']))
        new.append(1)
        hashes.append((elfhash((r['source']+r['comment']).encode('utf-8')),offset))
    replacements={0x69:bytes(new),0x42:b''.join(struct.pack('>II',h,o) for h,o in sorted(hashes))}
    result=bytearray(MAGIC)
    for tag,data in blocks:
        if tag==0x2f and extra:continue
        data=replacements.get(tag,data)
        result.extend(bytes([tag])+struct.pack('>I',len(data))+data)
    target.write_bytes(result)
    decoded=read_qm(target)
    assert [key(r) for r in decoded]==[key(r) for r in records+extra]
    assert [r['translations'] for r in decoded]==[r['translations'] for r in records+extra]

original={name:read_qm(SOURCE/name) for name in ['proteus_zh_CN.qm','qt_zh_CN.qm']}
source_map={}
for rs in original.values():
    for r in rs:
        if r['translations'] and HAN.search(r['translations'][0]):
            source_map.setdefault(canon(r['source']),r['translations'][0])
for source,zh in NEW_ZH.items():source_map[canon(source)]=zh
source_map.update({canon('Switch to colourset as set on the View/Layers command)'):'切换到“视图／图层”命令设置的配色方案',canon('Set Layer Usage'):'设置图层用途',canon('Find Next'):'查找下一个'})
for source,zh in {"Dest'n:":'目标：',"Dest'n (None):":'目标（无）：',"Dest'n (Read only):":'目标（只读）：',"Dest'n (v1.xx/v2.xx):":'目标（v1.xx/v2.xx）：','Cat.':'类别','Sub-Cat.':'子类别'}.items():source_map[canon(source)]=zh

catalogs={};stats={};coverage=[]
for name,base_records in original.items():
    records=copy.deepcopy(base_records);changed=0
    for r in records:
        values=r['translations'] or ['']
        for i,value in enumerate(values):
            if r['context']=='ConfirmationDialog' and 'Do you want reports regarding recently experienced problems' in r['source']:
                value=r['source'].replace('Do you want reports regarding recently experienced problems to be uploaded to Labcenter server?','是否将最近遇到的问题报告上传到 Labcenter 服务器？').replace('It is vitally important for Labcenter team to know details about all kinds of problems with Proteus software.','了解 Proteus 软件各种问题的详细情况，有助于 Labcenter 团队改进软件。')
            if not HAN.search(value):value=source_map.get(canon(r['source']),value)
            if r['source']=='QT_LAYOUT_DIRECTION':result=values[i] or 'LTR'
            else:result=bilingual(r['source'],value)
            changed+=int(HAN.search(result) is not None)
            values[i]=result
        r['translations']=values
    extras=[];keys={key(r) for r in records}
    if name.startswith('proteus'):
        editor=json.loads((ROOT/'work/qscintilla_sources.json').read_text(encoding='utf-8'))
        for r in editor:
            r=copy.deepcopy(r);r['translations']=[bilingual(r['source'],editor_translate(r['source']))]
            if key(r) not in keys:extras.append(r);keys.add(key(r))
        editor_count=len(extras)
        # Mirror actual resource-name casing, and the CORE namespace used by PDS.
        old_contexts=collections.defaultdict(set)
        for r in records:old_contexts[r['context'].lower()].add(r['context'])
        labels=json.loads((ROOT/'work/current-ui-labels.json').read_text(encoding='utf-8'))
        added_labels=set()
        for r in labels:
            zh=source_map.get(canon(r['source']))
            if not zh or not HAN.search(zh):continue
            header,resname=r['context'].split('\\',1)
            headers={header}
            if header.endswith(': PDS'):headers.add(header[:-3]+'CORE')
            contexts=set()
            for h in headers:
                contexts.update([h+'\\'+resname,h+'\\'+resname.lower()])
                contexts.update(old_contexts[(h+'\\'+resname).lower()])
            for ctx in contexts:
                new=dict(context=ctx,source=r['source'],comment='',translations=[bilingual(r['source'],zh)])
                if key(new) not in keys:
                    extras.append(new);keys.add(key(new));added_labels.add(r['source'])
        stats['editor_entries_added']=editor_count
        stats['native_resource_alias_entries_added']=len(extras)-editor_count
        stats['native_resource_distinct_labels_added']=len(added_labels)
    else:
        tree=ET.parse(ROOT/'work/official-qt4-zh_CN.ts')
        for ctx in tree.findall('context'):
            for msg in ctx.findall('message'):
                tr=msg.find('translation')
                if tr is None or tr.get('type') in ['obsolete','unfinished','vanished']:continue
                zh=tr.text or ''
                if not HAN.search(zh):continue
                r=dict(context=ctx.findtext('name'),source=msg.findtext('source') or '',comment=msg.findtext('comment') or '',translations=[bilingual(msg.findtext('source') or '',zh)])
                if key(r) not in keys:extras.append(r);keys.add(key(r))
    patch_qm(SOURCE/name,records,extras,DEST/name)
    catalogs[name]=records+extras
    stats[name]={'original_entries':len(records),'bilingual_original_entries':changed,'additional_entries':len(extras),'total_entries':len(records)+len(extras)}

# This user's Qt4 system locale is en_US. Keep the Chinese names as well for portability.
for stem in ['proteus','qt']:
    (DEST/(stem+'_en_US.qm')).write_bytes((DEST/(stem+'_zh_CN.qm')).read_bytes())

# Validate formatting-sensitive tokens in every modified original record.
for name,records in catalogs.items():
    for r in records:
        en=r['source'];value=r['translations'][0] if r['translations'] else ''
        if PRINTF.search(en) and not re.search(r'%[1-9]',en):
            assert PRINTF.findall(en)==PRINTF.findall(value),(name,r['context'],en,value)
        if '\t' in en:assert value.split('\t',1)[-1]==en.split('\t',1)[-1]

(ROOT/'work/complete-catalogs.json').write_text(json.dumps(catalogs,ensure_ascii=False),encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(stats,ensure_ascii=False,indent=2))
