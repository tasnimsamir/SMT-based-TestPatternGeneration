from ATPG import *
from Circuit import Circuit
from Parser import Parser

DIRECTORY = "./bench_files"

def test(fileName, Stuck_fault, fault_gate, inputIndex = None, useOutNode = None):
    print("=================================test of {} Circuit==============================".format(fileName.split(".")[0]))
    c = Circuit()
    p = Parser(c, os.path.join(DIRECTORY, fileName))
    p.parse()
    atpg = ATPG(c)
    atpg.addFault(Stuck_fault, fault_gate, inputIndex, useOutNode)
    atpg.solve()
    atpg.print()
#
test('simple_test.bench', Circuit.STUCK_AT_1_FAULT, 'f') #Not satisfiable
test('c17.bench', Circuit.STUCK_AT_1_FAULT, 'G11gat')
test('c17.bench', Circuit.STUCK_AT_0_FAULT, 'G22gat', inputIndex=1)
test('c432.bench', Circuit.STUCK_AT_1_FAULT, 'G360gat')
test('c1355.bench', Circuit.STUCK_AT_0_FAULT, 'G996gat', inputIndex=4)
test('c7552.bench', Circuit.STUCK_AT_1_FAULT, 'G550')
test('c6288.bench', Circuit.STUCK_AT_0_FAULT, 'G545gat')