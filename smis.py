
# this is moreso to do some testing
from pem_parser import *
import math,re

@lambda x:x()
class SpolServiceEngine:
  def __init__(self):
    pass
  
  def IMPORT(self,name):
    # stuff to simplyfy this
    def _tst_bin(path):
      with open(path,"rb") as f:
        modtype = f.read(16).decode("utf8")
        modtype = re.match("(?:\/\*|\#)!spol\/(spol|pyth)(?:\*\/|#)",modtype)
      return modtype

    for path in self.__scan(name):
      if path.endswith(".py"):
        self.__load_py(path)
      elif path.endswith(".bin"):
        mode = _tst_bin(path)
        match mode.group(1):
          case "pyth":
            self.__load_py(path)
          case "spol":
            self.__load_spol(path)
          case _:
            self.Raise("Import Error")
      else:
        continue
      break
  def __scan(self,name):
    pathstack = [[r".\Lib"]]

    while pathstack:
      curpath = pathstack[-1].pop()
      if not pathstack[-1]:pathstack.pop()
      dirs,files = [],[]
      for p in os.listdir(curpath):
        fp = f"{curpath}\\{p}"
        if os.path.isdir(fp):
          dirs.append(fp)
        elif os.path.isfile(fp):
          if os.path.split(fp)[-1].startswith(name):
            yield fp
      if dirs: pathstack.append(dirs)
    return None

  def __load_py(self,path):
    with open(path,"rb")as f:
      prog = f.read().decode("utf8")
    venv = {"Engine":self,
            "SpolCompiler":lambda text:Compiler(Parser(text))}
    exec(prog,None,venv)
    self.env.update({k:venv.get(k) for k in venv.get("__all__",[])})
    for i in venv.get("__all__",[]):
      venv.pop(i)
    globals().update(venv)

  def __load_spol(self,path):
    with open(path,"rb") as f:
      prog = f.read().decode("utf8")
    try:
      code = Compiler(Parser(prog))
    except Exception as e:
      globals()["PREVIOUS_ERROR"] = e
      self.Raise(f"Error in Module {e}")
    else:
      self.Curnode.extend_single(code)
    
  def Raise(self,ref):
    if isinstance(ref,Exception):
      pass
    else:
      print(ref,file=sys.stderr)

  def SpolLink(self,function,args,cls=None):
    nargs = len(args)
    getter = b"".join([bytes([3,i,4]) for i in range(nargs)])
    doer = b"\x02\x00\x34" + bytes([nargs])
    return SpolCode(args,(function,),getter+doer + b"\x01",args)

  def method(self,cls,args,clsmethod=False):
    def wrap(func):
      tmp = self.SpolLink(func,args)
      try:cls.__setattr__(func.__name__,tmp)
      except TypeError:
        cls.__setattr__(cls,func.__name__,tmp)
      return func
    return wrap
    
genv = GlobEnv(SpolServiceEngine)
#Written As CodeObjects
genv["print"] = SpolCode(("expr",),(print,),b"\x03\x00\x04\x02\x00\x34\x01",("expr",))
def _dump(node):
  out = [f"{node._cref} :: {node.stack}"]
  if node.children:
    out.append(1)
    for i in node.children:
      out.extend(_dump(i))
    out.append(-1)
  return out
  
def dump(node,tw=4):
  out,cd = "",0
  for i in _dump(node):
    if isinstance(i,int):
      cd += i
    else:
      out += "\t"*cd + i + "\n"
  print(out.expandtabs(tw))

def Run(text):
  exe = ExtendExecutorNode(Compiler(Parser(text)),genv,genv)
  while next(exe):
    pass
  
def Runt(text):
  exe = ExtendExecutorNode(Compiler(Parser(text)),genv,genv)
  sn = 0
  while next(exe):
    print(f"\n== Step {sn} ==\n")
    dump(exe)
    sn += 1
