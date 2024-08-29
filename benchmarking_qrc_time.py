import numpy as np
import matplotlib.pyplot as plt
from problem import qrc
import time

funcs = [qrc.qrc_Qsun, qrc.qrc_ProjectQ, qrc.qrc_Qiskit, qrc.qrc_Pennylane]
packages = ['Qsun', 'ProjectQ', 'Qiskit', 'Pennylane']
server = 'cad114'

depths = 10
num_qubits = 17
num_repeats = 100
for j, package in enumerate(packages):
    print(f'-- Package: {package} --')
    for depth in range(1, depths + 1):
        print(f'-- # depth: {depth} --')
        timess = []
        for num_qubit in range(3, num_qubits + 1):
            times = []
            for _ in range(num_repeats):
                start = time.time()
                prob = funcs[j](num_qubit, depth)
                end = time.time()
                times.append(end-start)
            timess.append(np.mean(times))
        
        np.savetxt(f'./time/qrc/QRC_{package}_{server}_depth{depth}_Time.txt', timess)