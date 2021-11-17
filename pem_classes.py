
# pem classes
## Opcode Enum
from enum import Enum
class opcode(Enum):
      stop = 0 #
      _return = 1 #
      _load_const = 2 #
      _load_name = 3 #
      _get_name = 4 #
      _set_name = 5 #
      _add = 16 #
      _sub = 17 # 
      _mul = 18 #
      _div = 19 #
      _neg = 20 #
      _and = 21 #
      _or = 22  # 
      _not = 23 #
      _equ = 32 #
      _neq = 33 #
      _grt = 34 #
      _lst = 35 #
      _geq = 36 #
      _leq = 37 #
      _if = 48  #
      _while = 49 #
      _call = 50 #
      _call_many = 51 #
      _call_py = 52 #
      _pop = 64  #
      _push = 65 #
      _set_item = 66 #
      _get_item = 67 #
      _build_list = 68 #
      _get_len = 69 #
      _get_attribute = 70 #
      _set_attribute = 71 
      _build_class = 72 #
      _instance = 73 #
      _distribute = 74#
      _import = 75
## Compiler Classes

class Name:
  def __init__(self,name):
    self.name = name
  def compile(self,compiler):
    _ = compiler.addName(self.name)
    compiler.Write([opcode._load_name.value,_])
    if compiler.isSet:
      compiler.Write([opcode._set_name.value])
    else:
      compiler.Write([opcode._get_name.value])
      
class Literal:
  def __init__(self,raw):
    self.raw = raw
  def compile(self,compiler):
    _ = compiler.addLiteral(self.raw)
    compiler.Write([opcode._load_const.value,_])

class List:
  def __init__(self,list):
    self.list = list
  def compile(self,compiler):
    _ = len(self.list) 
    for i in self.list:
      compiler.Compile(i)
    compiler.Write([opcode._build_list.value,_])

class StackOp:
  def __init__(self,target):
    self.target = target
  def compile(self,compiler):
    compiler.Compile(self.target)
    if compiler.isSet:
      compiler.Write([opcode._push.value])
    else:
      compiler.Write([opcode._pop.value])

class Index:
  def __init__(self,target,value):
    self.target = target
    self.value = value
  def compile(self,compiler):
    compiler.Compile(self.value)
    compiler.Compile(self.target)
    if compiler.isSet:
      compiler.Write([opcode._set_item.value])
    else:
      compiler.Write([opcode._get_item.value])

class LenOp:
  def __init__(self,target):
    self.target = target
  def compile(self,compiler):
    compiler.Compile(self.target)
    compiler.Compile(opcode._get_len)

class BiOp:
  def __init__(self,op,left,right):
    self.op = op
    self.left = left
    self.right = right
  def compile(self,compiler):
    compiler.Compile(self.right)
    compiler.Compile(self.left)
    compiler.Write([self.op.value])

class UnOp:
  def __init__(self,op,child):
    self.op = op
    self.child = child
  def compile(self,compiler):
    compiler.Compile(self.child)
    compiler.Write([self.op.value])

class Assign:
  def __init__(self,target,value):
    self.target = target
    self.value = value
  def compile(self,compiler):
    compiler.Compile(self.value)
    compiler.Compile(self.target,True)

class If:
  def __init__(self,cond,body,orelse):
    self.cond = cond
    self.body = body
    self.orelse = orelse
  def compile(self,compiler):
    compiler.new()
    if self.orelse:
          for i in self.orelse:
            compiler.Compile(i)
          _ = compiler.end(None,())
    else:
          _ = compiler.addLiteral(None)
    compiler.Write([opcode._load_const.value,_])
    compiler.new()
    for i in self.body:
      compiler.Compile(i)
    _ = compiler.end(None,())
    compiler.Write([opcode._load_const.value,_])
    compiler.Compile(self.cond)
    compiler.Write([opcode._if.value])

