import numpy as np
import os

Noise_Position_filepath = '/home/wky/RNNAD/RNN-Time-series-Anomaly-Detection-master/dataset/ofdm/raw/NoisePosition.npy'
Noise_Symbol_filepath = '/home/wky/RNNAD/RNN-Time-series-Anomaly-Detection-master/dataset/ofdm/raw/NoiseSymbol.txt'

K = 1024  # subcarriers = K
CP = K // 32
P = 64  # number of pilot carriers per OFDM block
mu = 2    # one symbol combined with two bits for QAM or QPSK (LJS)
# payloadbits per OFDM version 2 (decided by how many data carriers per OFDM , LJS)
payloadBits_per_OFDM = K * mu

SNRdb = 30  # signal to noise-ratio in dB at the receiver

mapping_table = {
    (0, 0): -1 - 1j,
    (0, 1): -1 + 1j,
    (1, 0): 1 - 1j,
    (1, 1): 1 + 1j,
}

demapping_table = {v: k for k, v in mapping_table.items()}

if os.path.isfile('checkpoint.txt'):
    checkpoint = np.loadtxt('checkpoint.txt')
else:
    np.savetxt('checkpoint.txt', [0, 0, 0, 0, 0])
    checkpoint = np.loadtxt('checkpoint.txt')
valid_epochs = int(checkpoint[0])
total_accuracy = float(checkpoint[1])
total_fbeta = float(checkpoint[2])
total_precision = float(checkpoint[3])
total_recall = float(checkpoint[4])


