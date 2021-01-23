## SMT-Based ATPG
generating input pattern that differentiate between Normal and faulty Circuit using Constraints Satisfaction Problems (SMT-based algorithm).

## Fault Modelling 
using miter structure (XOR gates) that is connected to the output node.

![ATPG_Model](/Images/ATPG_model.png)

## Implementation
 We used SMT based test generation algorithm using z3 solver library in python. The input files that describe the circuit need to have the bench format. Implementation steps are described as follows:
    1-	Parsing the input file and building up an internal data structure which contains gates, edges and nodes that represent the circuit.
    2-	Copying the original circuit and appending the miter structure.
    3-	The user can choose the location of the fault and whether it is a stuck-at-0 or stuch-at-1 fault.
    4-	The miter structure connects the corresponding output signals of two circuits with XOR gates and feeds all output signals of these XOR gates into an OR gate. 
    5-	The circuit is then encoded as an SMT instance and passed to the SMT solver Z3.
    6-	Test pattern generation if the instance is satisfiable.
The output of the OR gate can only be 1 if any output of the XOR gates is one. A XOR gate outputs a 1 only if the input bits are different. This means that the miter structure outputs a 1 only if the outputs of the two circuits are different.
 The encoding works as follows: For each input and output of each gate and for each input and output node, a Boolean variable is introduced. For each edge, the connected nodes have to have the same value. For each gate, the output value has to have the value corresponding to its function and input values. For example, a NAND gate with the Inputs 'I1' and 'I2' and Output 'O' has the constraint 'O' == nand (I1, I2). Finally, the output of the miter structure needs to be 1. This ensures that the faulty and fault free circuits have different outputs, and the fault can be observed by only looking at the output values.
If the SMT solver finds a model, i.e., a solution to the instance is found, the generated input pattern, that allows us to check for the given fault, can be extracted. Otherwise, the given fault cannot be detected.

## DTPG 
generating input vector that differentiate between two different faults in the circuit.

## Diagnostic Fault Modelling
![DTPG_Model](/Images/DTPG_model.png)

## Requirements
installing z3 solver :  pip install z3-solver

for more details about **z3 solver** you can visit Github Repository: https://github.com/Z3Prover/z3
**SMT/SAT Solvers** : https://youtu.be/d76e4hV1iJY


## Code Demo
you can test the circuit by running "test_ATPG.py" for automatic test pattern generation and "test_DTPG.py" for diagnostic test pattern generation.
the user enter fault location and type of the fault, then the program generates the test input patter.

you can run "ATPG_benchmarks.py" or "DTPG_benchmarks.py" for generating the test pattern of all possible faults and the result is saved in log files.