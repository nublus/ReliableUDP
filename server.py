import socket
import time
import random
import pickle

SERVERPORT = 12000
# 定义数据包大小和窗口大小
packet_size = 1024
window_size = 4
next_seqnum = -1
base = -1
# 模拟数据包丢失率，这里设定为20%
loss_rate = 0.2

class Package:
    def __init__(self, seq, data):
        self.seq = seq  # 序号
        self.data = data  # 数据
    
    # def __incode__(self):
    #     self.seq = self.seq.encode('UTF-8')

def initWindow(size):
    global window_size, base, next_seqnum
    window_size = size
    base = 0
    next_seqnum = 0

def makePackage(filename, packet_size):
    # 将文件打包成大小为packet_size的Package数组，并为其打上序号
    packages = []
    seq_num = 0
    with open(filename, 'rb') as f:
        while True:
            data = f.read(packet_size)
            if not data:
                break
            packages.append(Package(seq=seq_num, data=data))
            seq_num += 1
    return packages


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', SERVERPORT))
    print("ready to rcv")
    message, client_address = server_socket.recvfrom(1024)
    file_name = message.decode()
    # 将文件打包成packet_size大小的数组，用于后续udp传输
    print(file_name)
    # initWindow(window_size)
    packages = makePackage(file_name, packet_size)
    
    # while True:
    for package in packages:
        serialized_package = pickle.dumps(package)
        server_socket.sendto(serialized_package, client_address)
        
        


        # # 模拟丢包
        # if loss_rate > 0 and random.random() < loss_rate:
        #     print(f"Packet {sequence_num} lost")
        #     continue
    
    end_package = Package(seq=-1, data=b'')
    serialized_end_package = pickle.dumps(end_package)
    server_socket.sendto(serialized_end_package, client_address)
    print("File transfer completed.")
 
if __name__ == "__main__":
    main()
