# coding: utf-8
"""Load the user's original Qt4 DLL in its bundled 32-bit Python, in a separate process."""
import ctypes as c, os, sys, json
from pathlib import Path
assert c.sizeof(c.c_void_p)==4
base=Path(os.environ['PROTEUS_DIR'])/'BIN'
os.add_dll_directory(str(base))
qt=c.WinDLL(str(base/'QtCore4.dll'))
k=c.WinDLL('kernel32')
k.VirtualAlloc.argtypes=[c.c_void_p,c.c_size_t,c.c_uint,c.c_uint];k.VirtualAlloc.restype=c.c_void_p
stubs={}
def invoke(symbol, obj, *args):
    n=len(args)
    if n not in stubs:
        code=b'\x55\x8b\xec'
        for i in reversed(range(n)):code+=b'\xff\x75'+bytes([16+4*i])
        code+=b'\x8b\x4d\x0c\x8b\x45\x08\xff\xd0\x8b\xe5\x5d\xc3'
        ptr=k.VirtualAlloc(None,len(code),0x3000,0x40);c.memmove(ptr,code,len(code))
        stubs[n]=c.CFUNCTYPE(c.c_uint32,*([c.c_void_p]*(n+2)))(ptr)
    func=c.cast(getattr(qt,symbol),c.c_void_p).value
    return stubs[n](func,c.addressof(obj),*args)

class Translator:
    def __init__(self,path):
        self.obj=c.create_string_buffer(128)
        invoke('??0QTranslator@@QAE@PAVQObject@@@Z',self.obj,None)
        self.data=c.create_string_buffer(Path(path).read_bytes())
        assert invoke('?load@QTranslator@@QAE_NPBEH@Z',self.obj,c.addressof(self.data),len(self.data)-1)&255
    def lookup(self,ctx,src,comment='',n=-1,source_encoding='utf-8'):
        result=c.create_string_buffer(4)
        buffers=[c.create_string_buffer(s.encode(encoding)) for s,encoding in [(ctx,'utf-8'),(src,source_encoding),(comment,'utf-8')]]
        # QString returned by value uses the caller-provided result address.
        invoke('?translate@QTranslator@@QBE?AVQString@@PBD00H@Z',self.obj,c.addressof(result),*[c.addressof(b) for b in buffers],n&0xffffffff)
        length=invoke('?size@QString@@QBEHXZ',result)
        ptr=invoke('?constData@QString@@QBEPBVQChar@@XZ',result)
        value=c.string_at(ptr,length*2).decode('utf-16-le')
        invoke('??1QString@@QAE@XZ',result)
        return value
    def close(self):invoke('??1QTranslator@@UAE@XZ',self.obj)

def qstring(value):
    result=c.create_string_buffer(4)
    utf16=c.create_string_buffer(value.encode('utf-16-le'))
    invoke('??0QString@@QAE@PBVQChar@@H@Z',result,c.addressof(utf16),len(value))
    return result

def system_locale():
    locale=c.create_string_buffer(32)
    address=c.cast(getattr(qt,'?system@QLocale@@SA?AV1@XZ'),c.c_void_p).value
    c.CFUNCTYPE(c.c_void_p,c.c_void_p)(address)(c.addressof(locale))
    name=c.create_string_buffer(4)
    invoke('?name@QLocale@@QBE?AVQString@@XZ',locale,c.addressof(name))
    length=invoke('?size@QString@@QBEHXZ',name)
    ptr=invoke('?constData@QString@@QBEPBVQChar@@XZ',name)
    text=c.string_at(ptr,length*2).decode('utf-16-le')
    invoke('??1QString@@QAE@XZ',name)
    return locale,text

if __name__=='__main__':
    if len(sys.argv)==2 and sys.argv[1]=='--locale':
        print(system_locale()[1])
    elif len(sys.argv)==3 and sys.argv[1]=='--locale-load':
        locale,text=system_locale()
        for prefix in ['proteus','qt']:
            obj=c.create_string_buffer(128);invoke('??0QTranslator@@QAE@PAVQObject@@@Z',obj,None)
            strings=[qstring(s) for s in [prefix,'_',str(Path(sys.argv[2]).resolve()),'.qm']]
            loaded=invoke('?load@QTranslator@@QAE_NABVQLocale@@ABVQString@@111@Z',obj,c.addressof(locale),*[c.addressof(s) for s in strings])&255
            print(prefix,text,'locale load:',bool(loaded));assert loaded
            invoke('??1QTranslator@@UAE@XZ',obj)
            for s in strings:invoke('??1QString@@QAE@XZ',s)
    elif len(sys.argv)==2:
        t=Translator(sys.argv[1]); print(repr(t.lookup('QDialogButtonBox','Cancel'))); t.close()
    else:
        root=Path(sys.argv[1]); records=json.loads(Path(sys.argv[2]).read_text(encoding='utf-8'))
        results=[]
        for name,rs in records.items():
            t=Translator(root/name);checked=0
            for r in rs:
                expected=r['translations'][0] if r['translations'] else ''
                if not expected or len(r['translations'])!=1:continue
                got=t.lookup(r['context'],r['source'],r['comment'])
                if got!=expected and any(ord(ch)>127 for ch in r['source']):
                    try:got=t.lookup(r['context'],r['source'],r['comment'],source_encoding='latin1')
                    except UnicodeEncodeError:pass
                assert got==expected,(name,r['context'],r['source'],repr(got),repr(expected))
                checked+=1
            t.close();results.append({'file':name,'Qt4_lookups_passed':checked})
        print(json.dumps(results))
