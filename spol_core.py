
# Symbolic Process Orientated Language
# using extended ascii

### Syntax ###

##atom  ::= digit+ [. digit+]  // number [float or int]
##	| '"' character* '"' // String literal
##	| "£" [name] ("*" | "[" name ["," name]* "]") "{" statement* "}" [ "[" name* "]" ]   // Process Literal
##	| "[" expr ["," expr]* "]" // list
##
##
##nexpr ::= name ["$" name]*
##
##expr4 ::= atom
##	| nexpr
##	| "-" expr4
##	| "!" expr4
##	| "(" expr ")"
##
##expr3 ::= expr4 [("*" | "/") expr4]*
##expr2 ::= expr3 [("+" | "-")  expr3]*
##expr1 ::= expr2 [("==" | "!=" | ">=" | "<=" | ">" | "<") expr2]
##expr  ::= expr1 [("&&" | "||") expr1]*
##
##stExec ::= expr ["(" expr [ "," expr] * ")"]
##	 
##
##statement     ::= nexpr "=" expr
##		| "~" (stExec | "[" stExec ["," stExec]*"]")
##		| "print" expr
##		| expr "?" "{" statement* "}" ["{" statement* "}"] // if statement
##		| expr "%" "{" statement* "}" // while loop

##############

import sys,io,re,os
from enum import Enum
# support Data Structures/classes

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

  

class Dummy:
  def __init__(self,func=None):self.func=func
  def exec(self,env):return self.func()
  Engine = None

# Lexer

_l_rules = (
              ("name"   ,r"([a-zA-Z][a-zA-Z0-9]*)"),
              ("number" ,r"([0-9]+(?:\.[0-9]+)?)"),
              ("string" ,r"\"(.*?)\""),
              
              ("equal"  ,r"(\=\=)"),
              ("noeql"  ,r"(\!\=)"),
              ("grthn"  ,r"(\>)"),
              ("lsthn"  ,r"(\<)"),
              ("gtoeq"  ,r"(\>\=)"),
              ("ltoeq"  ,r"(\<\=)"),
              ("boand"  ,r"(\&\&)"),
              ("booor"  ,r"(\|\|)"),
              ("bonot"  ,r"(\!)"),
              
              ("plus"   ,r"(\+)"),
              ("minus"  ,r"(\-)"),
              ("aster"  ,r"(\*)"),
              ("doller" ,r"(\$)"),
              ("pound"  ,r"(\£)"),
              ("cents"  ,r"(\%)"),
              ("condit" ,r"(\?)"),
              ("colon"  ,r"(\:)"),
              ("fwslsh" ,r"(\/)"),
              
              ("oparen" ,r"(\()"),
              ("cparen" ,r"(\))"),
              ("obrack" ,r"(\{)"),
              ("cbrack" ,r"(\})"),
              ("osqrbr" ,r"(\[)"),
              ("csqrbr" ,r"(\])"),
              
              ("apos"   ,r"(\')"),
              ("invoke" ,r"(\!)"),
              ("process",r"(\~)"),
              ("assign" ,r"(\=)"),
              ("comma"  ,r"(\,)")
            )
_l_t=_l_types= Enum("l_types",tuple(i[0] for i in _l_rules))

class lToken:
  def __init__(self,ttype,lexeme):
    self.type,self.lexeme = ttype,lexeme
  def __repr__(self):
    return f"<{self.type} \"{self.lexeme}\">"
    
def _Lexer(text):
  out = []
  while text:
    if text[0] in " \t\n":
      text = text.lstrip()
      continue
    for rn,r in _l_rules:
      res = re.match(r,text)
      if res:
        text = text[res.span()[1]:]
        out.append(lToken(_l_t[rn],res.group(0)))
        break
    else:
      raise SyntaxError("Unrecognised syntax")
  return out


### Parser

# Defining Parser Classes [ the dataclasses the parse will built
class BiOp:
  def __init__(self,left,right):
    self.left,self.right = left,right
class Command:
  def exec(self,env):pass
class UnOp:pass

# deriving Binary Operator classes
class Add(BiOp):
  def get(self,env):
    return self.left.get(env) + self.right.get(env)

class Sub(BiOp):
  def get(self,env):
    return self.left.get(env) - self.right.get(env)

class Mul(BiOp):
  def get(self,env):
    return self.left.get(env) * self.right.get(env)

class Div(BiOp):
  def get(self,env):
    return self.left.get(env) / self.right.get(env)

