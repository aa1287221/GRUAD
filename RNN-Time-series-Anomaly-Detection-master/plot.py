import numpy as np
from matplotlib import pyplot as plt
SNRresult128 = np.loadtxt('SNR_result128.txt')
SNRresult1024 = np.loadtxt('SNR_result1024.txt')
SNR128 = SNRresult128[:, 0]
SNR1024 = SNRresult1024[:, 0]
ACC128 = SNRresult128[:, 1]
ACC1024 = SNRresult1024[:, 1]
FBETA128 = SNRresult128[:, 2]
FBETA1024 = SNRresult1024[:, 2]

Ac128 = plt.plot(SNR128, ACC128, label='Block Length 128')
Ac1024 = plt.plot(SNR1024, ACC1024, label='Block Length 1024')
plt.ylim(0.97, 1)
plt.xlim(0, 30)
plt.xticks([0, 5, 10, 15, 20, 25, 30])
plt.grid(True)
plt.title('OFDM Simulate on 10000 Blocks Test',
          fontsize=18, fontweight='bold')
plt.ylabel('Accuracy', fontsize=10, fontweight='bold')
plt.xlabel('SNR(Eb/N0)', fontsize=10, fontweight='bold')
plt.setp(Ac128, marker='o',
         linestyle='--', markersize=5, linewidth=1)
plt.setp(Ac1024, color='red', marker='*',
         linestyle='--', markersize=5, linewidth=1)
plt.legend()
plt.savefig('OFDM Simulate on 10000 Blocks_Accuracy.jpg')
plt.cla()
Fb128 = plt.plot(SNR128, FBETA128, label='Block Length 128')
Fb1024 = plt.plot(SNR1024, FBETA1024, label='Block Length 1024')
plt.ylim(0.95, 0.99)
plt.xlim(0, 30)
plt.xticks([0, 5, 10, 15, 20, 25, 30])
plt.grid(True)
plt.title('OFDM Simulate on 10000 Blocks Test',
          fontsize=18, fontweight='bold')
plt.ylabel('F-0.1 Score', fontsize=10, fontweight='bold')
plt.xlabel('SNR(Eb/N0)', fontsize=10, fontweight='bold')
plt.setp(Fb128, marker='o',
         linestyle='--', markersize=5, linewidth=1)
plt.setp(Fb1024, color='red', marker='*',
         linestyle='--', markersize=5, linewidth=1)
plt.legend()
plt.savefig('OFDM Simulate on 10000 Blocks_F-0.1.jpg')
plt.cla()
# Pr = plt.plot([5,
#                10,
#                15,
#                20,
#                25],
#               [0.9884194885311648,
#                0.9913594731761958,
#               0.9925750170802581,
#               0.9925373739657341,
#               0.9946216550577547])
# plt.ylim(0.987, 0.995)
# plt.xlim(0, 30)
# plt.xticks([0, 5, 10, 15, 20, 25, 30])
# plt.grid(True)
# plt.title('OFDM Simulate on 10000 Blocks Test',
#           fontsize=18, fontweight='bold')
# plt.ylabel('Precision', fontsize=10, fontweight='bold')
# plt.xlabel('SNR(Eb/N0)', fontsize=10, fontweight='bold')
# plt.setp(Pr, color='purple', marker='o',
#          linestyle='--', markersize=5, linewidth=1)
# plt.savefig('OFDM Simulate on 10000 Blocks_Precision.jpg')
# plt.cla()
# Rc = plt.plot([5,
#                10,
#                15,
#                20,
#                25],
#               [0.4065132861509919,
#                0.4297448675628752,
#               0.44822052444405855,
#               0.4415464423671365,
#               0.45631645740456875])
# plt.ylim(0.40, 0.46)
# plt.xlim(0, 30)
# plt.xticks([0, 5, 10, 15, 20, 25, 30])
# plt.grid(True)
# plt.title('OFDM Simulate on 10000 Blocks Test',
#           fontsize=18, fontweight='bold')
# plt.ylabel('Recall', fontsize=10, fontweight='bold')
# plt.xlabel('SNR(Eb/N0)', fontsize=10, fontweight='bold')
# plt.setp(Rc, color='brown', marker='o',
#          linestyle='--', markersize=5, linewidth=1)
# plt.savefig('OFDM Simulate on 10000 Blocks_Recall.jpg')
