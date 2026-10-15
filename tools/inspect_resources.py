import os
import ctypes as c, json, struct
from pathlib import Path
k=c.WinDLL('kernel32',use_last_error=True)
k.LoadLibraryExW.argtypes=[c.c_wchar_p,c.c_void_p,c.c_uint]; k.LoadLibraryExW.restype=c.c_void_p
k.FindResourceW.argtypes=[c.c_void_p,c.c_void_p,c.c_void_p]; k.FindResourceW.restype=c.c_void_p
k.LoadResource.argtypes=[c.c_void_p,c.c_void_p]; k.LoadResource.restype=c.c_void_p
k.LockResource.argtypes=[c.c_void_p]; k.LockResource.restype=c.c_void_p
k.SizeofResource.argtypes=[c.c_void_p,c.c_void_p]; k.SizeofResource.restype=c.c_uint
CB=c.WINFUNCTYPE(c.c_bool,c.c_void_p,c.c_void_p,c.c_void_p,c.c_ssize_t)
k.EnumResourceNamesW.argtypes=[c.c_void_p,c.c_void_p,CB,c.c_ssize_t]
base=Path(os.environ['PROTEUS_DIR'])/'BIN'
result=[]
for name in ['PDS.EXE','APPFRAME.DLL','ISIS.DLL','ARES.DLL','WINCORE.DLL','WINDIALOG.DLL','VSMSTUDIO.DLL']:
 h=k.LoadLibraryExW(str(base/name),None,2|32)
 strings=[]
 @CB
 def cb(handle,typ,rid,param):
  r=k.FindResourceW(h,rid,typ)
  data=c.string_at(k.LockResource(k.LoadResource(h,r)),k.SizeofResource(h,r))
  if typ==6:
   i=0
   for index in range(16):
    n=struct.unpack_from('<H',data,i)[0]; i+=2
    s=data[i:i+2*n].decode('utf-16-le'); i+=2*n
    if s: strings.append({'id':(rid-1)*16+index,'text':s})
  return True
 k.EnumResourceNamesW(h,6,cb,0)
 chinese=[s for s in strings if any('\u4e00'<=ch<='\u9fff' for ch in s['text'])]
 print(name,len(strings),'strings;',len(chinese),'Chinese;',repr(chinese[:2]))
 result.append({'file':name,'strings':strings})
Path('work/windows-resources.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
