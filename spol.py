import argparse as ap,sys,os
import smis

apar = ap.ArgumentParser("SPOL")

apar.add_argument("file",metavar="F",default=None,type=str,help="The file to be Interpreted")
#apar.add_argument("--help",dest="sph",action="store_const",const=False,default=True,help="Prints this help text")

if __name__ == "__main__":
  tmp = apar.parse_args()
  print(tmp.__dict__)
  if tmp.file:
    with open(tmp.file,"rb") as f:
      prog = f.read()
    smis.Run(prog.decode())
  else:
    apar.print_help()