def anomaly_detection():
    import argparse
    import torch
    import pickle
    import preprocess_data
    from model import model
    from torch import optim
    from pathlib import Path
    from matplotlib import pyplot as plt
    import numpy as np
    from sklearn.svm import SVR
    from sklearn.model_selection import GridSearchCV
    from anomalyDetector import fit_norm_distribution_param
    from anomalyDetector import anomalyScore
    from anomalyDetector import get_precision_recall
    parser = argparse.ArgumentParser(
        description='PyTorch RNN Anomaly Detection Model')
    parser.add_argument('--prediction_window_size', type=int, default=1,
                        help='prediction_window_size')
    parser.add_argument('--data', type=str, default='ofdm',
                        help='type of the dataset (ecg, gesture, power_demand, space_shuttle, respiration, nyc_taxi, ofdm')
    parser.add_argument('--filename', type=str, default='NoiseSymbol.pkl',
                        help='filename of the dataset')
    parser.add_argument('--save_fig', '-s', action='store_true',
                        help='save results as figures')
    parser.add_argument('--compensate', action='store_true',
                        help='compensate anomaly score using anomaly score esimation')
    parser.add_argument('--beta', type=float, default=0.1,
                        help='beta value for f-beta score')

    args_ = parser.parse_args()
    print('-' * 120)
    # print("=> loading checkpoint ")
    checkpoint = torch.load(
        str(Path('save', args_.data, 'checkpoint', args_.filename).with_suffix('.pth')))
    args = checkpoint['args']
    args.prediction_window_size = args_.prediction_window_size
    args.beta = args_.beta
    args.save_fig = args_.save_fig
    args.compensate = args_.compensate
    # print("=> loaded checkpoint")

    # Set the random seed manually for reproducibility.
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed(args.seed)

    ###############################################################################
    # Load data
    ###############################################################################
    TimeseriesData = preprocess_data.PickleDataLoad(
        data_type=args.data, filename=args.filename, augment_test_data=False)
    train_dataset = TimeseriesData.batchify(
        args, TimeseriesData.trainData[:TimeseriesData.length], bsz=1)
    test_dataset = TimeseriesData.batchify(
        args, TimeseriesData.testData, bsz=1)

    ###############################################################################
    # Build the model
    ###############################################################################
    nfeatures = TimeseriesData.trainData.size(-1)
    model = model.RNNPredictor(rnn_type=args.model,
                               enc_inp_size=nfeatures,
                               rnn_inp_size=args.emsize,
                               rnn_hid_size=args.nhid,
                               dec_out_size=nfeatures,
                               nlayers=args.nlayers,
                               res_connection=args.res_connection).to(args.device)
    model.load_state_dict(checkpoint['state_dict'])
    # del checkpoint

    scores, predicted_scores, precisions, recalls, f_betas = list(
    ), list(), list(), list(), list()
    targets, mean_predictions, oneStep_predictions, Nstep_predictions = list(
    ), list(), list(), list()
    # For each channel in the dataset
    for channel_idx in range(nfeatures):
        ''' 1. Load mean and covariance if they are pre-calculated, if not calculate them. '''
        # Mean and covariance are calculated on train dataset.
        if 'means' in checkpoint.keys() and 'covs' in checkpoint.keys():
            # print('=> loading pre-calculated mean and covariance')
            mean, cov = checkpoint['means'][channel_idx], checkpoint['covs'][channel_idx]
        else:
            # print('=> calculating mean and covariance')
            mean, cov = fit_norm_distribution_param(
                args, model, train_dataset, channel_idx=channel_idx)

        ''' 2. Train anomaly score predictor using support vector regression (SVR). (Optional) '''
        # An anomaly score predictor is trained
        # given hidden layer output and the corresponding anomaly score on train dataset.
        # Predicted anomaly scores on test dataset can be used for the baseline of the adaptive threshold.
        if args.compensate:
            # print('=> training an SVR as anomaly score predictor')
            train_score, _, _, hiddens, _ = anomalyScore(
                args, model, train_dataset, mean, cov, channel_idx=channel_idx)
            score_predictor = GridSearchCV(SVR(), cv=5, param_grid={
                                           "C": [1e0, 1e1, 1e2], "gamma": np.logspace(-1, 1, 3)})
            score_predictor.fit(
                torch.cat(hiddens, dim=0).numpy(), train_score.cpu().numpy())
        else:
            score_predictor = None

        ''' 3. Calculate anomaly scores'''
        # Anomaly scores are calculated on the test dataset
        # given the mean and the covariance calculated on the train dataset
        # print('=> calculating anomaly scores')
        score, sorted_prediction, sorted_error, _, predicted_score = anomalyScore(args, model, test_dataset, mean, cov,
                                                                                  score_predictor=score_predictor,
                                                                                  channel_idx=channel_idx)

        ''' 4. Evaluate the result '''
        # The obtained anomaly scores are evaluated by measuring precision, recall, and f_beta scores
        # The precision, recall, f_beta scores are are calculated repeatedly,
        # sampling the threshold from 1 to the maximum anomaly score value, either equidistantly or logarithmically.
        # print('=> calculating precision, recall, and f_beta')
        precision, recall, f_beta, error_point, accuracy, threshold = get_precision_recall(mean, cov, sorted_error, args, score, num_samples=1000, beta=args.beta,
                                                                                           label=TimeseriesData.testLabel.to(args.device))
        # print('data: ', args.data, ' filename: ', args.filename,
        #       ' f-beta (no compensation): ', f_beta.max().item(), ' beta: ', args.beta)
        if args.compensate:
            precision, recall, f_beta = get_precision_recall(args, score, num_samples=1000, beta=args.beta,
                                                             label=TimeseriesData.testLabel.to(
                                                                 args.device),
                                                             predicted_score=predicted_score)
            # print('data: ', args.data, ' filename: ', args.filename,
            #       ' f-beta    (compensation): ', f_beta.max().item(), ' beta: ', args.beta)

        target = preprocess_data.reconstruct(test_dataset.cpu()[:, 0, channel_idx],
                                             TimeseriesData.mean[channel_idx],
                                             TimeseriesData.std[channel_idx]).numpy()
        mean_prediction = preprocess_data.reconstruct(sorted_prediction.mean(dim=1).cpu(),
                                                      TimeseriesData.mean[channel_idx],
                                                      TimeseriesData.std[channel_idx]).numpy()
        oneStep_prediction = preprocess_data.reconstruct(sorted_prediction[:, -1].cpu(),
                                                         TimeseriesData.mean[channel_idx],
                                                         TimeseriesData.std[channel_idx]).numpy()
        Nstep_prediction = preprocess_data.reconstruct(sorted_prediction[:, 0].cpu(),
                                                       TimeseriesData.mean[channel_idx],
                                                       TimeseriesData.std[channel_idx]).numpy()
        sorted_errors_mean = sorted_error.abs().mean(dim=1).cpu()
        sorted_errors_mean *= TimeseriesData.std[channel_idx]
        sorted_errors_mean = sorted_errors_mean.numpy()
        score = score.cpu()
        scores.append(score), targets.append(
            target), predicted_scores.append(predicted_score)
        mean_predictions.append(
            mean_prediction), oneStep_predictions.append(oneStep_prediction)
        Nstep_predictions.append(Nstep_prediction)
        precisions.append(precision), recalls.append(
            recall), f_betas.append(f_beta)

        if args.save_fig:
            save_dir = Path('result', args.data, args.filename).with_suffix(
                '').joinpath('fig_detection')
            save_dir.mkdir(parents=True, exist_ok=True)
            plt.plot(precision.cpu().numpy(), label='precision')
            plt.plot(recall.cpu().numpy(), label='recall')
            plt.plot(f_beta.cpu().numpy(), label='f1')
            plt.legend()
            plt.xlabel('Threshold (log scale)')
            plt.ylabel('Value')
            plt.title('Anomaly Detection on ' + args.data
                      + ' Dataset', fontsize=18, fontweight='bold')
            plt.savefig(str(save_dir.joinpath(
                'fig_f_beta_channel'+str(channel_idx)).with_suffix('.png')))
            plt.close()

            fig, ax1 = plt.subplots(figsize=(15, 5))
            ax1.plot(target, label='Target',
                     color='black',  marker='.', markersize=1, linewidth=0.7)
            # ax1.plot(mean_prediction, label='Mean predictions',
            #          color='purple', marker='.', linestyle='--', markersize=1, linewidth=0.5)
            # ax1.plot(oneStep_prediction, label='1-step predictions',
            #          color='green', marker='.', linestyle='--', markersize=1, linewidth=0.5)
            # ax1.plot(Nstep_prediction, label=str(args.prediction_window_size) + 'step predictions',
            #          color='blue', marker='.', linestyle='--', markersize=1, linewidth=0.5)
            # ax1.plot(sorted_errors_mean, label='Absolute mean prediction errors',
            #          color='orange', marker='.', linestyle='--', markersize=1, linewidth=1.0)
            ax1.legend(loc='upper left')
            ax1.set_ylabel('Value', fontsize=15)
            ax1.set_xlabel('Index', fontsize=15)
            ax2 = ax1.twinx()
            ax2.plot(score.numpy().reshape(-1, 1), label='Anomaly scores from \nmultivariate normal distribution',
                     color='red', marker='.', linestyle=':', markersize=1, linewidth=1)
            if args.compensate:
                ax2.plot(predicted_score, label='Predicted anomaly scores from SVR',
                         color='cyan', marker='.', linestyle='--', markersize=1, linewidth=1)
            # ax2.plot(score.numpy().reshape(-1, 1)/(predicted_score+1), label='Anomaly scores from \nmultivariate normal distribution',
            #          color='hotpink', marker='.', linestyle='--', markersize=1, linewidth=1)
            ax2.legend(loc='upper right')
            ax2.set_ylabel('anomaly score', fontsize=15)
            # plt.axvspan(344, 348, color='yellow', alpha=0.3)
            # plt.axvspan(486, 490, color='yellow', alpha=0.3)
            # plt.axvspan(546, 550, color='yellow', alpha=0.3)
            # plt.axvspan(957, 957, color='yellow', alpha=0.3)
            # plt.axvspan(1078, 1082, color='yellow', alpha=0.3)
            # plt.axvspan(1118, 1118, color='yellow', alpha=0.3)
            # plt.axvspan(1265, 1269, color='yellow', alpha=0.3)
            # plt.axvspan(1533, 1537, color='yellow', alpha=0.3)
            # plt.axvspan(1725, 1725, color='yellow', alpha=0.3)
            # plt.axvspan(1733, 1737, color='yellow', alpha=0.3)
            # plt.axvspan(1841, 1841, color='yellow', alpha=0.3)
            # plt.axvspan(1864, 1868, color='yellow', alpha=0.3)
            plt.title('Anomaly Detection on ' + args.data
                      + ' Dataset', fontsize=18, fontweight='bold')
            plt.tight_layout()
            plt.xlim([0, len(test_dataset)])
            plt.savefig(str(save_dir.joinpath(
                'fig_scores_channel'+str(channel_idx)).with_suffix('.png')))
            # plt.show()
            plt.close()

    # NoiseSymbol = np.loadtxt(Noise_Symbol_filepath)
    # true = np.loadtxt(Noise_Position_filepath, dtype=str)
    # np.savetxt('error_point.npy', error_point, fmt='%s')
    # error = np.loadtxt('error_point.npy', dtype=str)
    # true = true.tolist()
    # error = error.tolist()
    # lack_error = [x for x in error if x not in true]
    # extra_error = [x for x in true if x not in error]
    # total_error = lack_error + extra_error
    # detect_probability = 1 - (len(total_error)/len(NoiseSymbol))
    # print('=> saving the results as pickle extensions')
    print('-' * 120)
    print('Detect anomaly is on the', error_point)
    print('-' * 120)
    # print('Detect probability is', detect_probability)
    save_dir = Path('result', args.data, args.filename).with_suffix('')
    save_dir.mkdir(parents=True, exist_ok=True)
    pickle.dump(targets, open(str(save_dir.joinpath('target.pkl')), 'wb'))
    pickle.dump(mean_predictions, open(
        str(save_dir.joinpath('mean_predictions.pkl')), 'wb'))
    pickle.dump(oneStep_predictions, open(
        str(save_dir.joinpath('oneStep_predictions.pkl')), 'wb'))
    pickle.dump(Nstep_predictions, open(
        str(save_dir.joinpath('Nstep_predictions.pkl')), 'wb'))
    pickle.dump(scores, open(str(save_dir.joinpath('score.pkl')), 'wb'))
    pickle.dump(predicted_scores, open(
        str(save_dir.joinpath('predicted_scores.pkl')), 'wb'))
    pickle.dump(precisions, open(
        str(save_dir.joinpath('precision.pkl')), 'wb'))
    pickle.dump(recalls, open(str(save_dir.joinpath('recall.pkl')), 'wb'))
    pickle.dump(f_betas, open(str(save_dir.joinpath('f_beta.pkl')), 'wb'))
    precision = precision.cpu().data.numpy().tolist()
    recall = recall.cpu().data.numpy().tolist()
    f_beta = f_beta.cpu().data.numpy().tolist()
    precision = precision[f_beta.index(threshold):]
    recall = recall[f_beta.index(threshold):]
    f_beta = f_beta[f_beta.index(threshold):]
    precision = np.asarray(precision).mean()
    recall = np.asarray(recall).mean()
    f_beta = np.asarray(f_beta).mean()
    return accuracy.max().item(), f_beta, precision, recall


