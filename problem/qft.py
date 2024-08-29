

def qft_Qsun(num_qubits: int):
    from Qsun.Qwave import Wavefunction
    from Qsun.Qcircuit import Qubit
    from Qsun.Qgates import RZ, H, CNOT
    def qft_rotations_Qsun(circuit: Wavefunction, num_qubits: int):
        import numpy as np
        if num_qubits == 0:
            return circuit
        num_qubits -= 1
        H(circuit, num_qubits)
        for j in range(num_qubits):
            # qc.cp(np.pi/2**(num_qubits-j), j, num_qubits)
            RZ(circuit, j, (np.pi/2**(num_qubits-j)) / 2)
            CNOT(circuit, j, num_qubits)
            RZ(circuit, num_qubits, -(np.pi/2**(num_qubits-j)) / 2)
            CNOT(circuit, j, num_qubits)
            RZ(circuit, num_qubits, (np.pi/2**(num_qubits-j)) / 2)
        qft_rotations_Qsun(circuit, num_qubits)
    def swap_registers_Qsun(circuit: Wavefunction, num_qubits: int):
        for j in range(num_qubits // 2):
            CNOT(circuit, j, num_qubits-j-1)
            CNOT(circuit, num_qubits-j-1, j)
            CNOT(circuit, j, num_qubits-j-1)
        return circuit

    circuit = Qubit(num_qubits)
    qft_rotations_Qsun(circuit, num_qubits)
    swap_registers_Qsun(circuit, num_qubits)
    return circuit.probabilities()

def qft_Qsun_verify(num_qubits: int):
    from Qsun.Qwave import Wavefunction
    from Qsun.Qcircuit import Qubit
    from Qsun.Qgates import RZ, H, CNOT
    def qft_rotations_Qsun(circuit: Wavefunction, num_qubits: int):
        import numpy as np
        if num_qubits == 0:
            return circuit
        num_qubits -= 1
        H(circuit, num_qubits)
        for j in range(num_qubits):
            RZ(circuit, num_qubits, np.pi/2**(num_qubits-j) / 2)
            CNOT(circuit, j, num_qubits)
            RZ(circuit, num_qubits, -np.pi/2**(num_qubits-j) / 2)
            CNOT(circuit, j, num_qubits)
            RZ(circuit, num_qubits, +np.pi/2**(num_qubits-j) / 2)
        qft_rotations_Qsun(circuit, num_qubits)
    def swap_registers_Qsun(circuit: Wavefunction, num_qubits: int):
        for j in range(num_qubits // 2):
            CNOT(circuit, j, num_qubits-j-1)
            CNOT(circuit, num_qubits-j-1, j)
            CNOT(circuit, j, num_qubits-j-1)
        return circuit

    circuit = Qubit(num_qubits)
    qft_rotations_Qsun(circuit, num_qubits)
    swap_registers_Qsun(circuit, num_qubits)
    return circuit.amplitude



def qft_ProjectQ(num_qubits: int):
    from projectq.backends import Simulator
    from projectq import MainEngine
    import projectq.ops as ops
    import itertools
    import numpy as np
    def qft_rotations_ProjectQ(qbits, num_qubits: int):
        if num_qubits == 0:
            return qbits
        num_qubits -= 1
        ops.H | qbits[num_qubits]
        for j in range(num_qubits):
            ops.Rz(np.pi/2**(num_qubits - j) / 2) | qbits[num_qubits]
            ops.CX | (qbits[j], qbits[num_qubits])
            ops.Rz(-np.pi/2**(num_qubits - j) / 2) | qbits[num_qubits]
            ops.CX | (qbits[j], qbits[num_qubits])
            ops.Rz(+np.pi/2**(num_qubits - j) / 2) | qbits[num_qubits]
        qft_rotations_ProjectQ(qbits, num_qubits)
    def swap_registers_ProjectQ(qbits, num_qubits: int):
        for j in range(num_qubits // 2):
            ops.CX | (qbits[j], qbits[num_qubits-j-1])
            ops.CX | (qbits[num_qubits-j-1], qbits[j])
            ops.CX | (qbits[j], qbits[num_qubits-j-1])
        return qbits

    eng = MainEngine(backend=Simulator(gate_fusion=True), engine_list=[])
    qbits = eng.allocate_qureg(num_qubits)
    qft_rotations_ProjectQ(qbits, num_qubits)
    swap_registers_ProjectQ(qbits, num_qubits)
    strings = ["".join(seq) for seq in itertools.product("01", repeat = num_qubits)]
    probs = np.array([eng.backend.get_probability(i, qbits) for i in strings])
    ops.All(ops.Measure) | qbits
    return probs




def qft_Qiskit(num_qubits):
    import qiskit
    import numpy as np
    """QFT on the first n qubits in circuit"""
    def qft_rotations_Qiskit(qc: qiskit.QuantumCircuit, num_qubits):
        """Performs qft on the first n qubits in circuit (without swaps)"""
        if num_qubits == 0:
            return qc
        num_qubits -= 1
        qc.h(num_qubits)
        for j in range(num_qubits):
            
            # qc.rz(np.pi/2**(num_qubits-j) / 2, num_qubits)
            # qc.cx(j, num_qubits)
            # qc.rz(-np.pi/2**(num_qubits-j) / 2, num_qubits)
            # qc.cx(j, num_qubits)
            # qc.rz(+np.pi/2**(num_qubits-j) / 2, num_qubits)
            
            qc.cp(np.pi/2**(num_qubits-j), j, num_qubits)
            qc.barrier()
        qft_rotations_Qiskit(qc, num_qubits)
    def swap_registers_Qiskit(qc, num_qubits):
        for j in range(num_qubits//2):
            qc.cx(j, num_qubits-j-1)
            qc.cx(num_qubits-j-1, j)
            qc.cx(j, num_qubits-j-1)
            qc.barrier()
        return qc
    qc = qiskit.QuantumCircuit(num_qubits)
    qft_rotations_Qiskit(qc, num_qubits)
    swap_registers_Qiskit(qc, num_qubits)
    prob = qiskit.quantum_info.Statevector.from_instruction(qc).probabilities()
    return prob



import pennylane as qml
from pennylane import numpy as np

dev = qml.device('default.qubit')
@qml.qnode(dev)
def qft_Pennylane(num_qubits: int):
    def qft_rotations_Pennylane(num_qubits: int):
        """Performs QFT on the given wires (without swaps)"""
        if num_qubits == 0:
            return
        num_qubits -= 1
        qml.Hadamard(num_qubits)
        for j in range(num_qubits - 1):
            qml.ControlledPhaseShift(np.pi / 2**(num_qubits-j-1), wires = [j, num_qubits])
        qft_rotations_Pennylane(num_qubits)

    def swap_registers_Pennylane(num_qubits: int):
        for j in range(num_qubits // 2):
            qml.CNOT(wires = [j, num_qubits-j-1])
            qml.CNOT(wires = [num_qubits-j-1, j])
            qml.CNOT(wires = [j, num_qubits-j-1])
    qft_rotations_Pennylane(num_qubits)
    swap_registers_Pennylane(num_qubits)
    # return qml.state()
    return qml.probs(wires=range(num_qubits))
