import os
# coding: utf-8
import ctypes as c, struct, json
from pathlib import Path
exec(Path('work/inspect_resources.py').read_text(encoding='utf-8').split('base=Path')[0])
base=Path(os.environ['PROTEUS_DIR'])/'BIN'
class Cursor:
 def __init__(self,b): self.b=b;self.i=0
 def u16(self):v=struct.unpack_from('<H',self.b,self.i)[0];self.i+=2;return v
 def u32(self):v=struct.unpack_from('<I',self.b,self.i)[0];self.i+=4;return v
 def skip(self,n):self.i+=n
 def align(self):self.i=(self.i+3)&~3
 def text(self):
  v=self.u16()
  if v==0xffff:return '#'+str(self.u16())
  vals=[]
  while v:vals.append(v);v=self.u16()
  return struct.pack('<'+'H'*len(vals),*vals).decode('utf-16-le')

def dialog(data):
 r=Cursor(data);extended=struct.unpack_from('<HH',data)==(1,65535)
 if extended:
  r.skip(12);style=r.u32();count=r.u16();r.skip(8)
 else:style=r.u32();r.skip(4);count=r.u16();r.skip(8)
 r.text();r.text();texts=[r.text()]
 if style&0x40:r.skip(6 if extended else 2);r.text()
 for i in range(count):
  r.align();r.skip(24 if extended else 18);r.text();texts.append(r.text());r.skip(r.u16())
 return [s for s in texts if s and not s.startswith('#')]

def menu(data):
 r=Cursor(data);version=r.u16();offset=r.u16();r.skip(offset);texts=[]
 def items():
  while True:
   if version==0:
    flags=r.u16();popup=bool(flags&16)
    if not popup:r.u16()
    title=r.text()
   else:
    r.align();r.skip(12);flags=r.u16();popup=bool(flags&1);title=r.text();r.align()
    if popup:r.skip(4)
   if title:texts.append(title)
   if popup:items()
   if flags&128:break
 items();return texts

def normalize_label(text):
 if not text:return []
 if ord(text[0])>=128:
  kind=ord(text[0]);text=text[1:]
  if text.startswith('='):
   index={0x97:5,0x93:4,0x95:4,0xb0:3}.get(kind)
   if index is None:return []
   fields=text.split(',',index)
   if len(fields)<=index:return []
   text=fields[-1]
 elif __import__('re').match(r'^[0-9A-F]{4},',text):
  fields=text.split(',',2)
  text=fields[-1] if len(fields)==3 else ''
 if not text or text in ['*','-'] or text.startswith('=') or any(ord(ch)<32 and ch not in '\t\n\r' for ch in text):return []
 if (text.startswith(',') or text.startswith('W,')) and '=' in text:
  return [part.split('=',1)[0] for part in text.split(',') if '=' in part]
 return text.split('|') if '|' in text else [text]

result=[];errors=[]
for file in base.iterdir():
 if file.suffix.lower() not in ['.exe','.dll']:continue
 if file.name.lower().startswith(('qt','msvc','lib','qscintilla')):continue
 h=k.LoadLibraryExW(str(file),None,34)
 if not h:continue
 for typ in (4,5):
  @CB
  def cb(handle,rt,rid,param):
   try:
    name=str(rid) if rid<65536 else c.wstring_at(rid)
    resource=k.FindResourceW(h,rid,rt)
    data=c.string_at(k.LockResource(k.LoadResource(h,resource)),k.SizeofResource(h,resource))
    texts=(menu if rt==4 else dialog)(data)
    context=('MENU: ' if rt==4 else 'DLG: ')+file.stem.upper()+'\\'+name
    result.extend(dict(context=context,source=clean,comment='',translations=[]) for s in texts for clean in normalize_label(s))
   except Exception as e:errors.append([file.name,str(rid),str(e)])
   return True
  k.EnumResourceNamesW(h,typ,cb,0)
k.FreeLibrary.argtypes=[c.c_void_p]
original=json.loads(Path('work/proteus_zh_CN.qm.full.json').read_text(encoding='utf-8'))
keys={(r['context'].lower(),r['source']) for r in original}
source_map={r['source'].replace('&','').strip().lower():r['translations'][0] for r in original if r['translations'] and any('\u3400'<=ch<='\u9fff' for ch in r['translations'][0])}
missing=[];seen=set()
for r in result:
 key=(r['context'].lower(),r['source'])
 if key not in keys and key not in seen:missing.append(r);seen.add(key)
Path('work/current-ui-missing.json').write_text(json.dumps(missing,ensure_ascii=False,indent=2),encoding='utf-8')
Path('work/current-ui-labels.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('Extracted',len(result),'labels;',len(missing),'not in supplied catalog; errors',errors)
unknown=list(dict.fromkeys(r['source'] for r in missing if r['source'].replace('&','').strip().lower() not in source_map))
Path('work/current-ui-unknown.json').write_text(json.dumps(unknown,ensure_ascii=False,indent=2),encoding='utf-8')
print('New English labels without a reusable Chinese translation:',len(unknown))
for s in unknown: print(ascii(s))