def generate_dataset():
    import requests
    from pathlib import Path
    import pickle
    from shutil import unpack_archive
    import numpy as np
    urls = dict()
    urls['ofdm'] = []
    NoisePosition = np.loadtxt(Noise_Position_filepath, dtype=str)
    k = 0
    for dataname in urls:
        raw_dir = Path('dataset', dataname, 'raw')
        raw_dir.mkdir(parents=True, exist_ok=True)
        for url in urls[dataname]:
            filename = raw_dir.joinpath(Path(url).name)
            # print('Downloading', url)
            resp = requests.get(url)
            filename.write_bytes(resp.content)
            if filename.suffix == '':
                filename.rename(filename.with_suffix('.txt'))
            # print('Saving to', filename.with_suffix('.txt'))
            if filename.suffix == '.zip':
                # print('Extracting to', filename)
                unpack_archive(str(filename), extract_dir=str(raw_dir))

        for filepath in raw_dir.glob('*.txt'):
            with open(str(filepath)) as f:
                # Label anomaly points as 1 in the dataset
                labeled_data = []
                for i, line in enumerate(f):
                    tokens = [float(token) for token in line.split()]
                    if filepath.name == 'NoiseSymbol.txt':
                        if i == int(NoisePosition[k])-1:
                            tokens.append(1.0)
                            if k < len(NoisePosition)-1:
                                k += 1
                        else:
                            tokens.append(0.0)
                    labeled_data.append(tokens)
                np.savetxt('label_data.txt', labeled_data)

                # Save the labeled dataset as .pkl extension
                labeled_whole_dir = raw_dir.parent.joinpath('labeled', 'whole')
                labeled_whole_dir.mkdir(parents=True, exist_ok=True)
                with open(str(labeled_whole_dir.joinpath(filepath.name).with_suffix('.pkl')), 'wb') as pkl:
                    pickle.dump(labeled_data, pkl)

                # Divide the labeled dataset into trainset and testset, then save them
                labeled_train_dir = raw_dir.parent.joinpath('labeled', 'train')
                labeled_train_dir.mkdir(parents=True, exist_ok=True)
                labeled_test_dir = raw_dir.parent.joinpath('labeled', 'test')
                labeled_test_dir.mkdir(parents=True, exist_ok=True)
                if filepath.name == 'NoiseSymbol.txt':
                    # with open(str(labeled_train_dir.joinpath(filepath.name).with_suffix('.pkl')), 'wb') as pkl:
                    #     pickle.dump(labeled_data[1000:], pkl)
                    with open(str(labeled_test_dir.joinpath(filepath.name).with_suffix('.pkl')), 'wb') as pkl:
                        pickle.dump(labeled_data, pkl)


