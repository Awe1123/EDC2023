# 导入必要的库，例如 numpy
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert,butter,filtfilt
import my_filter
import json

max_frequency_deviation=0

def am_demodulation(modulated_wave):
    # 使用希尔伯特转换找到解析信号
    analytic_signal = hilbert(modulated_wave)
    # 计算解析信号的绝对值，得到解调信号
    envelope = np.abs(analytic_signal)

    return envelope

def fm_demodulation(data):
    fc=2e6
    fs=8e6
    global max_frequency_deviation
    t = np.arange(len(data)) / fs

    # 使用希尔伯特变换得到解析信号
    analytic_signal = hilbert(data)

    # 计算相位，然后对其进行解包
    instantaneous_phase = np.unwrap(np.angle(analytic_signal))

    filtered_phase = my_filter.phase_filter(instantaneous_phase)  # 对相位进行低通滤波

    # 对滤波后的相位进行差分，并考虑采样时间得到频率偏移
    frequency_deviation = np.diff(filtered_phase) / (2.0*np.pi) * fs
    # 对相位进行差分，并考虑采样时间得到频率偏移
    # frequency_deviation = np.diff(instantaneous_phase) / (2.0*np.pi) * 8e6
        
    # # 计算最大频偏
    # max_frequency_deviation = np.max(np.abs(frequency_deviation[200:-199]))
    max_frequency_deviation = np.max(np.abs((frequency_deviation - np.mean(frequency_deviation))[200:-199]))
    
    max_frequency_deviation=0.00094897*max_frequency_deviation+-919.26156234
    
    params={}
    params["DFmax"]=max_frequency_deviation

    # plt.plot(frequency_deviation)
    # plt.savefig('max_frequency_deviation.png')
    frequency_deviation=np.append(frequency_deviation,frequency_deviation[-1])
    
    # FM信号的载波频率为2MHz，得到基带信号
    baseband = frequency_deviation - 2e6
    
    baseband=baseband/np.max(baseband[2000:6000])
    
    
    with open('parameter.json','w',encoding='UTF-8') as f:
        f.write(json.dumps(params))
    np.savetxt('frequency_deviation.dat',frequency_deviation)
    
    return baseband

# def psk_demodulation(modulated_wave):
#     import scipy.signal as signal
#     # 定义采样率和载波频率
#     fs = 8e6
#     fc = 2e6

#     # 定义载波时间
#     time = np.arange(8000)/fs
    
#     # 生成载波
#     carrier = np.sin(2 * np.pi * fc * time)
    
#     # 乘法混频
#     product = modulated_wave * carrier

#     plt.plot(product)
#     plt.title('product')
#     plt.show()
#     # 定义低通滤波器的截止频率为码速率的上限，这里取10kHz
#     cutoff_freq = 10e3
    
#     # 定义滤波器的滤波器阶数，根据经验，选择一个较小的值，例如10
#     numtaps = 10
    
#     # 使用firwin函数设计低通滤波器
#     fir_coeff = signal.firwin(numtaps, cutoff=cutoff_freq, fs=fs)
    
#     # 使用lfilter函数对信号进行滤波
#     demodulated_wave = signal.lfilter(fir_coeff, 1.0, product)
    
#     # 因为2PSK信号的值在0和1之间，我们可以使用0.5作为阈值进行判决
#     demodulated_wave = np.where(demodulated_wave > 0.5, 1, 0)
    
#     return demodulated_wave

def psk_demodulation(modulated_wave):
    import scipy.signal as signal
    # 声明采样率，载波频率，可能的码速率
    sampling_rate = 8000000
    carrier_freq = 2000000
    symbol_rates = [6000, 8000, 10000]

    # 构建同相位载波
    t = np.arange(8000) / sampling_rate
    carrier = np.cos(2 * np.pi * carrier_freq * t)

    # 将同相位载波与调制信号相乘
    multiplied = modulated_wave * carrier

    # 对于所有可能的码速率，计算自相关函数
    autocorrelations = [np.correlate(multiplied, np.roll(multiplied, -int(sampling_rate/rate)), 'valid')
                        for rate in symbol_rates]

    # 找出哪个自相关函数的峰值最大
    symbol_rate_index = np.argmax([np.max(auto) for auto in autocorrelations])

    # 确定正确的码速率
    correct_rate = symbol_rates[symbol_rate_index]

    # 低通滤波以抑制二倍频率的成分
    b, a = signal.butter(5, correct_rate*1.2/(sampling_rate/2), 'low')
    demodulated_wave = signal.lfilter(b, a, multiplied)

    # 将连续的解调波形转换为离散的方波
    square_wave = np.sign(demodulated_wave)

    return square_wave

def demodulate_signal(signal_type, preprocessed_signal):
    """
    根据预处理过的信号和它的类型解调信号。

    参数:
        signal_type (str): 信号的类型，例如 'AM', 'FM', 'CW', '2ASK', '2PSK', '2FSK'。
        preprocessed_signal (np.array): 预处理过的信号。

    返回:
        demodulated_signal (np.array): 解调后的信号。
    """
    # 初始化一个空的 numpy array 来保存解调后的信号
    demodulated_signal = np.array([])

    # 根据信号的类型来解调信号。
    # 这可能涉及到复杂的信号处理和机器学习技术，
    # 这些技术超出了这个例子的范围。

    if signal_type == 'AM' or signal_type == '2ASK':

        demodulated_signal = am_demodulation(preprocessed_signal)
        filted_signal = my_filter.AM_filter_after(demodulated_signal)
        filted_signal[:139] = filted_signal[139]
        filted_signal[-140:] = filted_signal[-140]
        return filted_signal
        

    elif signal_type == 'FMor2FSK':
        # 对于 'FM' 信号，我们可能需要进行更复杂的解调过程
        # 这可能需要通过傅里叶变换或其他频率分析技术来实现
        # 这里我们只是用一个占位符来代替真实的解调信号
        demodulated_signal = fm_demodulation(preprocessed_signal)
        # filted_signal = my_filter.FM_filter_after(demodulated_signal)
        filted_signal=demodulated_signal
        filted_signal[:139] = filted_signal[139]
        filted_signal[-140:] = filted_signal[-140]
        return filted_signal
    # 以此类推，对于其他类型的信号，我们也可以添加相应的解调代码...
    elif signal_type=='2PSK':
        demodulated_signal = psk_demodulation(preprocessed_signal)
        # filted_signal = my_filter.FM_filter_after(demodulated_signal)
        filted_signal=demodulated_signal
        filted_signal[:139] = filted_signal[139]
        filted_signal[-140:] = filted_signal[-140]
        return filted_signal        
    return demodulated_signal

if __name__=="__main__":
    data=np.loadtxt('data-test.dat')
    filterd_data=my_filter.pre_filter(data)
    result=demodulate_signal('2PSK',filterd_data)
    # print("设置:5K")
    print('max_frequency_deviation:',max_frequency_deviation)
    plt.plot(result)
    plt.show()
    plt.savefig('test-signal-demodulation.png')
    import test_plot
 


