from DTPG import *
from Parser import Parser

DIRECTORY = "./bench_files"

def test(fileName, faultPair, faultLocation, inputIndex = None, useOutNode = None):
    c = Circuit()
    p = Parser(c, os.path.join(DIRECTORY, fileName))
    p.parse()
    dtpg = DTPG(c)
    dtpg.addPairFaults(faultPair, faultLocation, inputIndex, useOutNode)
    dtpg.solve()
    dtpg.print()
    dtpg.removePairFaults()

test(fileName= 'c17.bench', faultPair = (Circuit.STUCK_AT_1_FAULT , Circuit.STUCK_AT_0_FAULT), faultLocation = ('G22gat' , 'G11gat'), inputIndex= (0 , 1))
