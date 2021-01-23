from Circuit import *
from Node import *

class DTPGCircuit(Circuit):
    """
    Representation of a circuit that can be used for generating input assignments
    to test for stuck at 1 or 0 faults. 
    """
    FAULT2_SUFFIX = '_f2'
    FAULT1_SUFFIX = '_f1'

    def __init__(self, faultfree : Circuit , faulty1: Circuit, faulty2: Circuit):
        """
        The constructor takes two circuits that need to have the same input and output nodes. 
        These two circuits are merged into one and the output nodes are replaced with a miter structure.
        The input circuits must not be used afterwards.
        """
        self.inNodes = faultfree.inNodes
        self.faultyInNodes = {}
        self.outNodes = faultfree.outNodes
        self.originalGates = faultfree.gates
        self.gates = {}
        self.edges = []
        self.generateMiter(faulty1 , faulty2)

    def generateMiter(self, faulty1 , faulty2):
        """
        Take another circuit _faulty_ that has the same input and output nodes as _self_
        and modify _self_ such that _self_ contains both circuits and connects their outputs
        via a miter structure. _self_ will have a new output which is the output of the
        miter structure
        """
        # 1. merge gates, edges and outNodes of faulty circuit into orignal circuit
        # copy gates
        for gate in faulty1.gates.values():
            gate.name = self.getFaulty1SignalName(gate.name)
            self.gates[gate.name] = gate

        # copy edges
        for e in faulty1.edges:
            self.edges.append(e)

        # copy inNodes
        for inNode in faulty1.inNodes.values():
            inNode.name = self.getFaulty1SignalName(inNode.name)
            self.faultyInNodes[inNode.name] = inNode

        # copy gates
        for gate in faulty2.gates.values():
            gate.name = self.getFaulty2SignalName(gate.name)
            self.gates[gate.name] = gate

        # copy edges
        for e in faulty2.edges:
            self.edges.append(e)

        # copy inNodes
        for inNode in faulty2.inNodes.values():
            inNode.name = self.getFaulty2SignalName(inNode.name)
            self.faultyInNodes[inNode.name] = inNode


        # 2. add miter structure; replace outNodes with XOR gates, add final Or gate and add 1 outNode
        ctr = 0 #number of output signals
        xor_gates = []
        for (outName, outNode) in self.outNodes.items():
            outNodeFaulty1 = faulty1.getOutNode(outName)
            outNodeFaulty2 = faulty2.getOutNode(outName)

            #adding XoR gate
            xor_name = "miter_XOR_%d" % ctr
            self.addGate(xor_name, 'xor', 2)
            xor_gates.append(self.gates[xor_name])
            xor_gate = self.gates[xor_name]
            ctr += 1

            # reconnect the predecessor of OutNode to the XOR gate
            e = outNodeFaulty1.inEdge
            e.disconnectOutput()
            xor_gate.connectInput(e, 0)
 
            # do same for faulty circuit
            e = outNodeFaulty2.inEdge # use edge to get predecessor instead of looking into gates/inNodes
            e.disconnectOutput()
            xor_gate.connectInput(e, 1)             

        self.outNodes = {}

        # generate final OR and connect XORs to it
        miter_or_name = "miter_OR"
        self.addGate(miter_or_name, 'or', ctr)
        assert(len(xor_gates) == ctr)
        for (ctr, gate) in enumerate(xor_gates):
            self.connectGate(gate.name, miter_or_name, ctr)
        
        self.addOutNode(miter_or_name)
        self.connectOutput(miter_or_name)

    def getFaulty1SignalName(self, signalName):
        """
        Return corresponding faulty signal name of the given signal.
        Assumes that generateMiter has been called before, otherwise this function is not useful
        """
        return signalName + DTPGCircuit.FAULT1_SUFFIX

    def getFaulty2SignalName(self, signalName):
        """
        Return corresponding faulty signal name of the given signal.
        Assumes that generateMiter has been called before, otherwise this function is not useful
        """
        return signalName + DTPGCircuit.FAULT2_SUFFIX

    def addPairFaults(self, fault, signalName, **kwargs):
        """ variables are set to store where the fault is """
        self.fault1 = fault[0]
        self.fault2 = fault[1]
        self.signalName_f1 = signalName[0]
        self.signalName_f2 = signalName[1]
        self.useOutNode = kwargs.get('useOutNode', None)
        self.inputIndex = kwargs.get('inputIndex', (None,None))
        faulty1SignalName = self.getFaulty1SignalName(self.signalName_f1)
        faulty2SignalName = self.getFaulty2SignalName(self.signalName_f2)

        #add fault1
        if self.signalName_f1 in self.inNodes: # fault at input
            node = self.faultyInNodes[faulty1SignalName]
            # iterate over copy of list because deleting
            # while iterating gives undefined behaviour
            for e in node.outEdges[:]:
                node.disconnectOutput(e)
                self.fault1.connectOutput(e)

        # add fault around a gate
        elif faulty1SignalName in self.gates:
            gate = self.gates[faulty1SignalName]
            if self.inputIndex[0] is None: # fault at output of gate
                node = gate.output
                # iterate over copy of list because deleting 
                # while iterating gives undefined behaviour
                for e in node.outEdges[:]: 
                    node.disconnectOutput(e)
                    self.fault1.connectOutput(e)
            else: # fault at input
                node = gate.inputs[self.inputIndex[0]]
                e = node.inEdge
                e.inNode.disconnectOutput(e)
                self.fault1.connectOutput(e)
        else:
            raise ValueError('cannot add fault 1 because signal is not found')

        #add fault2
        if self.signalName_f2 in self.inNodes: # fault at input
            node = self.faultyInNodes[faulty2SignalName]
            # iterate over copy of list because deleting
            # while iterating gives undefined behaviour
            for e in node.outEdges[:]:
                node.disconnectOutput(e)
                self.fault2.connectOutput(e)

        # add fault around a gate
        elif faulty2SignalName in self.gates:
            gate = self.gates[faulty2SignalName]
            if self.inputIndex[1] is None: # fault at output of gate
                node = gate.output
                # iterate over copy of list because deleting
                # while iterating gives undefined behaviour
                for e in node.outEdges[:]:
                    node.disconnectOutput(e)
                    self.fault2.connectOutput(e)
            else: # fault at input
                node = gate.inputs[self.inputIndex[1]]
                e = node.inEdge
                e.inNode.disconnectOutput(e)
                self.fault2.connectOutput(e)
        else:
            raise ValueError('cannot add fault 2 because signal is not found')

    def removePairFaults(self):
        faulty1SignalName = self.getFaulty1SignalName(self.signalName_f1)
        faulty2SignalName = self.getFaulty2SignalName(self.signalName_f2)
         #remove fault1
        if self.signalName_f1 in self.inNodes: # fault at input
            faultyInNode = self.faultyInNodes[faulty1SignalName]
            for e in self.fault1.outEdges[:]: # BUG
                self.fault1.disconnectOutput(e)
                faultyInNode.connectOutput(e)

        elif self.signalName_f1 in self.gates:
            gate = self.gates[faulty1SignalName]
            if self.inputIndex[0] is None:
                node = gate.output
                for e in self.fault1.outEdges[:]:
                    self.fault1.disconnectOutput(e)
                    node.connectOutput(e)
            else:
                # get corresponding gate and input node from fault free circuit
                fault1FreeGate = self.gates[self.signalName_f1] # corresponding gate in fault free circuit
                fault1FreeNode = fault1FreeGate.inputs[self.inputIndex[0]]
                node = fault1FreeNode.inEdge.inNode
                if isinstance(node, OutputNode):
                    nodeInFaulty1Circuit = self.gates[self.getFaulty1SignalName(node.gate.name)]
                elif isinstance(node, InNode):
                    nodeInFaulty1Circuit = self.faultyInNodes[self.getFaulty1SignalName(node.name)]
                else:
                    print(type(fault1FreeNode))
                    raise ValueError('Edge is connected to invalid node')
                
                assert(len(self.fault1.outEdges) == 1)
                e = self.fault1.outEdges[0]
                self.fault1.disconnectOutput(e)
                nodeInFaulty1Circuit.connectOutput(e) # BUG get corresponding node in faultfree cricuit and reroute edge

        #remove fault2
        if self.signalName_f2 in self.inNodes:  # fault at input
            faultyInNode = self.faultyInNodes[faulty2SignalName]
            for e in self.fault2.outEdges[:]:  # BUG
                self.fault2.disconnectOutput(e)
                faultyInNode.connectOutput(e)

        elif self.signalName_f2 in self.gates:
            gate = self.gates[faulty2SignalName]
            if self.inputIndex[1] is None:
                node = gate.output
                for e in self.fault2.outEdges[:]:
                    self.fault2.disconnectOutput(e)
                    node.connectOutput(e)
            else:
                # get corresponding gate and input node from fault free circuit
                fault2FreeGate = self.gates[self.signalName_f2]  # corresponding gate in fault free circuit
                fault2FreeNode = fault2FreeGate.inputs[self.inputIndex[1]]
                node = fault2FreeNode.inEdge.inNode
                if isinstance(node, OutputNode):
                    nodeInFaulty2Circuit = self.gates[self.getFaulty2SignalName(node.gate.name)]
                elif isinstance(node, InNode):
                    nodeInFaulty2Circuit = self.faultyInNodes[self.getFaulty2SignalName(node.name)]
                else:
                    print(type(fault2FreeNode))
                    raise ValueError('Edge is connected to invalid node')

                assert (len(self.fault2.outEdges) == 1)
                e = self.fault2.outEdges[0]
                self.fault2.disconnectOutput(e)
                nodeInFaulty2Circuit.connectOutput(e)  # BUG get corresponding node in faultfree cricuit and reroute edge

        self.signalName_f1 = None
        self.signalName_f2 = None
        self.fault1 = None
        self.fault2 = None
        self.inputIndex = (None , None)
        self.useOutNode = None

