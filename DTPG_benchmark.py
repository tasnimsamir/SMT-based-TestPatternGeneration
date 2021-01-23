from Parser import *
from DTPG import *
import logging
import time


DIRECTORY = "./bnch"
DTP = {}
def run_test(dtpg : DTPG, fault, signalName, inputIndex = (None , None), useOutNode = None):
        dtpg.addPairFaults(fault, signalName, inputIndex, useOutNode)
        dtpg.solve()
        log_info = str(signalName[0]) +\
                                ("[" + str(inputIndex[0]) + "]" if inputIndex[0] != None else "") + \
                                ("[Output]" if useOutNode is not None else "") + \
                                " , " + \
                   str(signalName[1]) + \
                                ("[" + str(inputIndex[1]) + "]" if inputIndex[1] != None else "") + \
                                ("[Output]" if useOutNode is not None else "") + \
                                ": "

        if dtpg.s.check() == sat:
            inValues =[dtpg.s.model()[dtpg.vars[nodeName]] for nodeName in dtpg.circuit.getInNodeNames()]
            inValuesStr = "".join([("1" if is_true(i) else "0") for i in inValues])
            if inValuesStr not in DTP.keys():
                DTP[inValuesStr] = [(str(signalName[0]) +("[" + str(inputIndex[0]) + "]" if inputIndex[0] != None else "")+ '|' + ("1" if fault[0] == Circuit.STUCK_AT_1_FAULT else '0'), str(signalName[1]) +("[" + str(inputIndex[1]) + "]" if inputIndex[1] != None else "")+ '|' + ("1" if fault[1] == Circuit.STUCK_AT_1_FAULT else '0'))]
            else:
                stored_diagnostic_set = DTP[inValuesStr]
                stored_diagnostic_set.append((str(signalName[0]) +("[" + str(inputIndex[0]) + "]" if inputIndex[0] != None else "") + '|' + ("1" if fault[0] == Circuit.STUCK_AT_1_FAULT else '0'), str(signalName[1]) +("[" + str(inputIndex[1]) + "]" if inputIndex[1] != None else "")+ '|' + ("1" if fault[1] == Circuit.STUCK_AT_1_FAULT else '0')))
                DTP[inValuesStr] = stored_diagnostic_set
            logging.info(log_info + inValuesStr)
        else:
            logging.info(log_info + "No test case possible")
        dtpg.removePairFaults()

logging.basicConfig(format = '%(message)s', filename='benchmark_DTPG_failureLog.log', filemode='w', level=logging.INFO)

for filename in os.listdir(DIRECTORY):
    logging.info("START with " + filename)
    c = Circuit()
    p = Parser(c, os.path.join(DIRECTORY, filename))
    p.parse()
    dtpg = DTPG(c)
    fault_pairs = {"01":(c.STUCK_AT_0_FAULT, c.STUCK_AT_1_FAULT) , "10":(c.STUCK_AT_1_FAULT, c.STUCK_AT_0_FAULT),"00":(c.STUCK_AT_0_FAULT, c.STUCK_AT_0_FAULT) ,"11":(c.STUCK_AT_1_FAULT, c.STUCK_AT_1_FAULT)}
    signal_info = []
    logging.info("Inputs: " + " ".join(c.getInNodeNames()))
    start = time.process_time()
    for fault in fault_pairs.keys():
        logging.info("START with fault_pair " + fault)
        for inputNodeName in c.inNodes:
            loc1 = inputNodeName
            for inputNodeName in c.inNodes:
                if inputNodeName != loc1:
                    loc2 = inputNodeName
                    if ((loc1, loc2, fault_pairs[fault][0] , fault_pairs[fault][1]) not in signal_info) and (loc1 != loc2):
                        signal_info.append((loc1, loc2 , fault_pairs[fault][0] , fault_pairs[fault][1]))
                        run_test(dtpg, fault_pairs[fault], signalName= (loc1 , loc2))
            for gateName in c.gates:
                loc2 = gateName
                if ((loc1, loc2, fault_pairs[fault][0] , fault_pairs[fault][1]) not in signal_info) and (loc1 != loc2):
                    signal_info.append((loc1, loc2 , fault_pairs[fault][0] , fault_pairs[fault][1]))
                    run_test(dtpg, fault_pairs[fault], signalName=(loc1, loc2))
                    for i in range(len(c.gates[gateName].inputs)):
                        run_test(dtpg, fault_pairs[fault], (loc1, loc2), inputIndex= (None , i))
#===========================================================================================================
        for gateName in c.gates:
            loc1 = gateName
            for inputNodeName in c.inNodes:
                loc2 = inputNodeName
                if ((loc1, loc2, fault_pairs[fault][0] , fault_pairs[fault][1]) not in signal_info) and (loc1 != loc2):
                    signal_info.append((loc1, loc2, fault_pairs[fault][0], fault_pairs[fault][1]))
                    run_test(dtpg, fault_pairs[fault], signalName=(loc1, loc2))
            for gateName in c.gates:
                if gateName != loc1:
                    loc2 = gateName
                    if ((loc1, loc2, fault_pairs[fault][0] , fault_pairs[fault][1]) not in signal_info) and (loc1 != loc2):
                        signal_info.append((loc1, loc2 , fault_pairs[fault][0] , fault_pairs[fault][1]))
                        run_test(dtpg, fault_pairs[fault], signalName=(loc1, loc2))
                        for i in range(len(c.gates[gateName].inputs)):
                            run_test(dtpg, fault_pairs[fault], (loc1, loc2), inputIndex= (None , i))

        logging.info("FINISHED with fault_pair " + fault)
        logging.info("========================================================================================================================")
    end = time.process_time()
    logging.info(filename + " ELAPSED TIME: " + str(end - start) + " seconds")
    print(filename + " ELAPSED TIME: " + str(end - start) + " seconds")
    logging.info("FINISHED with " + filename)
    logging.info("****************************************************************************************************************************")

print(DTP.keys())