def Modulation(bits):
    # for i in range(*bits.shape):
    # This is just for QAM modulation
    bit_r = bits.reshape((int(len(bits) / mu), mu))
    return (2 * bit_r[:, 0] - 1) + 1j * (2 * bit_r[:, 1] - 1)


def IDFT(OFDM_data):
    return np.fft.ifft(OFDM_data)   # np.fft.ifft(OFDM_data)*np.sqrt(K)  (lJS)


def addCP(OFDM_time):
    cp = OFDM_time[-CP:]  # take the last CP samples ...
    return np.hstack([cp, OFDM_time])  # ... and add them to the beginning


# construct the another version is including impulse noise(LJS)
def channel_BG(signal, channelResponse, SNRdb):
    # Bernoulli-Gaussian channel          # lJS
    # IGR = 50  # impulse gaussian ratio
    # prob = 0.005  # prob
    prob = np.random.uniform(0.001, 0.01)
    convolved = np.convolve(signal, channelResponse)
    signal_power = np.mean(abs(convolved**2))
    sigma2 = signal_power * 10**(-SNRdb / 10)      # (signal_power/2)  (LJS)
    # sigma3 = sigma2 * IGR
    # sigma3 = 15
    sigma3 = np.random.uniform(13, 17)
    Gaussian = np.random.randn(*convolved.shape) + 1j * \
        np.random.randn(*convolved.shape)
    power1 = np.zeros([*convolved.shape])
    power2 = np.zeros([*convolved.shape])
    noise_position = []
    noise_position_res = []
    # print('Channel Length :', len(channelResponse))
    # print('Bits Length :', len(convolved))
    # print('IGR :', IGR)
    # print('Signal Power :', signal_power)
    # print('AWGN Power :', sigma2)
    # print('Impulse Power :', sigma3)
    # print('SNR:', SNRdb)
    # print('Impulse Probability :', prob*100, '%')
    for i in range(*convolved.shape):
        k = np.random.rand()
        if k > prob:
            power1[i] = np.sqrt(sigma2 / 2)
            power2[i] = np.sqrt(sigma2 / 2)
    for i in range(*convolved.shape):
        k = np.random.rand()
        n = np.random.binomial(n=1, p=0.5)
        if k <= prob:
            if n == 1:
                power1[i] = np.sqrt(sigma3 / 2)
                power2[i] = np.sqrt(sigma3 / 2)
                # print('impulse_position_single =', i + 1)
                j = i + 1
                # position = 'single ' + str(j)
                position = str(j)
                noise_position.append(position)
            else:
                if i > 1:
                    if (i+5) < 1071:
                        power1[i] = np.sqrt(sigma3 / 2)
                        power2[i] = np.sqrt(sigma3 / 2)
                        power1[i+1] = np.sqrt(sigma3 / 2)
                        power2[i+1] = np.sqrt(sigma3 / 2)
                        power1[i+2] = np.sqrt(sigma3 / 2)
                        power2[i+2] = np.sqrt(sigma3 / 2)
                        power1[i+3] = np.sqrt(sigma3 / 2)
                        power2[i+3] = np.sqrt(sigma3 / 2)
                        power1[i+4] = np.sqrt(sigma3 / 2)
                        power2[i+4] = np.sqrt(sigma3 / 2)
                        # print('impulse_position_mutiple =', i + 1)
                        j = i + 1
                        # position = 'mutiple ' + str(j)
                        for m in range(5):
                            position = str(j)
                            j += 1
                            noise_position.append(position)
    [noise_position_res.append(x)
     for x in noise_position if x not in noise_position_res]
    # print('Real anomaly is on the', noise_position)
    noise1 = np.multiply(power1, Gaussian.real)
    noise2 = np.multiply(power2, Gaussian.imag)
    noise_BG = np.zeros([*convolved.shape]).astype(complex)
    noise_BG.real = noise1
    noise_BG.imag = noise2
    noise_symbol = noise_BG + convolved     # NoiseSymbol
    noise_symbol_real = noise_symbol.real
    noise_symbol_image = noise_symbol.imag
    noise_symbol = []
    for i in range(0, len(convolved)):
        noise_symbol.append(
            np.sqrt((noise_symbol_image[i]**2)+(noise_symbol_real[i]**2)))
    noise_symbol = np.array(noise_symbol)
    # np.savetxt('Noise.txt', noise_BG)
    # np.savetxt('NoiseReal.txt', noise_BG.real)
    # np.savetxt('NoiseImag.txt', noise_BG.imag)
    # np.savetxt('NoiseSymbolReal.txt', noise_BG.real + convolved.real)
    # np.savetxt('NoiseSymbolImag.txt', noise_BG.imag + convolved.imag)
    np.savetxt(Noise_Symbol_filepath, noise_symbol)
    np.savetxt(Noise_Position_filepath, noise_position_res, fmt="%s")
    return noise_position_res


