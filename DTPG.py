from z3 import *
from Circuit import *
from DTPGCircuit import *
from GateConstraintVisitor import *
"""
Class that generates an input for a given fault and circuit, 
using the SMT solver z3
"""

class DTPG(object):
    def __init__(self, circuit: Circuit):
        self.s = Solver()
        self.s.set("sat.pb.solver", "solver")
        self.vars = {} # Map with all variables of SMT solves

        self.circuit = DTPGCircuit(copy.deepcopy(circuit), copy.deepcopy(circuit),copy.deepcopy(circuit))
        self.declareVars()
        self.setInputConstraints()
        self.setGateConstraints()
        self.setOutputConstraint()

    def declareVars(self):
        for gate in self.circuit.getGates():
            var_name = gate.output.__str__()
            self.vars[var_name] = Bool(var_name)
            for inputNode in gate.inputs:
                var_name = inputNode.__str__()
                self.vars[var_name] = Bool(var_name)
        for inNode in self.circuit.getInNodes():
            var_name = inNode.__str__()
            self.vars[var_name] = Bool(var_name)
        for inNodeName, inNode in self.circuit.faultyInNodes.items():
            var_name = inNode.__str__()
            self.vars[var_name] = Bool(var_name)
        for outNode in self.circuit.getOutNodes():
            var_name = outNode.__str__()
            self.vars[var_name] = Bool(var_name)

        self.vars[Circuit.STUCK_AT_1_FAULT.__str__()] = Bool(Circuit.STUCK_AT_1_FAULT.__str__())
        self.s.add(self.vars[Circuit.STUCK_AT_1_FAULT.__str__()] == True)
        self.vars[Circuit.STUCK_AT_0_FAULT.__str__()] = Bool(Circuit.STUCK_AT_0_FAULT.__str__())
        self.s.add(self.vars[Circuit.STUCK_AT_0_FAULT.__str__()] == False)

    def setEdgeConstraints(self):
        for e in self.circuit.edges:
            inNode = e.inNode
            outNode = e.outNode
            self.s.add(self.vars[inNode.__str__()] == self.vars[outNode.__str__()])

    def setGateConstraints(self):
        visitor = GateConstraintVisitor(self.s, self.vars)
        for gate in self.circuit.getGates():
            gate.accept(visitor)

    def setInputConstraints(self):
        for inNodeName in self.circuit.inNodes:
            faulty1InNodeName = self.circuit.getFaulty1SignalName(inNodeName)
            faulty2InNodeName = self.circuit.getFaulty2SignalName(inNodeName)
            self.s.add((self.vars[inNodeName] == self.vars[faulty1InNodeName]) and (self.vars[inNodeName]  == self.vars[faulty2InNodeName]))

    def setOutputConstraint(self):
        assert(len(self.circuit.getOutNodeNames()) == 1)
        outNodeName = list(self.circuit.getOutNodeNames())[0]
        outNode = self.circuit.getOutNode(outNodeName)
        self.s.add(True == self.vars[outNode.__str__()])

    def solve(self):
        self.s.check()

            
    def print(self, printAllSignals = False):
        pattern = {}
        if self.s.check() == sat:
            m = self.s.model()
            for inNodeName in self.circuit.getInNodeNames():
                var = self.vars[inNodeName]
                pattern[inNodeName] = 1 if m[var] == True else 0
                print('{0!s:<5s}: {1!s:<5s}'.format(inNodeName, ("1" if is_true(m[var]) else "0")))

            print("Diagnostic Test Pattern: {}".format(list(pattern.values())))
            if printAllSignals:
                print("gate values: faulty1 | faulty2")
                for gateName in self.circuit.originalGates:
                    faulty1Gatename = self.circuit.getFaulty1SignalName(gateName)
                    faulty2Gatename = self.circuit.getFaulty2SignalName(gateName)
                    if (faulty1Gatename in self.circuit.gates) and (faulty2Gatename in self.circuit.gates): # filter faulty gates
                        faultyGate1 = self.circuit.gates[faulty1Gatename]
                        varFaulty1 = self.vars[faultyGate1.output.__str__()]

                        faultyGate2 = self.circuit.gates[faulty2Gatename]
                        varFaulty2 = self.vars[faultyGate2.output.__str__()]

                        print('{0}: {1!s:<5s} | {2!s:<5s}'.format(gateName, m[varFaulty1], m[varFaulty2]))

                        for (i, (faulty1InputNode, faulty2InputNode)) in enumerate(zip(faultyGate1.inputs, faultyGate2.inputs)):
                            varFaulty1 = self.vars[faulty1InputNode.__str__()]
                            varFaulty2 = self.vars[faulty2InputNode.__str__()]
                            print('\t{0}: {1!s:<5s} | {2!s:<5s}'.format(i, m[varFaulty1], m[varFaulty2]))
        else:
            print('The given fault cannot be detected')

    def addPairFaults(self, fault, signalName, inputIndex = None, useOutNode = None):
        self.s.push()
        self.circuit.addPairFaults(fault, signalName, inputIndex=inputIndex, useOutNode=useOutNode)
        self.setEdgeConstraints()

    def removePairFaults(self):
        self.s.pop()
        self.circuit.removePairFaults()
