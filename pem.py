
# New SPOL EXECUTOR MODEL BOII
from pem_classes import *
import gc,sys,os
from copy import copy
gc.enable()
Commands = opcode

class BaseExecutorNode:
  def __init__(self,codeobj,penv,parent):
    #print(codeobj,codeobj.consts)
    codeobj = copy(codeobj)
    self.code,self._cref = iter(codeobj),codeobj
    self.env = BackRef(penv,codeobj._SpolCode__links)
    self.stack = []
    self.children,self.parent = [],parent

  def add_single(self,cobj,args):
    if isinstance(cobj,SpolCode):
      if cobj._isclassmethod:
        instnc = ClassExecutorNode(cobj,self.env,self,cobj._isclassmethod)
      else:
        instnc = BaseExecutorNode(cobj,self.env,self)
      self.children.append(instnc)
      if args and cobj._params:
        instnc.env.update(zip(cobj._params,args))
    elif isinstance(cobj,(int,float)):
      raise SyntaxError("Resolve to int")
    else:
      self.children.append(cobj)

  def extend_single(self,cobj):
    instnc = ExtendExecutorNode(cobj,self.env,self)
    self.children.append(instnc)
    
  def drop_single(self,inst):
    if inst.stack:
      self.stack.append(inst.stack.pop())
    self.children.remove(inst)
  
  def Cycle(self):
##    try:print(self._cref,[*copy(self._cref.code_iter)])
##    except AttributeError:pass
    try:
      comm = Commands(next(self.code))
    except StopIteration:
      return False
    #print(comm)
    #print(self._cref,comm,self.stack,self.env)
    match comm:
      ## Control
      case Commands.stop:
        if self.parent:
          self.parent.drop_single(self)
          return False
      case Commands._load_name:
##        print(self._cref,comm,[*copy(self._cref.code_iter)])
        tmp = next(self._cref.code_iter)