def ofdm_simulate_BG(codeword, channelResponse, SNRdb):       # LJS
    # OFDM_data = np.zeros(K, dtype=complex)
    # OFDM_data[allCarriers] = pilotValue
    # OFDM_time = IDFT(OFDM_data)
    # OFDM_withCP = addCP(OFDM_time)
    # OFDM_TX = OFDM_withCP
    # OFDM_RX = channel_BG(OFDM_TX, channelResponse, SNRdb)
    # OFDM_RX_noCP = removeCP(OFDM_RX)
    # ----- target inputs ---
    symbol = np.zeros(K, dtype=complex)
    codeword_qam = Modulation(codeword)
    symbol[np.arange(K)] = codeword_qam
    OFDM_data_codeword = symbol
    OFDM_time_codeword = np.fft.ifft(OFDM_data_codeword) * np.sqrt(K)
    OFDM_withCP_cordword = addCP(OFDM_time_codeword)
    # np.savetxt('PreSymbol.txt', OFDM_data_codeword)
    # np.savetxt('Symbol.txt', OFDM_withCP_cordword)
    # np.savetxt('SymbolReal.txt', OFDM_withCP_cordword.real)
    # np.savetxt('SymbolImag.txt', OFDM_withCP_cordword.imag)
    datacheck = channel_BG(OFDM_withCP_cordword, channelResponse, SNRdb)
    return datacheck


