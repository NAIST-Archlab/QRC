import qiskit
import qiskit.quantum_info
import numpy as np
import time
from problem import qrc
import os


for num_qubits in range(3, 18):
    print(f"num_qubits = {num_qubits}")
    for depth in range(1, 11):
        for time in range(1,51):
            circuit, gates = qrc.qrc_Qsun_verify(num_qubits, depth)
            folder_path = f"./data/qrc/cpu/{time}"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            with open(f"./data/qrc/cpu/{time}/{num_qubits}_{depth}.txt", "w") as text_file:
                gates_str = '\n'.join([str(gate) for gate in gates])
                text_file.write(gates_str)
            np.savetxt(f"./data/qrc/cpu/{time}/{num_qubits}_{depth}_amplitude.txt", circuit.amplitude)