class While:
  def __init__(self,sentinel,body):
    self.sentinel = sentinel
    self.body = body
  def compile(self,compiler):
    compiler.new()
    for i in self.body:
      compiler.Compile(i)
    _ = compiler.end(None,())
    compiler.Write([opcode._load_const.value,_])
    compiler.new()
    compiler.Compile(self.sentinel)
    compiler.Write([opcode._return.value])
    _ = compiler.end(None,())
    compiler.Write([opcode._load_const.value,_,opcode._while.value])

class Process_Literal:
  def __init__(self,body,name,links,params):
    self.body = body
    self.name = name
    self.links = links
    self.params = params
  def compile(self,compiler):
    compiler.new()
    for i in self.body:
      compiler.Compile(i)
    _ = compiler.end(self.params,self.links,self.name)
    compiler.Write([opcode._load_const.value,_])
    # loading process metadata

class Attr:
  def __init__(self,target,name):
    self.target = target
    self.name = name
  def compile(self,compiler):
    _ = compiler.addName(self.name)
    compiler.Write([opcode._load_name.value,_])
    compiler.Compile(self.target)
    if compiler.isSet:
      compiler.Write([opcode._set_attribute.value])
    else:
      compiler.Write([opcode._get_attribute.value])

class Instance:
  def __init__(self,target,params):
    self.target = target
    self.params = params
  def compile(self,compiler):
    if self.params:
      for i in self.params:
        compiler.Compile(i)
    compiler.Compile(self.target)
    compiler.Write([opcode._instance.value,len(self.params or [])])
  
class Class_literal:
  def __init__(self,name,attributes,derives):
    self.name,self.attr,self.derv = name,attributes,derives
  def compile(self,compiler):  
    for name,value in self.attr:
      compiler.Compile(value)
      _ = compiler.addName(name)
      compiler.Write([opcode._load_name.value,_])

    _ = compiler.addLiteral(self.derv)
    compiler.Write([opcode._load_const.value,_])
      
    _ = compiler.addName(self.name)
    compiler.Write([opcode._load_name.value,_])
    
    compiler.Write([opcode._build_class.value,len(self.attr)])

    
  
class Return:
  def __init__(self,value):
    self.value = value
  def compile(self,compiler):
    compiler.Compile(self.value)
    compiler.Write([opcode._return.value])

class Invoke:
  def __init__(self,target,params):
    self.target = target
    self.params = params or []
  def compile(self,compiler):
    for i in self.params:
      compiler.Compile(i)
    compiler.Compile(self.target)
    compiler.Write([opcode._call.value,len(self.params)])

class Invoke_many:
  def __init__(self,targets,paramss):
    self.targets = targets
    self.paramss = paramss
  def compile(self,compiler):
    #target list
    for target in self.targets:
      compiler.Compile(target)
    compiler.Write([opcode._build_list.value,len(self.targets)])
    #param list
    for params in self.paramss:
      if params:
        for param in params:
          compiler.Compile(param)
        compiler.Write([opcode._build_list.value,len(params)])
      else:
        _ = compiler.addLiteral(None)
        compiler.Write([opcode._load_const.value,_])
    compiler.Write([opcode._build_list.value,len(self.paramss)])
      
    compiler.Write([opcode._call_many.value])
    
class PyInvoke:
  def __init__(self,target,params):
    self.target = target
    self.params = params
  def compile(self,compiler):
    for i in self.params:
      compiler.Compile(i)
    compiler.Compile(self.target)
    compiler.Write([opcode._call_py.value,len(self.params)])

class Distribute:
  def __init__(self,source,drain):
    self.source = source
    self.drain = drain
  def compile(self,compiler):
    compiler.Compile(self.drain)
    compiler.Compile(self.source)
    compiler.Write([opcode._distribute.value])

class Import:
  def __init__(self,name):
    self.name = name
  def compile(self,compiler):
    _ = compiler.addName(self.name)
    compiler.Write([opcode._load_name.value,_,
                    opcode._import.value])
      