H_folder_test = '../RNN-Time-series-Anomaly-Detection-master/test/'
test_idx_low = 301
test_idx_high = 401
channel_response_set_test = []
for test_idx in range(test_idx_low, test_idx_high):
    # print("Processing the train", train_idx, "th document")
    H_file = H_folder_test + str(test_idx) + '.txt'
    with open(H_file) as f:
        for line in f:
            numbers_str = line.split()
            # np.shape(numbers_str)=32 x 1
            numbers_float = [float(x) for x in numbers_str]
            # np.shape(numbers_float)=32 x 1
            h_response = np.asarray(numbers_float[0:int(len(numbers_float) / 2)]) +\
                1j * \
                np.asarray(
                    numbers_float[int(len(numbers_float) / 2):len(numbers_float)])
            channel_response_set_test.append(h_response)

for x in range(1000-valid_epochs):
    for index_k in range(0, 1):
        bits = np.random.binomial(n=1, p=0.5, size=(payloadBits_per_OFDM, ))
        # print(bits)
        # ofdm_simulate_BG(bits, SNRdb)
        channel_response = channel_response_set_test[np.random.randint(
            0, len(channel_response_set_test))]
        checkpoint = []
        datacheck = ofdm_simulate_BG(bits, channel_response, SNRdb)
        if len(datacheck) <= 1:
            continue
        generate_dataset()
        accuracy, fbeta, precision, recall = anomaly_detection()
        total_accuracy += accuracy
        total_fbeta += fbeta
        total_precision += precision
        total_recall += recall
        valid_epochs += 1
        avg_accuracy = (total_accuracy/valid_epochs)*100
        avg_fbeta = (total_fbeta/valid_epochs)*100
        avg_precision = (total_precision/valid_epochs)*100
        avg_recall = (total_recall/valid_epochs)*100
        checkpoint.extend(
            [valid_epochs, total_accuracy, total_fbeta, total_precision, total_recall])
        np.savetxt('checkpoint.txt', checkpoint)
        print('Ac:', accuracy, ' F-beta:',
              fbeta, ' Pr:', precision, ' Rc:', recall)
        print('-' * 120)
        print('epoch ' + str(valid_epochs) + '\navg.accuracy = ' + str(avg_accuracy) + ' %\navg.f-beta = '
              + str(avg_fbeta) + ' %\navg.precision = ' + str(avg_precision) + ' %\navg.recall = ' + str(avg_recall) + ' %')

if valid_epochs == 1000:
    os.remove('checkpoint.txt')
