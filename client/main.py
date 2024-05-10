import time
import module.readarg as readarg
import gbn_receiver as gbn_receiver
import sr_receiver as sr_receiver
import pickle


class Package:
    def __init__(self, seq, data):
        self.seq = seq  # 序号
        self.data = data  # 数据


protocol, window_size, timeout, filename = readarg.readArg()

start_time = time.perf_counter()
if protocol == 'GBN':
    file_size=gbn_receiver.gbn_rec(window_size, timeout, filename)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")
    print(f"Received data: {file_size/1048576} MB")
elif protocol == 'SR':
    file_size=sr_receiver.sr_rec(window_size, timeout, filename)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")
    print(f"Received data: {file_size/1048576} bytes")

else:
    print(protocol, window_size, timeout)