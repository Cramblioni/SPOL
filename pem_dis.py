
# pem_dis
from pem_parser import *
from copy import copy

def dis_single(iid,bit,cobj):
  out = f"{iid.value}\t"
  match iid:
    case opcode.stop:
      out += "stop"
    case opcode._load_const:
      out += "load_const\t"
      ci = next(bit)
      #print(">",ci)
      out += f"{ci}({cobj.consts[ci]})"
    case opcode._load_name:
      out += "load_name\t"
      ci = next(bit)
      #print(ci)
      out += f"{ci}({cobj.names[ci]})"
    case opcode._set_name: out+="set_name"
    case opcode._get_name: out+="get_name"
    case opcode._return:
      out += "return"
    #arith
    case opcode._add: out += "add"
    case opcode._sub: out += "sub"
    case opcode._mul: out += "mul"
    case opcode._div: out += "div"
    case opcode._neg: out += "neg"
    #comp
    case opcode._equ: out += "equ"
    case opcode._neq: out += "neq"
    case opcode._grt: out += "grt"
    case opcode._lst: out += "lst"
    case opcode._geq: out += "geq"
    case opcode._leq: out += "leq"
    #bool
    case opcode._and: out += "and"
    case opcode._or : out += "or"
    case opcode._not: out += "not"

    #flow
    case opcode._call:
      out += f"call\t{next(bit)}"
    case opcode._call_py:
      out += f"call_Python\t{next(bit)}"
    case opcode._call_many:
      out += f"call_many"
    case opcode._while:
      out += f"while"
    case opcode._if:
      out += f"if"
    #contianers
    case opcode._build_list:
      out += f"build_list\t{next(bit)}"

    
  #print(out)
  return out

def dis(cobj):
  out = []
  ci = iter(cobj) ; cobj.code_iter = [1]
  while [*copy(cobj.code_iter)]:
    iid = next(ci)
    try:
      out.append(dis_single(opcode(iid),cobj.code_iter,cobj))
    except RuntimeError:
      print([*copy(cobj.code_iter)])
      for c in cobj.consts:
          if isinstance(c,SpolCode):
            out.append("!")
            out.append(repr(c))
            out.append(dis(c))
      return "\n".join(out)
  for c in cobj.consts:
    if isinstance(c,SpolCode):
      out.append("")
      out.append(repr(c))
      out.append(dis(c))
  return "\n".join(out)
if __name__ == "__main__":
  tco = Compiler(Parser("""
£x[a]{z = 3}
~x(1)
~[x(1),
  x(2)]
"""))
  print(dis(tco))