class Ind(BiOp):
  def get(self,env):
    return self.left.get(env).__getitem__(self.right.get(env))
  def set(self,value,env):
    self.left.get(env).__setitem__(self.right.get(env),value)

class Equ(BiOp):
  def get(self,env):
    return self.left.get(env) == self.right.get(env)

class Neq(BiOp):
  def get(self,env):
    return self.left.get(env) != self.right.get(env)

class Grt(BiOp):
  def get(self,env):
    return self.left.get(env) >  self.right.get(env)

class Let(BiOp):
  def get(self,env):
    return self.left.get(env) <  self.right.get(env)

class Geq(BiOp):
  def get(self,env):
    return self.left.get(env) >= self.right.get(env)

class Leq(BiOp):
  def get(self,env):
    return self.left.get(env) <= self.right.get(env)

class Or(BiOp):
  def get(self,env):
    return self.left.get(env) or self.right.get(env)

class And(BiOp):
  def get(self,env):
    return self.left.get(env) and self.right.get(env)

# deriving Unary Operator classes
class Neg(UnOp):
  def __init__(self,child):
    self.child = child
  def get(self,env):
    return - self.child.get(env) 

class Not(UnOp):
  def __init__(self,child):
    self.child = child
  def get(self,env):
    return not self.child.get(env)

# Deriving Literal classes As Unary Operators
class Var(UnOp):
  def __init__(self,name):
    self.name = name
  def get(self,env):
    return env.get(self.name)
  def set(self,value,env):
    env.update({self.name:value.get(env)})

class Raw(UnOp):
  def __init__(self,val):
    self.value = val
  def get(self,env):
    return self.value

class List(UnOp):
  def __init__(self,exprs):
    self.exprs = exprs
  def get(self,env):
    return [i.get(env) for i in self.exprs]

class ProcessLiteral(UnOp,Command): # ooh
  def __init__(self,name,params,code,links):
    self.name,self.params = name,params
    self.code,self.links = code,tuple(links) if links != None else links

  def get(self,env):
    if self.params:
      return macroProcess(self.params,self.code,self.links)
    else:
      return Process(self.code,self.links)
  
  def exec(self,env):
    if self.name:
      env.update({self.name:self.get(env)})
    else:
      raise SyntaxError("Process Declaration Missing name")

# derived command classes
class Assign(Command):
  def __init__(self,target,value):
    self.target,self.value = target,value
  def exec(self,env):
    self.target.set(self.value,env)

class ExecuteSingle(Command):
  def __init__(self,target,params):
    self.target,self.params = target,params
  def exec(self,env):
    tmp = self.target.get(env)
    if isinstance(tmp,Process):
      if self.params:
        raise SyntaxError("Providing Parameters to Process That cannot take them")
      else:
        env.Engine.addsingle(tmp.instance(env))
    elif self.params == None:
      raise SyntaxError("MacroProcess Requires Parameter Values")
    else:
      env.Engine.addsingle(tmp.instance(self.params,BackRef(env,tmp.links)))

class ExecuteMany(Command):
  def __init__(self,procs):
    self.procs = procs

  def _instanceEach(self,env):
    out = []
    for p,a in self.procs:
      p = p.get(env)
      if isinstance(p,Process):
        if a:
          raise SyntaxError("Providing Parameters to Process That cannot take them")
        else:
          out.append(p.instance(BackRef(env,p.links)))
      elif a == None:
        raise SyntaxError("MacroProcess Requires Parameter Values")
      else:
        out.append(p.instance(a,BackRef(env,p.links)))
    return out

  def exec(self,env):
    env.Engine.addmany(self._instanceEach(env))
      
class Print(Command):
  def __init__(self,expr):
    self.expr = expr
  def exec(self,env):
    print(self.expr.get(env),file=sys.stderr)

class If(Command):
  def __init__(self,condition,body,orelse):
    self.cond,self.body = condition,body
    self.orelse = orelse

  def _load(self,item,env):
    er = env.Engine.current
    tmp = LSIE(Dummy,item,())
    tmp.env = er.env
    env.Engine.addsingle(tmp)

  def exec(self,env):
    if self.cond.get(env):
      self._load(self.body,env)
    elif self.orelse:
      self._load(self.orelse,env)

class While(Command):
  def __init__(self,sentinel,code):
    self.sent,self.code = sentinel,code

  def exec(self,env):
    er = env.Engine.current
    tmp = RLSIE(Dummy,self.code,(),self.sent)
    tmp.env = er.env
    env.Engine.addsingle(tmp)
    
    
  
