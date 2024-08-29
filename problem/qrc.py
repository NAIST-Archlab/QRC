import qiskit
import numpy as np

gate_prob = [1, 1, 1, 2]

def choice_from_array(arr, condition):
    import random
    item = None
    while item is None:
        item = random.choice(arr)
        if condition(item):
            return item
        else:
            item = None
    return item
    
def qrc_Qsun_verify(num_qubits: int, depth: int):
    import numpy as np
    from Qsun.Qcircuit import Qubit
    from Qsun.Qgates import RX, RZ, RY, H, S, CNOT
    seed = np.random.randint(0, np.iinfo(np.int32).max)
    rng = np.random.default_rng(seed)
    max_operands = 2
    circuit = Qubit(num_qubits)
    pool = [RX, RZ, RY, H, S, CNOT]
    list_gates = []
    for _ in range(depth):
        remaining_qubits = list(range(num_qubits))
        while remaining_qubits:
            max_possible_operands = min(len(remaining_qubits), max_operands)
            num_operands = choice_from_array(
                gate_prob, lambda value: value <= max_possible_operands)
            rng.shuffle(remaining_qubits)
            operands = remaining_qubits[:num_operands]
            remaining_qubits = [
                q for q in remaining_qubits if q not in operands]
            if num_operands == 1:
                num_op_pool = [RX, RZ, RY, H, S]
            else:
                num_op_pool = [CNOT]
            operation = rng.choice(num_op_pool)
            if operation == RX or operation == RY or operation == RZ:
                phase = np.random.uniform(0, 2*np.pi)
                operation(circuit, *operands, phase)
                list_gates.append((operation.__name__, operands, phase))
            else:
                operation(circuit, *operands)
                list_gates.append((operation.__name__, operands, -999))
    return circuit, list_gates

def qrc_Qsun(num_qubits: int, depth: int):
    import numpy as np
    from Qsun.Qcircuit import Qubit
    from Qsun.Qgates import RX, RZ, RY, H, S, CNOT
    seed = np.random.randint(0, np.iinfo(np.int32).max)
    rng = np.random.default_rng(seed)
    max_operands = 2
    circuit = Qubit(num_qubits)
    pool = [RX, RZ, RY, H, S, CNOT]
    for _ in range(depth):
        remaining_qubits = list(range(num_qubits))
        while remaining_qubits:
            max_possible_operands = min(len(remaining_qubits), max_operands)
            num_operands = choice_from_array(
                gate_prob, lambda value: value <= max_possible_operands)
            rng.shuffle(remaining_qubits)
            operands = remaining_qubits[:num_operands]
            remaining_qubits = [
                q for q in remaining_qubits if q not in operands]
            if num_operands == 1:
                num_op_pool = [RX, RZ, RY, H, S]
            else:
                num_op_pool = [CNOT]
            operation = rng.choice(num_op_pool)
            if operation == RX or operation == RY or operation == RZ:
                operation(circuit, *operands, np.random.uniform(0, 2*np.pi))
            else:
                operation(circuit, *operands)
    return circuit


def qrc_Qsun_qiskit(num_qubits: int, qiskit_circuit: qiskit.QuantumCircuit):
    """_summary_

    Args:
        num_qubits (int): numbero of qubits
        qiskit_circuit (qiskit.QuantumCircuit): _description_

    Returns:
        _type_: _description_
    """
    from Qsun.Qcircuit import Qubit
    from Qsun.Qgates import RX, RZ, RY, H, S, CNOT
    circuit = Qubit(num_qubits)
    # Map Qiskit gates to ProjectQ gates
    for gate in qiskit_circuit.data:
        if gate[0].name == "h":
            H(circuit, gate[1][0]._index)
        elif gate[0].name == "x":
            S(circuit, gate[1][0]._index)
        elif gate[0].name == "cx":
            CNOT(circuit, gate[1][0]._index, gate[1][1]._index)
        elif gate[0].name == "rx":
            RX(circuit, gate[1][0]._index, gate[0].params[0])
        elif gate[0].name == "ry":
            RY(circuit, gate[1][0]._index, gate[0].params[0])
        elif gate[0].name == "rz":
            RZ(circuit, gate[1][0]._index, gate[0].params[0])
    return circuit.probabilities()

