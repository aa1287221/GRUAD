# import numpy as np
from matplotlib import pyplot as plt

Ac = plt.plot([5, 10, 15, 20, 25], [0.9846143798530102, 0.9822735771238804,
                                    0.9823295993991196, 0.9868732370745689, 0.9844369756430388])
Fb = plt.plot([5, 10, 15, 20, 25], [0.7907128770069615, 0.7861544718314809,
                                    0.8529279924378349, 0.8616311117531777, 0.844717353046518])
plt.ylim(0.97, 1)
plt.xlim(0, 30)
plt.xticks([0, 5, 10, 15, 20, 25, 30])
plt.grid(True)
plt.title('OFDM Simulate on 1000 Blocks', fontsize=18, fontweight='bold')
plt.ylabel('Accuracy', fontsize=10, fontweight='bold')
plt.xlabel('SNR(Eb/N0)', fontsize=10, fontweight='bold')
plt.setp(Ac, marker='o',
         linestyle='--', markersize=5, linewidth=1)
plt.savefig('OFDM Simulate on 1000 Blocks_Accuracy.jpg')
plt.ylim(0.7, 0.9)
plt.xlim(0, 30)
plt.xticks([0, 5, 10, 15, 20, 25, 30])
plt.grid(True)
plt.title('OFDM Simulate on 1000 Blocks', fontsize=18, fontweight='bold')
plt.ylabel('F-0.1 Score', fontsize=10, fontweight='bold')
plt.xlabel('SNR(Eb/N0)', fontsize=10, fontweight='bold')
plt.setp(Fb, color='red', marker='o',
         linestyle='--', markersize=5, linewidth=1)
plt.savefig('OFDM Simulate on 1000 Blocks_F-0.1.jpg')