# Base Dataclasses 
class Process:
  def __init__(self,code,links):
    self.code = code
    self.links = links if links else ()

  def instance(self,env):
    return LSIE(env,self.code,self.links)

class macroProcess:
  def __init__(self,params,code,links):
    self.params,self.code = params,code
    self.links = links if links else ()

  def instance(self,params,env):
    out = LSIE(env,self.code,self.links)
    out.update(zip(self.params,map(lambda x: x.get(env),params) ))
    return out

class LSIE:
  def __init__(self,penv,code,links):
    self.env = BackRef(penv,links)
    self.code = iter(code)
  def __next__(self):
    try:
      next(self.code).exec(self.env)
      return False
    except StopIteration:
      return True
  def update(self,E,**F):
    self.env.update(E,**F)

class RLSIE(LSIE):
  def __init__(self,penv,code,links,sentinel):
    self.env,self.code = BackRef(penv,links), code
    self.ccode = iter(())
    self.sent = sentinel
  def __next__(self):
    try:
      next(self.ccode).exec(self.env)
      return False
    except StopIteration:
      if self.sent.get(self.env):
        self.ccode = iter(self.code)
        try:
          next(self.ccode).exec(self.env)
        except StopIteration:
          pass
        finally:
          return False
      return True
      
class SSIE(LSIE):
  def __init__(self,penv,code):
    self.env = penv
    self.code = iter(code)
    