def qrc_ProjectQ_qiskit(num_qubits: int, qiskit_circuit: qiskit.QuantumCircuit):
    from projectq import MainEngine
    from projectq.backends import Simulator
    from projectq.ops import H, X, S, CNOT, Measure, Rx, Ry, Rz, All
    import itertools, numpy as np
    eng = MainEngine(backend=Simulator(gate_fusion=True), engine_list=[])
    qubits = eng.allocate_qureg(num_qubits)

    # Map Qiskit gates to ProjectQ gates
    for gate in qiskit_circuit.data:
        if gate[0].name == "h":
            H | qubits[gate[1][0]._index]
        elif gate[0].name == "x":
            S | qubits[gate[1][0]._index]
        elif gate[0].name == "cx":
            CNOT | (qubits[gate[1][0]._index], qubits[gate[1][1]._index])
        elif gate[0].name == "rx":
            angle = gate[0].params[0]
            Rx(angle) | qubits[gate[1][0]._index]
        elif gate[0].name == "ry":
            angle = gate[0].params[0]
            Ry(angle) | qubits[gate[1][0]._index]
        elif gate[0].name == "rz":
            angle = gate[0].params[0]
            Rz(angle) | qubits[gate[1][0]._index]
        elif gate[0].name == "measure":
            Measure | qubits[gate[1][0]._index]

    strings = ["".join(seq) for seq in itertools.product("01", repeat = num_qubits)]
    probs = np.array([eng.backend.get_probability(i, qubits) for i in strings])
    All(Measure) | qubits
    return probs

def qrc_ProjectQ(num_qubits: int, depth: int):
    import numpy as np
    from projectq import MainEngine
    from projectq.backends import Simulator
    from projectq.ops import H, S, CNOT, Measure, Rx, Ry, Rz, All
    import itertools, numpy as np

    seed = np.random.randint(0, np.iinfo(np.int32).max)
    rng = np.random.default_rng(seed)
    max_operands = 2
    eng = MainEngine(backend=Simulator(gate_fusion=True), engine_list=[])
    qubits = eng.allocate_qureg(num_qubits)
    pool = [Rx, Ry, Rz, H, S, CNOT]
    for _ in range(depth):
        remaining_qubits = list(range(num_qubits))
        while remaining_qubits:
            max_possible_operands = min(len(remaining_qubits), max_operands)
            num_operands = choice_from_array(
                gate_prob, lambda value: value <= max_possible_operands)
            rng.shuffle(remaining_qubits)
            operands = remaining_qubits[:num_operands]
            remaining_qubits = [
                q for q in remaining_qubits if q not in operands]
            if num_operands == 1:
                num_op_pool = [Rx, Ry, Rz, H, S]
            else:
                num_op_pool = [CNOT]
            operation = rng.choice(num_op_pool)
            if operation in [Rx, Ry, Rz]:
                operation(np.random.uniform(0, 2*np.pi)) | qubits[operands[0]]
            elif operation == CNOT:
                operation | (qubits[operands[0]], qubits[operands[1]])
            else:
                operation | qubits[operands[0]]
    strings = ["".join(seq) for seq in itertools.product("01", repeat = num_qubits)]
    probs = np.array([eng.backend.get_probability(i, qubits) for i in strings])
    All(Measure) | qubits
    return probs
