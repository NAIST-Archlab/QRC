import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import os

num_qubits = 17
for times in range(1, 2):
    for depth in range(1,11):
        num_gates = []
        for num_qubit in range(3, num_qubits + 1):
            # from software simulator
            with open(f'./data/qrc/cpu/{times}/{num_qubit}_{depth}.txt', 'r') as file:
                num_gate = sum(1 for line in file)
            save_path = f'./gate/qrc/{times}/qrc_{depth}depth_NumGate.txt'
            if not os.path.exists(f'./gate/qrc/{times}'):
                os.makedirs(f'./gate/qrc/{times}')
            num_gates.append(num_gate)
        
        np.savetxt(save_path, num_gates, fmt='%d')