#################################################################################################################################
@lambda cls:cls()
class Parse:
  def __call__(self,text):
    global ___A_TOKS
    self.toks=toks= ___A_TOKS = _Lexer(text)
    out = []
    while toks:out.append(self._parse_statement())
    return out
    
  def _parse_statement(self):
    "parser a single statement"
    if self.toks[0].type is _l_t.process:
      self.toks.pop(0)
      if self.toks[0].type is _l_t.osqrbr:
        self.toks.pop(0)
        procs = []
        while self.toks[0].type is not _l_t.csqrbr:
          procs.append(self._parse_stExec())
          if self.toks.pop(0).type is not _l_t.comma:
            break
        return ExecuteMany(procs)
      else:
        return ExecuteSingle(*self._parse_stExec())
    elif self.toks[0].type is _l_t.pound:
      return self._parse_atom()
    
    else:
      if self.toks[0].type is _l_t.name:
        if self.toks[0].lexeme == "print":
          self.toks.pop(0)
          return Print(self._parse_expr())
    
      lval = self._parse_expr()
      if self.toks[0].type is _l_t.assign:
        self.toks.pop(0)
        return Assign(lval,self._parse_expr())
      if self.toks[0].type is _l_t.cents:
        self.toks.pop(0)
        return While(lval,self._parse_codbod())
      if self.toks[0].type is _l_t.condit:
        self.toks.pop(0)
        bod = self._parse_codbod()
        if self.toks and self.toks[0].type is _l_t.colon:
          self.toks.pop(0)
          orelse = self._parse_codbod()
        else:
          orelse = False
        return If(lval,bod,orelse)
        

  def _parse_atom(self): #parses the smallest parts of the language
    tmp = self.toks.pop(0)
    if   tmp.type is _l_t.number:
      return Raw(eval(tmp.lexeme))
    elif tmp.type is _l_t.string:
      return Raw(tmp.lexeme)
    elif tmp.type is _l_t.pound:
      # name
      if self.toks[0].type is _l_t.name:
        name = self.toks.pop(0).lexeme
      else :
        name = None
      #params
      if self.toks[0].type is _l_t.aster:
        self.toks.pop(0)
        params = None
      else:
        assert self.toks.pop(0).type is _l_t.osqrbr
        params = []
        while self.toks and self.toks[0].type is not _l_t.csqrbr:
          params.append(self.toks.pop(0).lexeme)
          if self.toks.pop(0).type is not _l_t.comma:
            break
      #code
      code = self._parse_codbod()
      #links
      if self.toks and self.toks[0].type is _l_t.osqrbr:
        links = []
        self.toks.pop()
        while self.toks[0].type is not _l_t.csqrbr:
          links.append(self.toks.pop(0).lexeme)
          if self.toks.pop(0).type is not _l_t.comma:
            break
      else:
        links = None
      return ProcessLiteral(name,params,code,links)

  def _parse_expr4(self):
    if   self.toks[0].type is _l_t.minus:
      self.toks.pop(0)
      return Neg(self._parse_expr4())
    elif self.toks[0].type is _l_t.bonot:
      self.toks.pop(0)
      return Not(self._parse_expr4())
    elif self.toks[0].type is _l_t.name:
      return self._parse_nexpr()
    elif self.toks[0].type is _l_t.oparen:
      self.toks.pop(0)
      tmp = self._parse_expr()
      assert self.toks.pop(0).type is _l_t.cparen
      return tmp
    else:
      return self._parse_atom()

  def _parse_expr3(self):
    res = self._parse_expr4()
    while self.toks and self.toks[0].type in (_l_t.aster,_l_t.fwslsh):
      res = Mul(res,self._parse_expr4()) \
                if self.toks.pop(0).type is _l_t.aster else\
            Div(res,self._parse_expr4())
    return res
  
  def _parse_expr2(self):
    res = self._parse_expr3()
    while self.toks and self.toks[0].type in (_l_t.plus,_l_t.minus):
      res = Add(res,self._parse_expr3()) \
                if self.toks.pop(0).type is _l_t.plus else\
            Sub(res,self._parse_expr3())
    return res

  def _parse_expr1(self):
    res = self._parse_expr2()
    if self.toks and self.toks[0].type in (_l_t.equal,_l_t.noeql,_l_t.grthn,
                                              _l_t.lsthn,_l_t.gtoeq,_l_t.ltoeq):
      res = [Equ,Neq,Grt,
             Let,Grt,Leq]\
             [(_l_t.equal,_l_t.noeql,_l_t.grthn,
               _l_t.lsthn,_l_t.gtoeq,_l_t.ltoeq).index(self.toks.pop(0).type)](res,self._parse_expr2())
    return res

  def _parse_expr(self):
    res = self._parse_expr1()
    while self.toks and self.toks[0].type in (_l_t.boand,_l_t.booor):
      res = And(res,self._parse_expr1()) \
                if self.toks.pop(0).type is _l_t.boand else\
            Or(res,self._parse_expr1())
    return res

  def _parse_nexpr(self):
    res = Var(self.toks.pop(0).lexeme)
    while self.toks and self.toks[0].type is _l_t.doller:
      self.toks.pop(0)
      res = Ind(res,Var(self.toks.pop(0).lexeme))
    return res

  def _parse_stExec(self):
    target = self._parse_expr()
    if self.toks and self.toks[0].type is _l_t.oparen:
      self.toks.pop(0)
      params = []
      while self.toks[0].type is not _l_t.cparen:
        params.append(self._parse_expr())
        if self.toks.pop(0).type is not _l_t.comma:
          break
    else:
      params = None
    return target,params

  def _parse_codbod(self):
    if self.toks[0].type is _l_t.obrack:
      self.toks.pop(0)
      out = []
      while self.toks[0].type is not _l_t.cbrack:
        out.append(self._parse_statement())
      assert self.toks.pop(0).type is _l_t.cbrack
      return out
    else:
      return [self._parse_statement()]
    
#################################################################################################################################
def tstExpr(text):
  Parse.toks = _Lexer(text)
  return Parse._parse_expr()

# execution model
class ExecNode:
  _host = None
  def __init__(self,ref,parent):
    self.ref,self._par = ref,parent
    self._children = []
    
  def __next__(self):
    self._host._bref = self
    if self._children:
      for i in self._children[:]:
        next(i)
    else:
      if next(self.ref):self._par.end(self)

  def end(self,child):
    self._children.remove(child)

  def append(self,item):
    self._children.append(ExecNode(item,self))
    
    
class Executor:
  def __init__(self):
    self._bref=None
    ExecNode._host = self

  def cycle(self):
    next(self._root)
    return bool(self._root)
    
  def Init(self,item):
    self._bref=self._root=ExecNode(item,self)
  
  def addsingle(self,item):
    self._bref.append(item)

  def addmany(self,items):
    for i in items:
      self._bref.append(i)

  def end(self,child):
    self._root = None
    
  @property
  def current(self):
    return self._bref.ref
        
   
if __name__ == "__main__":
  genv = type("SPOLGENV",(dict,),{"Engine":Executor()})()
  Engine = genv.Engine
  
  def run(text,env=genv,midfunc=lambda:None):
    tmp = SSIE(env,Parse(text))
    env.Engine.Init(tmp)
    while env.Engine.cycle():midfunc()
    del tmp

