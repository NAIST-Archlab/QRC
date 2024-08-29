import qiskit
import numpy as np
import time
from problem import psr
import os, utilities
from qoop.core import metric

types = ['FP32', 'FX32', 'FX24']
#  types = ['FP32']
num_qubits = 5
for datatype in types:
    print(datatype)
    for times in range(1, 2):
        for depth in range(1,11):
            fidelities = []
            for num_qubit in range(3, num_qubits + 1):
                # from software simulator
                origin = np.loadtxt(f'./data/qrc/cpu/{times}/{num_qubit}_{depth}_amplitude.txt', dtype = complex)
                # from FPGA emulator
                reconstruct = utilities.read_complex_numbers(f'./data/qrc/FPGA/QRC/{datatype}/Output/{times}/{num_qubit}_{depth}_amplitude.txt')
                fidelities.append(utilities.fidelity(origin, reconstruct))
                save_path = f'./fidelity/qrc/{datatype}/{times}/qrc_depth_{depth}_Fidelity.txt'
                if not os.path.exists(f'./fidelity/qrc/{datatype}/{times}'):
                    os.makedirs(f'./fidelity/qrc/{datatype}/{times}')
            np.savetxt(save_path, fidelities)