## The Actual Compiler
@lambda x:x()    
class Compiler:
  def __call__(self,prog):
    self.__init__()
    self.BatchCompile(prog)
    return self.build(None,(),"SCRIPT")
  def __init__(self):
    self._stack = []
    self._literals = (None,)
    self._names = ()
    self._res = []
    self._sstack,self.isSet = [],False

  def addLiteral(self,val):
    if val not in self._literals:
      self._literals = (*self._literals,val)
    return self._literals.index(val)

  def addName(self,val):
    if val not in self._names:
      self._names = (*self._names,val)
    return self._names.index(val)

  def Compile(self,obj,isSet = False):
    self._sstack.append(self.isSet)
    self.isSet = isSet
    obj.compile(self)
    self.isSet = self._sstack.pop()

  def Drop(self):
    self._res.pop()

  def BatchCompile(self,stream):
    for i in stream:
      self.Compile(i)

  def Write(self,bytecode):
    self._res.extend(bytecode)

  def new(self):
    self._stack.append((
      self._literals,
      self._names,
      self._res))
    self._literals = (None,)
    self._names = ()
    self._res = []

  def end(self,params,links,name=None):
    data = self.build(params,links,name)
    self._literals,self._names,self._res =\
      self._stack.pop()
    return self.addLiteral(data)

  def build(self,params,links,name):
    return SpolCode(self._names,self._literals,bytearray(self._res),params,1,links,name)

## Execution Classes
class GlobEnv(dict):
  def __init__(self,engine):
    self.Engine = engine
    if engine:
          engine.env = self
    self.stack = []

class BackRef(dict):
  # Just Dict derived dataclass For Allowing Pass Through
  def __init__(self,glob,links):
    self.glob,self.links = glob,links
    self.Engine = glob.Engine
  def get(self,key,default=None):
    if key in self.links:
      return self.glob.get(key,default)
    return dict.get(self,key,self.glob.get(key,default))

  def __setitem__(self,key,value):
    if key in self.links:
      return self.glob.__setitem__(key,value)
    return dict.__setitem__(self,key,value)

  def update(self,E,**F):
    for k,v in E.items() if isinstance(E,dict) else E:
      self.__setitem__(k,v)
    for k,v in F.items():
      self.__setitem__(k,v)

class ClassRef(dict):
  def __init__(self,env,obj,cls):
    self.mapping = cls.__dict__
    self.Engine = env.Engine
    self.env,self.obj = env,obj

  def get(self,key,default=None):
    if key in self.mapping:
      return self.obj.__getattribute__(key)
    else:
      return self.env.get(key,dict.get(self,key,default))

  def __setitem__(self,key,value):
    if key in self.mapping:
      self.obj.__setattr__(key,value)
    else:
      dict.__setitem__(self,key,value)

  def update(self,E,**F):
    for k,v in E.items() if isinstance(E,dict) else E:
      self.__setitem__(k,v)
    for k,v in F.items():
      self.__setitem__(k,v)

    
class SpolCode:
  def __init__(self,names,consts,code,params=None,cwidth=1,links=(),name=None):
    self.names,self.consts = names,consts
    self.__cwidth,self.__links = cwidth,links
    self._params = params
    self.code = code
    self._isclassmethod = None
    self.name = name
  def __repr__(self):
    if self.name:return f"<{self.name} {len(self.code)}>"
    else:return f"<code {len(self.code)}>"

  def __iter__(self):
    def CODEITERATOR():
      self.code_iter=ci = iter(self.code)
      try:
        while True:
          tmp = [next(ci) for i in range(self.__cwidth)]
          yield sum(map(lambda x,y:x<<y*8,tmp,range(100)))

      except StopIteration as e:
        raise StopIteration from e
    return CODEITERATOR()

## For Marking
class SPOL_CLASS_TYPE:
  pass
