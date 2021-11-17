
## pem_parser
## SPOL(text) -> PEM(bytecode) parser
from pem import *
import re as _re

class lToken:
  def __init__(self,t,l):
    self.type,self.lexeme = t,l
  def __repr__(self):
    return f"<{self.type} {repr(self.lexeme)}>"
  
@lambda x:x()
class Lexer:
  def __call__(self,text):
    self.toks = []
    self._scan(text.lstrip())
    return self.toks

  def _scan(self,text):
    while text:
      # remove comments
      res = _re.match(self._comment,text,_re.DOTALL)
      if res:
        text = text[res.span()[1]:].lstrip()
        continue
      # extract token
      for rn,r in self.__rules:
        res = _re.match(r,text)
        if res:
          self.toks.append(lToken(self.types[rn],res.group(1)))
          text = text[res.span()[1]:].lstrip()
          break
      else:
        print("YEET")
      continue

Lexer._Lexer__rules = (
              ("name"   ,r"([a-zA-Z_][a-zA-Z_0-9]*)"),
              ("number" ,r"([0-9]+(?:\.[0-9]+)?)"),
              ("string" ,r"\"(.*?)\""),

              ("imprt",r"(\¬\<)"),
              ("ret" ,r"(\-\>)"),
              ("null",r"(\¬)"),
              
              ("equal"  ,r"(\=\=)"),
              ("noeql"  ,r"(\!\=)"),
              ("gtoeq"  ,r"(\>\=)"),
              ("ltoeq"  ,r"(\<\=)"),
              ("grthn"  ,r"(\>)"),
              ("lsthn"  ,r"(\<)"),
              ("boand"  ,r"(\&\&)"),
              ("booor"  ,r"(\|\|)"),
              ("bonot"  ,r"(\!)"),

              ("classi" ,r"(\£\£)"),
              ("attrib" ,r"(\.)"),
              ("instnc" ,r"(\~\~)"),
              
              ("plus"   ,r"(\+)"),
              ("minus"  ,r"(\-)"),
              ("aster"  ,r"(\*)"),
              ("doller" ,r"(\$)"),
              ("pound"  ,r"(\£)"),
              ("cents"  ,r"(\%)"),
              ("condit" ,r"(\?)"),
              ("colon"  ,r"(\:)"),
              ("fwslsh" ,r"(\/)"),
              ("acen"   ,r"(\^)"),
              ("hash"   ,r"(\#)"),
              
              ("oparen" ,r"(\()"),
              ("cparen" ,r"(\))"),
              ("obrack" ,r"(\{)"),
              ("cbrack" ,r"(\})"),
              ("osqrbr" ,r"(\[)"),
              ("csqrbr" ,r"(\])"),
              
              ("apos"   ,r"(\')"),
              ("process",r"(\~)"),
              ("assign" ,r"(\=)"),
              ("comma"  ,r"(\,)")
            )
l_t=Lexer.types = Enum("lTypes",tuple(i[0] for i in Lexer._Lexer__rules ))
Lexer._comment = r"\/\*.*?\*\/|\/\/.*?\n"

