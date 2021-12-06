# import numpy as np
from matplotlib import pyplot as plt

Ac = plt.plot([5, 10, 15, 20, 25, 30], [0.9880140063166618, 0.9894267046451569,
              0.989484594464302, 0.9900009343028069, 0.9897245571017265, 0.9901419240236282])
Fb = plt.plot([5, 10, 15, 20, 25, 30], [0.8626563475381238, 0.882832329978855,
              0.8823265895461175, 0.8975952825926349, 0.8921919969955546, 0.9002076907522365])
Pr = plt.plot([5, 10, 15, 20, 25, 30], [0.937890645245843, 0.9570646419824124,
              0.9564483328483854, 0.9710534354856965, 0.9650933718386321, 0.969389611356594])
Rc = plt.plot([5, 10, 15, 20, 25, 30], [0.18408903208749628, 0.19988267642850573,
              0.1960936922516995, 0.19835729364631526, 0.2031650248840634, 0.21570928249830015])
plt.ylim(0.987, 0.991)
plt.xlim(0, 35)
plt.xticks([0, 5, 10, 15, 20, 25, 30, 35])
plt.grid(True)
plt.title('OFDM Simulate on 1000 Blocks Test',
          fontsize=18, fontweight='bold')
plt.ylabel('Accuracy', fontsize=10, fontweight='bold')
plt.xlabel('SNR(Eb/N0)', fontsize=10, fontweight='bold')
plt.setp(Ac, marker='o',
         linestyle='--', markersize=5, linewidth=1)
plt.savefig('OFDM Simulate on 1000 Blocks_Accuracy.jpg')
plt.ylim(0.86, 0.91)
plt.xlim(0, 35)
plt.xticks([0, 5, 10, 15, 20, 25, 30, 35])
plt.grid(True)
plt.title('OFDM Simulate on 1000 Blocks Test',
          fontsize=18, fontweight='bold')
plt.ylabel('F-0.1 Score', fontsize=10, fontweight='bold')
plt.xlabel('SNR(Eb/N0)', fontsize=10, fontweight='bold')
plt.setp(Fb, color='red', marker='o',
         linestyle='--', markersize=5, linewidth=1)
plt.savefig('OFDM Simulate on 1000 Blocks_F-0.1.jpg')
plt.ylim(0.93, 0.98)
plt.xlim(0, 35)
plt.xticks([0, 5, 10, 15, 20, 25, 30, 35])
plt.grid(True)
plt.title('OFDM Simulate on 1000 Blocks Test',
          fontsize=18, fontweight='bold')
plt.ylabel('Precision', fontsize=10, fontweight='bold')
plt.xlabel('SNR(Eb/N0)', fontsize=10, fontweight='bold')
plt.setp(Pr, color='red', marker='o',
         linestyle='--', markersize=5, linewidth=1)
plt.savefig('OFDM Simulate on 1000 Blocks_Precision.jpg')
plt.ylim(0.18, 0.22)
plt.xlim(0, 35)
plt.xticks([0, 5, 10, 15, 20, 25, 30, 35])
plt.grid(True)
plt.title('OFDM Simulate on 1000 Blocks Test',
          fontsize=18, fontweight='bold')
plt.ylabel('Recall', fontsize=10, fontweight='bold')
plt.xlabel('SNR(Eb/N0)', fontsize=10, fontweight='bold')
plt.setp(Rc, color='red', marker='o',
         linestyle='--', markersize=5, linewidth=1)
plt.savefig('OFDM Simulate on 1000 Blocks_Recall.jpg')
