import itertools
import time
import types
import numpy as np

# ---------------------
# -------- Qsun -------
# ---------------------

def circuit_Qsun(params: np.ndarray, num_qubits: int):
    """_Generate vanilla ZXZ circuit

    Args:
        params (np.ndarray): parameters for parameterized quantum circuit
        num_qubits (int): number of qubits

    Returns:
        Qsun.Wavefunction.Wavefunction: vanilla quantum circuit
    """
    from Qsun.Qcircuit import Qubit
    from Qsun.Qgates import RX, RZ
    from Qsun.Qwave import Wavefunction

    c: Wavefunction = Qubit(num_qubits)
    j = 0
    for i in range(0, num_qubits):
        RZ(c, i, params[j])
        RX(c, i, params[j + 1])
        RZ(c, i, params[j + 2])
        j += 3
    return c

def cost_Qsun(params: np.ndarray) -> float:
    """Just a cost function for benchmarking

    Args:
        params (np.ndarray): parameters

    Returns:
        float: cost value
    """
    c = circuit_Qsun(params, len(params)//3)
    prob = c.probabilities()
    return -np.sum([i*prob[i] for i in range(len(prob))])


def psr(cost: types.FunctionType, params: np.ndarray, epsilon: float = np.pi/2, lr: float = 0.01) -> np.ndarray:
    """Return \nabla\mathcal{C}(\theta) by using 2-term parameter shift rule

    Args:
        params (np.ndarray): parameter
        epsilon (float, optional): Shifted value. Defaults to np.pi/2.
        lr (float, optional): learning rate hyperparameter. Defaults to 0.01.

    Returns:
        np.ndarray: gradient of cost function
    """
    grad = np.ones((len(params),))
    for i in range(len(params)):
        params_1 = params.copy()
        params_2 = params.copy()
        params_1[i] += epsilon
        params_2[i] -= epsilon
        grad[i] = (cost(params_1)-cost(params_2))/(2*np.sin(epsilon))
    for i in range(len(params)):
        params[i] = params[i] - lr*grad[i] # SGD
    return params

# ---------------------
# ----- ProjectQ ------
# ---------------------

def circuit_ProjectQ(params, num_qubits):
    from projectq.backends import Simulator
    from projectq import MainEngine
    import projectq.ops as ops
    import itertools
    eng = MainEngine(backend=Simulator(gate_fusion=True), engine_list=[])
    qbits = eng.allocate_qureg(num_qubits)
    j = 0
    for i in range(0, num_qubits):
        ops.Rz(params[j]) | qbits[i]
        ops.Rx(params[j+1]) | qbits[i]
        ops.Rz(params[j+2]) | qbits[i]
        j += 3
    strings = ["".join(seq) for seq in itertools.product("01", repeat = num_qubits)]
    probs = np.array([eng.backend.get_probability(i, qbits) for i in strings])
    ops.All(ops.Measure) | qbits
    eng.flush()
    return probs
def cost_ProjectQ(params):
    prob = circuit_ProjectQ(params, len(params)//3)
    return -np.sum([i*prob[i] for i in range(len(prob))])

# ---------------------
# ----- Pennylane -----
# ---------------------

import pennylane as qml
dev = qml.device('default.qubit')


@qml.qnode(dev)
def circuit_Pennylane(params: np.ndarray, num_qubits: int):
    j = 0
    for i in range(0, num_qubits):
        qml.RZ(params[j], wires=i)
        qml.RX(params[j+1], wires=i)
        qml.RZ(params[j+2], wires=i)
        j += 3
    return qml.probs(wires=range(num_qubits))

def cost_Pennylane(params):
    prob = circuit_Pennylane(params, len(params)//3)
    return -np.sum([i*prob[i] for i in range(len(prob))])

# ---------------------
# ------- Qiskit ------
# ---------------------


def circuit_Qiskit(params: np.ndarray, num_qubits: int):
    import qiskit
    import qiskit.quantum_info
    qc = qiskit.QuantumCircuit(num_qubits)
    j = 0
    for i in range(0, num_qubits):
        qc.rz(params[j], i)
        qc.rx(params[j+1], i)
        qc.rz(params[j+2], i)
        j += 3
    return qiskit.quantum_info.Statevector.from_instruction(qc).probabilities()

def cost_Qiskit(params):
    prob = circuit_Qiskit(params, len(params)//3)
    return -np.sum([i*prob[i] for i in range(len(prob))])