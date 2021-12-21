# import numpy as np
from matplotlib import pyplot as plt

Ac = plt.plot([5,
               10,
               15,
               20,
               25],
              [0.9890859950326383,
               0.9897154067605733,
              0.9902283852636813,
              0.9901786186933518,
              0.9902676009371876])
plt.ylim(0.9890, 0.9905)
plt.xlim(0, 30)
plt.xticks([0, 5, 10, 15, 20, 25, 30])
plt.grid(True)
plt.title('OFDM Simulate on 10000 Blocks Test',
          fontsize=18, fontweight='bold')
plt.ylabel('Accuracy', fontsize=10, fontweight='bold')
plt.xlabel('SNR(Eb/N0)', fontsize=10, fontweight='bold')
plt.setp(Ac, marker='o',
         linestyle='--', markersize=5, linewidth=1)
plt.savefig('OFDM Simulate on 10000 Blocks_Accuracy.jpg')
plt.cla()
Fb = plt.plot([5,
               10,
               15,
               20,
               25],
              [0.9709644467378966,
               0.9754906310437713,
              0.9777779830031331,
              0.9773064691469307,
              0.9804512768131215])
plt.ylim(0.970, 0.981)
plt.xlim(0, 30)
plt.xticks([0, 5, 10, 15, 20, 25, 30])
plt.grid(True)
plt.title('OFDM Simulate on 10000 Blocks Test',
          fontsize=18, fontweight='bold')
plt.ylabel('F-0.1 Score', fontsize=10, fontweight='bold')
plt.xlabel('SNR(Eb/N0)', fontsize=10, fontweight='bold')
plt.setp(Fb, color='red', marker='o',
         linestyle='--', markersize=5, linewidth=1)
plt.savefig('OFDM Simulate on 10000 Blocks_F-0.1.jpg')
plt.cla()
Pr = plt.plot([5,
               10,
               15,
               20,
               25],
              [0.9884194885311648,
               0.9913594731761958,
              0.9925750170802581,
              0.9925373739657341,
              0.9946216550577547])
plt.ylim(0.987, 0.995)
plt.xlim(0, 30)
plt.xticks([0, 5, 10, 15, 20, 25, 30])
plt.grid(True)
plt.title('OFDM Simulate on 10000 Blocks Test',
          fontsize=18, fontweight='bold')
plt.ylabel('Precision', fontsize=10, fontweight='bold')
plt.xlabel('SNR(Eb/N0)', fontsize=10, fontweight='bold')
plt.setp(Pr, color='purple', marker='o',
         linestyle='--', markersize=5, linewidth=1)
plt.savefig('OFDM Simulate on 10000 Blocks_Precision.jpg')
plt.cla()
Rc = plt.plot([5,
               10,
               15,
               20,
               25],
              [0.4065132861509919,
               0.4297448675628752,
              0.44822052444405855,
              0.4415464423671365,
              0.45631645740456875])
plt.ylim(0.40, 0.46)
plt.xlim(0, 30)
plt.xticks([0, 5, 10, 15, 20, 25, 30])
plt.grid(True)
plt.title('OFDM Simulate on 10000 Blocks Test',
          fontsize=18, fontweight='bold')
plt.ylabel('Recall', fontsize=10, fontweight='bold')
plt.xlabel('SNR(Eb/N0)', fontsize=10, fontweight='bold')
plt.setp(Rc, color='brown', marker='o',
         linestyle='--', markersize=5, linewidth=1)
plt.savefig('OFDM Simulate on 10000 Blocks_Recall.jpg')