##        print("name",tmp,self._cref.names,self._cref)
        self.stack.append(self._cref.names[tmp])
      case Commands._get_name:
        sname = self.stack.pop()
        self.stack.append(self.env.get(sname,self.env.get(sname)))
      case Commands._set_name:
        self.env.update({self.stack.pop():self.stack.pop()})
      case Commands._load_const:
        tmp = next(self._cref.code_iter)
        #print("consts",tmp,self._cref.consts,self._cref)
        self.stack.append(self._cref.consts[tmp])
      case Commands._return:
        if self.parent:
          self.parent.stack.append(self.stack.pop())
        return False
      case Commands._pop:
        self.stack.append(self.stack.pop().pop())
      case Commands._push:
        self.stack.pop().append(self.stack.pop())
      case Commands._get_item:
        self.stack.append(self.stack.pop()[self.stack.pop()])
      case Commands._set_item:
        self.stack.pop().__setitem__(self.stack.pop(),self.stack.pop())
      case Commands._import:
        self.env.Engine.IMPORT(self.stack.pop())
              
      ## Arithmatic
      case Commands._add:
        a,b = self.stack.pop(), self.stack.pop()
        #print(a,b)
        if isinstance(a,SPOL_CLASS_TYPE) and "__add__" in a.__class__.__dict__:
          proc = a.__add__
          self.add_single(proc,(b,))
        elif isinstance(b,SPOL_CLASS_TYPE) and "__radd__" in b.__class__.__dict__:
          proc = b.__radd__
          self.add_single(proc,(a,))
        else:
          self.stack.append(a+b)
      case Commands._sub:
        a,b = self.stack.pop(), self.stack.pop()
        #print(a,b)
        if isinstance(a,SPOL_CLASS_TYPE) and "__sub__" in a.__class__.__dict__:
          proc = a.__sub__
          self.add_single(proc,(b,))
        elif isinstance(b,SPOL_CLASS_TYPE) and "__rsub__" in b.__class__.__dict__:
          proc = b.__rsub__
          self.add_single(proc,(a,))
        else:
          self.stack.append(a-b)
      case Commands._mul:
        a,b = self.stack.pop(), self.stack.pop()
        #print(a,b)
        if isinstance(a,SPOL_CLASS_TYPE) and "__mul__" in a.__class__.__dict__:
          proc = a.__mul__
          self.add_single(proc,(b,))
        elif isinstance(b,SPOL_CLASS_TYPE) and "__rmul__" in b.__class__.__dict__:
          proc = b.__rmul__
          self.add_single(proc,(a,))
        else:
          self.stack.append(a*b)
      case Commands._div:
        a,b = self.stack.pop(), self.stack.pop()
        #print(a,b)
        if isinstance(a,SPOL_CLASS_TYPE) and "__div__" in a.__class__.__dict__:
          proc = a.__div__
          self.add_single(proc,(b,))
        elif isinstance(b,SPOL_CLASS_TYPE) and "__rdiv__" in b.__class__.__dict__:
          proc = b.__rdiv__
          self.add_single(proc,(a,))
        else:
          self.stack.append(a/b)
      case Commands._neg:
        a = self.stack.pop()
        if isinstance(a,SPOL_CLASS_TYPE) and "__neg__" in a.__dict__:
          proc = a.__neg__
          node = ClassExecutorNode(proc,self.env,self,a)
          self.addsingle(node,())
        else:
          self.stack.append(-a)

      ## Logic
      case Commands._and:
        self.stack.append(self.stack.pop() and self.stack.pop())
      case Commands._not:
        self.stack.append(not self.stack.pop())
      case Commands._or :
        self.stack.append(self.stack.pop() or  self.stack.pop())

      ## Comparisons
      case Commands._equ:
        self.stack.append(self.stack.pop() == self.stack.pop())
      case Commands._neq:
        self.stack.append(self.stack.pop() != self.stack.pop())
      case Commands._grt:
        self.stack.append(self.stack.pop() >  self.stack.pop())
      case Commands._lst:
        self.stack.append(self.stack.pop() <  self.stack.pop())
      case Commands._geq:
        self.stack.append(self.stack.pop() >= self.stack.pop())
      case Commands._leq:
        self.stack.append(self.stack.pop() <= self.stack.pop())
        
      ## Flow
      case Commands._call:
        noa = next(self._cref.code_iter)
        cobj = self.stack.pop()
        args,self.stack = self.stack[-noa:],self.stack[:-noa]
        self.add_single(cobj,args)

      case Commands._call_many:
        pars,tars = self.stack.pop(),self.stack.pop()
        for cobj,args in zip(tars,pars):
          self.add_single(cobj,args)
          

      case Commands._call_py:
        noa = next(self._cref.code_iter)
        targ = self.stack.pop()
        args,self.stack = self.stack[-noa:], self.stack[:-noa]
        self.stack.append(targ(*args))

      case Commands._if:
        if self.stack.pop():
          self.extend_single(self.stack.pop())
          self.stack.pop()
        else:
          self.stack.pop()
          tmp = self.stack.pop()
          if tmp:
            self.extend_single(tmp)
      case Commands._while:
        s,b = self.stack.pop(),self.stack.pop()
        tmp = RepeatedExecutorNode(b,self.env,self,s)
        self.children.append(tmp)
      case Commands._distribute:
        source,drain = self.stack.pop(),self.stack.pop()
        if isinstance(source,list):
          for i in source:
            self.add_single(drain,(i,))
        else:
          self.add_single(drain,(source,))

      ## Container
      case Commands._build_list:
        noi = next(self._cref.code_iter)
        new,self.stack = self.stack[-noi:], self.stack[:-noi]
        self.stack.append(new)
      case Commands._build_class:
        noa = next(self._cref.code_iter)
        name = self.stack.pop()
        derv = self.stack.pop()
        attr = {self.stack.pop():self.stack.pop() for i in range(noa)}
        try:
          tmp = attr.pop("__init__")
        except KeyError:
          tmp = SpolCode((),(),b"",())
        attr["__spol__init__"] = tmp
        nclass = type(name,(*(self.env.get(i) for i in derv),SPOL_CLASS_TYPE),attr)
        self.stack.append(nclass)
          

      ## Misc
      case Commands._get_len:
        self.stack.append(len(self.stack.pop()))
      case Commands._get_attribute:
        self.stack.append(self.stack.pop().__getattribute__(self.stack.pop()))
      case Commands._set_attribute:
        self.stack.pop().__setattr__(self.stack.pop(),self.stack.pop())
      case Commands._instance:
        noa = next(self._cref.code_iter)
        cls = self.stack.pop()
        args,self.stack = self.stack[:noa],self.stack[noa:]
        inst = cls()
        for i in dir(inst):
          if isinstance(inst.__getattribute__(i),SpolCode):
            inst.__getattribute__(i)._isclassmethod = inst
        self.add_single(inst.__spol__init__,args)
        self.stack.append(inst)
      
    return True

  def __next__(self):
    self.env.Engine.Curnode = self
    if self.children:
      for c in self.children[:]:
        if not next(c):
          self.drop_single(c)
      return True
    else:
      try:
        return bool(self.Cycle())
      except RuntimeError:
        return False