@lambda x:x()
class Parser:
  def __call__(self,text):
    global Atrack,Ahistory
    Atrack = self.toks = Lexer(text)
    Ahistory = Atrack[:]
    self.out=out = []
    while self.toks:
      out.append(self._parse_statement())
      #print(self.toks)
    return out

  def _parse_statement(self):
    # Check Header Statements
    match self.toks[0].type:
      case l_t.imprt:
        self.toks.pop(0)
        return Import(self.toks.pop(0).lexeme)
      case l_t.cents:
        self.toks.pop(0)
        tmp = self.out.pop()
        return While(tmp,self._parse_codbod())
      case l_t.classi:
        cls = self._parse_class()
        return Assign(Name(cls.name),cls)
      case l_t.pound:
        proc = self._parse_process()
        return Assign(Name(proc.name),proc)
      case l_t.process:
        self.toks.pop(0)
        if self.toks[0].type is l_t.osqrbr:
          sb,sp = [],[]
          self.toks.pop(0)
          while self.toks[0].type is not l_t.csqrbr:
            nb,np = self._parse_exec()
            sb.append(nb)
            sp.append(np)
            if self.toks.pop(0).type is not l_t.comma:
              break
          else:
            self.toks.pop(0)
          return Invoke_many(sb,sp)
        else:
          return Invoke(*self._parse_exec())
      case l_t.ret:
        self.toks.pop(0)
        return Return(self._parse_expr())
    # Non Header Statements
    init = self._parse_expr()
    if not self.toks:
      print("ERROR")
    else:
      match self.toks.pop(0).type:
        case l_t.assign:
          return Assign(init,self._parse_expr())
        case l_t.condit:
          self.toks.pop(0)
          body = self._parse_codbod()
          if self.toks[0].type is l_t.colon:
            self.toks.pop(0)
            orelse = self._parse_codbod()
          else:
            orelse = None
          return If(init,body,orelse)
        case l_t.cents:
          body = self._parse_codbod()
          return While(init,body)
        case l_t.null:
          # Distribute statement
          return Distribute(init,self._parse_atom())
          

  def _parse_expr(self):
    res = self._parse_expr1()
    while self.toks and self.toks[0].type in (l_t.boand,l_t.booor):
      if self.toks.pop(0).type is l_t.boand:
        res = BiOp(opcode._and,res,self._parse_expr1())
      else:
        res = BiOp(opcode._or,res,self._parse_expr1())
    return res

  def _parse_expr1(self):
    res = self._parse_expr2()
    if self.toks and self.toks[0].type in (l_t.equal,l_t.noeql,l_t.grthn,
                                           l_t.lsthn,l_t.gtoeq,l_t.ltoeq):
      op = (opcode._equ,opcode._neq,opcode._grt,
            opcode._lst,opcode._geq,opcode._leq)[(l_t.equal,l_t.noeql,l_t.grthn,
               l_t.lsthn,l_t.gtoeq,l_t.ltoeq).index(self.toks.pop(0).type)]
      res = BiOp(op,res,self._parse_expr2())
    return res

  def _parse_expr2(self):
    res = self._parse_expr3()
    while self.toks and self.toks[0].type in (l_t.plus,l_t.minus):
      if self.toks.pop(0).type is l_t.plus:
        res = BiOp(opcode._add,res,self._parse_expr3())
      else:
        res = BiOp(opcode._sub,res,self._parse_expr3())
    return res

  def _parse_expr3(self):
    res = self._parse_expr4()
    while self.toks and self.toks[0].type in (l_t.aster,l_t.fwslsh):
      if self.toks.pop(0).type is l_t.aster:
        res = BiOp(opcode._mul,res,self._parse_expr4())
      else:
        res = BiOp(opcode._div,res,self._parse_expr4())
    return res

  def _parse_expr4(self):
    if   self.toks[0].type is l_t.minus:
      self.toks.pop(0)
      return Neg(self._parse_expr4())
    elif self.toks[0].type is l_t.bonot:
      self.toks.pop(0)
      return Not(self._parse_expr4())
    elif self.toks[0].type is l_t.name:
      return self._parse_nexpr()
    elif self.toks[0].type is l_t.oparen:
      self.toks.pop(0)
      tmp = self._parse_expr()
      
      assert self.toks.pop(0).type is l_t.cparen
      return tmp
    elif self.toks[0].type is l_t.acen:
      self.toks.pop(0)
      return StackOp(self._parse_expr4())
    elif self.toks[0].type is l_t.hash:
      self.toks.pop(0)
      return LenOp(self._parse_expr4())
    else:
      return self._parse_atom()
  
  def _parse_nexpr(self):
    res = Name(self.toks.pop(0).lexeme)
    while self.toks and self.toks[0].type is l_t.doller:
      self.toks.pop(0)
      res = Index(res,self._parse_expr4())
    while self.toks and self.toks[0].type is l_t.attrib:
      self.toks.pop(0)
      res = Attr(res,self.toks.pop(0).lexeme)
    return res

  def _parse_atom(self): #parses the smallest parts of the language
    tmp = self.toks.pop(0)
    if   tmp.type is l_t.number:
      return Literal(eval(tmp.lexeme))
    elif tmp.type is l_t.string:
      return Literal(eval( "\"" + tmp.lexeme + '"'))
    elif tmp.type is l_t.osqrbr:
      if self.toks[0].type is l_t.csqrbr:
        self.toks.pop(0)
        return List([])
      
      expr = []
      while self.toks:
        expr.append(self._parse_expr())
        if self.toks.pop(0).type is not l_t.comma:
          break
      return List(expr)
    elif tmp.type is l_t.pound:
      return self._parse_process(False)
    elif tmp.type is l_t.process:
      return Invoke(*self._parse_exec())
    elif tmp.type is l_t.instnc:
      return self._parse_instance()
    elif tmp.type is l_t.null:
      return Literal(None)

  def _parse_codbod(self):
    prevb = self.out
    if self.toks[0].type is l_t.obrack:
      self.toks.pop(0)
      self.out=out = []
      while self.toks[0].type is not l_t.cbrack:
        out.append(self._parse_statement())
      else:
        self.toks.pop(0)
      self.out = prevb
      return out
    else:
      return [self._parse_statement()]

  def _parse_process(self,psp=True):
    if psp:assert self.toks.pop(0).type is l_t.pound
    
    if self.toks[0].type is l_t.name:
      name = self.toks.pop(0).lexeme
    else:
      name = None

    if self.toks[0].type is l_t.aster:
      self.toks.pop(0)
      params = None
    else:
      assert self.toks.pop(0).type is l_t.osqrbr
      params = []
      while self.toks and self.toks[0].type is not l_t.csqrbr:
        params.append(self.toks.pop(0).lexeme)
        if self.toks.pop(0).type is not l_t.comma:
          break
    code = self._parse_codbod()

    if self.toks and self.toks[0].type is l_t.osqrbr:
      links = []
      self.toks.pop(0)
      while self.toks[0].type is not l_t.csqrbr:
        links.append(self.toks.pop(0).lexeme)
        if self.toks.pop(0).type is not l_t.comma:
          break
      else:
        self.toks.pop(0)
        
    else:
      links = ()
    return Process_Literal(code,name,links,params)

  def _parse_exec(self):
    target = self._parse_expr()
    if self.toks and self.toks[0].type is l_t.oparen:
      self.toks.pop(0)
      params = []
      while self.toks[0].type is not l_t.cparen:
        params.append(self._parse_expr())
        if self.toks.pop(0).type is not l_t.comma:
          break
      else:
        self.toks.pop(0)
    else:
      params = None
    return target,params

  def _parse_instance(self):
    target = self._parse_expr()
    if self.toks and self.toks[0].type is l_t.oparen:
      self.toks.pop(0)
      params = []
      while self.toks[0].type is not l_t.cparen:
        params.append(self._parse_expr())
        if self.toks.pop(0).type is not l_t.comma:
          break
      else:
        self.toks.pop(0)
    else:
      params = None
    return Instance(target,params)
  
  def _parse_class(self):
    self.toks.pop(0)
    cname = self.toks.pop(0).lexeme
    assert self.toks.pop(0).type is l_t.obrack
    attr = []
    while self.toks[0].type is not l_t.cbrack:
      match self.toks[0].type:
        case l_t.name:
          name = self.toks.pop(0).lexeme
          if self.toks[0].type is l_t.assign:
            self.toks.pop(0)
            initial = self._parse_expr()
          else:
            initial = Literal(None)
          attr.append((name,initial))
        case l_t.pound:
          tmp = self._parse_process()
          attr.append((tmp.name,tmp))
    else:
      self.toks.pop(0)

    derv = []
    if self.toks and self.toks[0].type is l_t.osqrbr:
      self.toks.pop(0)
      while self.toks[0].type is not l_t.csqrbr:
        derv.append(self.toks.pop(0).lexeme)
        if self.toks.pop(0).type is not l_t.comma:
          break
      else:
        self.toks.pop(0)
    tmp = Class_literal(cname,attr,derv)
    return tmp

###########
if __name__ == "__main__":
  from pem_dis import dis
  prntproc = SpolCode(("print !","expr"),(None),b"\x03\x01\x04\x03\x00\x04\x34\x01",("expr",))
  defprnt  = SpolCode(("print !","print"),(print,prntproc),b"\x02\x00\x03\x00\x05\x02\x01\x03\x01\x05")
  setup_exec = ExtendExecutorNode(defprnt,genv,None)
  while next(setup_exec):
    pass
  pout = Parser("""
  £exp[a,b]{
    c = 1
    ~£*{b = b - 1 -> b >= 0}[b] %
    { c = c * a }
    ~print(c)
    -> c
  }
  ~[exp(2,5),
    exp(2,3),
    exp(2,1)]
  ~print(" :) ")
  """)
  co = Compiler(pout)
  print(dis(co))
  print()
  exe = ExtendExecutorNode(co,genv,None)
  while next(exe):
    pass
    #print(exe.stack)
    #print(exe.children)
