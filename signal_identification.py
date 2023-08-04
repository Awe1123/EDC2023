# # 导入所需的库，例如numpy
# import numpy as np

# def identify_signal(preprocessed_signal):
#     """
#     识别预处理过的信号的类型。

#     参数:
#         preprocessed_signal (np.array): 预处理过的信号。

#     返回:
#         signal_type (str): 信号的类型，例如'AM', 'FM', 'CW', '2ASK', '2PSK', '2FSK'。
#     """

#     if np.max(preprocessed_signal) > 0.5:
#         signal_type = 'AM'
#     else:
#         signal_type = 'Unknown'

#     return signal_type


import numpy as np
from scipy.signal import hilbert, fftconvolve
from scipy.fftpack import fft, fftfreq
import matplotlib.pyplot as plt


# def is_cw(preprocessed_signal, fs=8e6, carrier_freq=2e6, threshold=0.999995):
#     """
#     该函数用于识别信号是否为单纯的正弦载波信号。
    
#     参数:
#     preprocessed_signal (numpy array): 预处理后的信号
#     fs (float): 采样频率，默认为8e6 (8MHz)
#     carrier_freq (float): 载波频率，默认为2e6 (2MHz)
#     threshold (float): 判断阈值，默认为0.05，若频谱中除载波频率外其他频率分量的能量占总能量比例超过该值，则判断为调制信号

#     返回:
#     bool: 如果信号为单纯的正弦载波信号，则返回True；如果信号被调制，则返回False
#     """
#     # 计算FFT以转换到频域
#     signal_fft = fft(preprocessed_signal)
    
#     # 计算频率
#     freq = fftfreq(len(signal_fft), 1/fs)
    
#     # 取得正频率部分
#     signal_fft = signal_fft[freq >= 0]
#     freq = freq[freq >= 0]
    
#     # 找到载波频率在频率数组中的索引
#     idx = np.abs(freq - carrier_freq).argmin()
    
#     # 计算总能量
#     total_energy = np.sum(np.abs(signal_fft)**2)
    
#     # 计算载波能量
#     carrier_energy = np.abs(signal_fft[idx])**2
    
#     # 计算除载波外的能量
#     other_energy = total_energy - carrier_energy
    
#     test_point=other_energy / total_energy
#     print("test_point=",test_point)
    
#     # 如果除载波外的能量占总能量的比例超过阈值，则认为信号被调制了
#     if other_energy / total_energy < threshold:
#         return False
#     else:
#         return True

# def is_cw(preprocessed_signal, fs=8e6, carrier_freq=2e6, threshold=0.05):
#     """
#     判断输入的信号是否为单一载波信号。
#     参数：
#         preprocessed_signal: ndarray，需要判断的信号。
#         fs: float，采样频率，单位Hz。
#         carrier_freq: float，载波频率，单位Hz。
#         threshold: float，频率差的阈值，用于判断是否存在调制。
#     返回值：
#         bool，如果输入的信号是单一载波信号，返回True，否则返回False。
#     """
#     from scipy import signal
#     # 载波周期
#     carrier_period = 1.0 / carrier_freq

#     # 计算每一段的长度
#     segment_length = int(fs * carrier_period)

#     for i in range(0, len(preprocessed_signal), segment_length):
#         segment = preprocessed_signal[i:i+segment_length]

#         # 计算每一段的周期图
#         periodogram = signal.periodogram(segment, fs)

#         # 检查是否有其它频率分量
#         freqs, pwr = periodogram
#         max_pwr_idx = np.argmax(pwr)
#         max_freq = freqs[max_pwr_idx]
        
#         test_point=max_freq - carrier_freq
#         print("test_point=",test_point)
        
#         if abs(max_freq - carrier_freq) > threshold:
#             # 如果最大功率的频率与载波频率的差大于阈值，那么认为存在调制
#             return False

#     return True



def is_cw(preprocessed_signal, fs=8e6, carrier_freq=2e6, threshold=0.04):
    """
    判断输入的信号是否为单一载波信号。
    参数：
        preprocessed_signal: ndarray，需要判断的信号。
        fs: float，采样频率，单位Hz。
        carrier_freq: float，载波频率，单位Hz。
        threshold: float，用于判断是否存在调制的阈值。
    返回值：
        bool，如果输入的信号是单一载波信号，返回True，否则返回False。
    """
    import numpy as np
    from scipy.signal import hilbert
    
    # 计算希尔伯特变换
    analytic_signal = hilbert(preprocessed_signal)
    
    # 计算相位
    phase = np.unwrap(np.angle(analytic_signal))
    
    # 计算相位差
    phase_diff = np.diff(phase)
    
    # 对于一个单一载波信号，相位差应该是恒定的，我们可以通过检查相位差的标准差来看是否存在调制
    phase_diff_std = np.std(phase_diff)

    print("phase_diff_std:",phase_diff_std)
    
    if phase_diff_std > threshold:
        return False

    return True

def identify_signal(preprocessed_signal, window_size=1000):

    # 首先检查信号是经过调制的信号还是单纯的载波信号
    if is_cw(preprocessed_signal):
        return 'CW'
    
    #如果经过了调制运行下面的代码:

    # 计算解析信号（希尔伯特变换）
    analytic_signal = hilbert(preprocessed_signal)
    # 计算幅度包络和瞬时相位
    amplitude_envelope = np.abs(analytic_signal)
    instantaneous_phase = np.unwrap(np.angle(analytic_signal))

    # 计算瞬时频率（相位的导数）
    instantaneous_frequency = (np.diff(instantaneous_phase) / (2.0 * np.pi)) * 8e6

    # 计算信号的FFT
    yf = fft(preprocessed_signal)
    xf = fftfreq(len(preprocessed_signal), 1 / 8e6)

    # 计算幅度频谱
    # amplitude_spectrum = 2.0 / len(preprocessed_signal) * np.abs(yf[:len(preprocessed_signal)//2])

    # 计算幅度包络的滑动窗口变化率
    amplitude_envelope_diff = np.std(fftconvolve(amplitude_envelope, np.ones(window_size), 'valid') / window_size)

    print('amplitude_envelope_diff:',amplitude_envelope_diff)
    print('np.mean(np.abs(instantaneous_frequency)):',np.mean(np.abs(instantaneous_frequency)))
    
    # 检查信号是AM还是FM
    # if amplitude_envelope_diff > 0.001 and np.mean(np.abs(instantaneous_frequency)) < 2e6:
    if amplitude_envelope_diff > 0.001 and np.mean(np.abs(instantaneous_frequency)) >= 1.8e6:
        # print('信号是幅度调制（AM）。')
        signal_type='AM'
    elif amplitude_envelope_diff <= 0.001 and np.mean(np.abs(instantaneous_frequency)) >= 2e6:
        # print('信号是频率调制（FM）。')
        signal_type='FM'
    elif np.mean(np.abs(instantaneous_frequency)) <= 1.8e6:
        signal_type='2ASK'
    else:
        # print('信号不能明确地对应AM或FM调制。')
        signal_type='unknown'
    return signal_type

if __name__=="__main__":
    data=np.loadtxt('data-am.dat')
    print(identify_signal(data))
    data=np.loadtxt('data-fm.dat')
    print(identify_signal(data))