#Other node types
class ExtendExecutorNode(BaseExecutorNode):
  def __init__(self,codeobj,penv,parent):
    #print(codeobj,codeobj.consts)
    codeobj = copy(codeobj)
    self.code,self._cref = iter(codeobj),codeobj
    self.env = penv
    self.stack = []
    self.children,self.parent = [],parent

class RepeatedExecutorNode(BaseExecutorNode):
  def __init__(self,codeobj,penv,parent,sentinel):
    #print(codeobj,codeobj.consts)
    codeobj = copy(codeobj)
    self._body = codeobj
    self.env = penv
    self.stack = []
    self.children,self.parent = [],parent
    self._sentinel = copy(sentinel)
    self.code,self._cref = iter(self._sentinel),self._sentinel

  def Cycle(self):
    tmp = BaseExecutorNode.Cycle(self)
    if not tmp:
      #print("Swapping")
      if self._cref is self._body:
        self.code,self._cref = iter(self._sentinel),self._sentinel
        return True
      else:
        #print(self.parent.stack)
        if self.parent.stack.pop():
          self.code,self._cref = iter(self._body),self._body
          return True
        else:
          return False
    else:
      return True
      
  def __next__(self):
    if self.children:
      for c in self.children[:]:
        if not next(c):
          self.drop_single(c)
        return True
    else:
      try:
        return bool(self.Cycle())
      except RuntimeError:
        return True  

class ClassExecutorNode(BaseExecutorNode):
  def __init__(self,codeobj,env,parent,cls):
    codeobj = copy(codeobj)
    self.code,self._cref = iter(codeobj),codeobj
    self.env = ClassRef(env,cls,cls.__class__)
    self.stack = []
    self.children,self.parent = [],parent
    

genv = GlobEnv(None)
if __name__ == "__main__":
  program = [Assign(Name("print"),Literal(print)),
             Assign(Name("x"),Literal(0)),
             While(BiOp(opcode._leq,Name("x"),Literal(10)),
                   [PyInvoke(Name("print"),(Name("x"),)),
                    Assign(Name("x"),BiOp(opcode._add,Name("x"),Literal(1)))
                    ])
            ]
  ## /* Test of */
  ## x = 5
  ## £exp*{
  ##  x = 5 + x
  ##  ~print(x)
  ##}
  ##~exp
  ##~print(x)
  ## /* should output
  ##  10
  ##  5
  ##  */
  pcobj = Compiler(program)

  exe = BaseExecutorNode(pcobj,genv,None)

  while (prev:=next(exe)):
    pass
    #print("\t",exe.stack)
    #print("\t",exe.env)
    
    

