import module.readarg as readarg
import gbn_receiver as gbn_receiver
import sr_receiver as sr_receiver
import pickle


class Package:
    def __init__(self, seq, data):
        self.seq = seq  # 序号
        self.data = data  # 数据


protocol, window_size, timeout, filename = readarg.readArg()

if protocol == 'GBN':
    gbn_receiver.gbn_rec(window_size, timeout, filename)
elif protocol == 'SR':
    sr_receiver.sr_rec(window_size, timeout, filename)

else:
    print(protocol, window_size, timeout)