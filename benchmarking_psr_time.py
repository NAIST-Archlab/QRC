from problem import psr
import numpy as np
import time

cost_funcs = [psr.cost_Qsun, psr.cost_ProjectQ, psr.cost_Qiskit, psr.cost_Pennylane]
packages = ['Qsun', 'ProjectQ', 'Qiskit', 'Pennylane']
server = 'cad114'
num_qubits = 17
num_repeats = 100
for j, package in enumerate(packages):
    print(f'-- Package: {package} --')
    timess = []
    timess_std = []
    for num_qubit in range(3, num_qubits + 1):
        times = []
        for _ in range(num_repeats):
            start = time.time()
            params = np.ones((3*num_qubit,))
            diff = psr.psr(cost_funcs[j], params)
            end = time.time()
            times.append(end-start)
        timess.append(np.mean(times))
        timess_std.append(np.std(times))
        np.savetxt(f'./time/psr/psr_{package}_{server}_Time.txt', timess)
        np.savetxt(f'./time/psr/psr_{package}_{server}_TimeSTD.txt', timess_std)