def qrc_Qiskit(num_qubits: int, depth: int):
    import numpy as np
    from qiskit.circuit.library.standard_gates import (IGate, U1Gate, U2Gate, U3Gate, XGate,
                                                   YGate, ZGate, HGate, SGate, SdgGate, TGate,
                                                   TdgGate, RXGate, RYGate, RZGate, CXGate,
                                                   CYGate, CZGate, CHGate, CRXGate, CRYGate, CRZGate, CU1Gate,
                                                   CU3Gate, SwapGate, RZZGate,
                                                   CCXGate, CSwapGate)
    def initialize_random_parameters(num_qubits: int, max_operands: int, conditional: bool, seed):
        if max_operands < 1 or max_operands > 3:
            raise qiskit.circuit.exceptions.CircuitError("max_operands must be between 1 and 3")

        qr = qiskit.circuit.QuantumRegister(num_qubits, 'q')
        qc = qiskit.circuit.QuantumCircuit(num_qubits)

        if conditional:
            cr = qiskit.circuit.ClassicalRegister(num_qubits, 'c')
            qc.add_register(cr)

        if seed is None:
            seed = np.random.randint(0, np.iinfo(np.int32).max)

        rng = np.random.default_rng(seed)
        thetas = qiskit.circuit.ParameterVector('theta')
        return qr, qc, rng, thetas  
    H_gate = {'name': 'h', 'operation': HGate, 'num_op': 1, 'num_params': 0}
    S_gate = {'name': 's', 'operation': SGate, 'num_op': 1, 'num_params': 0}
    CX_gate = {'name': 'cx', 'operation': CXGate, 'num_op': 2, 'num_params': 0}
    RX_gate = {'name': 'rx', 'operation': RXGate, 'num_op': 1, 'num_params': 1}
    RY_gate = {'name': 'ry', 'operation': RYGate, 'num_op': 1, 'num_params': 1}
    RZ_gate = {'name': 'rz', 'operation': RZGate, 'num_op': 1, 'num_params': 1}
    pool = [
        H_gate,
        S_gate,
        CX_gate,
        RX_gate,
        RY_gate,
        RZ_gate,

    ]
    max_operands = 3
    conditional = False
    seed=None
    qr, qc, rng, thetas = initialize_random_parameters(num_qubits, max_operands, conditional, seed)
    thetas_length = 0
    for _ in range(depth):
        remaining_qubits = list(range(num_qubits))
        while remaining_qubits:
            max_possible_operands = min(len(remaining_qubits), max_operands)
            num_operands = choice_from_array(
                [1, 2], lambda value: value <= max_possible_operands)
            rng.shuffle(remaining_qubits)
            operands = remaining_qubits[:num_operands]
            remaining_qubits = [
                q for q in remaining_qubits if q not in operands]
            num_op_pool = [
                item for item in pool if item['num_op'] == num_operands]

            operation = rng.choice(num_op_pool)
            num_params = operation['num_params']
            thetas_length += num_params
            thetas.resize(thetas_length)
            angles = thetas[thetas_length - num_params:thetas_length]
            register_operands = [qr[i] for i in operands]
            op = operation['operation'](*angles)
            qc.append(op, register_operands)
    qc = qc.assign_parameters(np.random.uniform(0, 2*np.pi, size = len(qc.parameters)))
    return qc

import pennylane as qml

dev = qml.device('default.qubit')
@qml.qnode(dev)
def qrc_Pennylane_qiskit( num_qubits: int, qc: qiskit.QuantumCircuit):
    qml.from_qiskit(qc)(wires=range(num_qubits))
    return qml.probs(wires=range(num_qubits))


@qml.qnode(dev)
def qrc_Pennylane(num_qubits: int, depth: int):
    import numpy as np
    seed = np.random.randint(0, np.iinfo(np.int32).max)
    rng = np.random.default_rng(seed)
    max_operands = 2
    for _ in range(depth):
        remaining_qubits = list(range(num_qubits))
        while remaining_qubits:
            max_possible_operands = min(len(remaining_qubits), max_operands)
            num_operands = choice_from_array(
                gate_prob, lambda value: value <= max_possible_operands)
            rng.shuffle(remaining_qubits)
            operands = remaining_qubits[:num_operands]
            remaining_qubits = [
                q for q in remaining_qubits if q not in operands]
            if num_operands == 1:
                num_op_pool = [qml.RX, qml.RY, qml.RZ, qml.Hadamard, qml.S]
            else:
                num_op_pool = [qml.CNOT]
            operation = rng.choice(num_op_pool)
            if operation in [qml.RX, qml.RY, qml.RZ]:
                operation(np.random.uniform(0, 2*np.pi), *operands)
            else:
                operation(wires = operands)
    return qml.probs(wires=range(num_qubits))


