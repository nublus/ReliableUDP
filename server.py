import socket
import time
import random
import pickle
import threading
import logging

SERVERPORT = 12000
TIMEOUT = 5
packet_size = 1024
window_size = 4
next_seqnum = -1
base = -1
loss_rate = 0.05
timer = None
timer_running = False
receive_complete = False 

logger = logging.getLogger(__name__)
logging.basicConfig(filename='sender.log', level=logging.DEBUG)
class Package:
    def __init__(self, seq, data):
        self.seq = seq  # 序号
        self.data = data  # 数据

def startTimer():
    global timer_running
    if timer_running == True:
        logger.debug("Timer restart from startTimer")
        stopTimer()
    timer_running = True
    global timer
    timer = threading.Timer(TIMEOUT, handleTimeout)
    timer.start()
    logger.debug('Timer started')
    return timer


def stopTimer():
    global timer_running, timer
    if timer is not None:
        timer_running = False
        timer.cancel()
        logger.debug("Timer cancelled.")


def handleTimeout():
    global timer_running
    if timer_running:
        logger.debug("Timeout occurred!!!")
        # 处理超时逻辑，重新启动starttimer，重传数据包
        stopTimer()
        startTimer()
        global base, next_seqnum, packages
        for i in range(base, next_seqnum):
            serialized_package = pickle.dumps(packages[i])
            # 也有可能丢包
            if random.random() >= loss_rate:
                server_socket.sendto(serialized_package, client_address)
                logger.debug(f"Retransmitted packet {packages[i].seq}")
            else:
                logger.debug(f"Retransmitted Loss packet {packages[i].seq}")
            time.sleep(1)


def initWindow(size):
    global window_size, base, next_seqnum
    window_size = size
    base = 0
    next_seqnum = 0

def makePackage(filename, packet_size):
    # 将文件打包成大小为packet_size的Package数组，并为其打上序号
    global packages
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

def send_packets(server_socket, client_address, packages):
    global next_seqnum, base, window_size
    for i in range(len(packages)):
        # 发送窗口未满
        if next_seqnum - base < window_size:
            serialized_package = pickle.dumps(packages[i])

            # 模拟数据包丢失
            if random.random() >= loss_rate:
                server_socket.sendto(serialized_package, client_address)
                logger.debug(f"Sent packet {packages[i].seq}")
            else:
                logger.debug(f"Loss packet {packages[i].seq}")
            
            time.sleep(1)  # 模拟发送数据包的延迟
            if base == next_seqnum:
                # 开始计时，timeout时间内如果没有收到客户端ack，触发timeout，重新发送base - (nextseq - 1)
                startTimer()
            next_seqnum += 1

        else:
            print("sending window full, try again 3s later")
            logger.debug("sending window full, try again 3s later")
            time.sleep(3)
            i = i-1

    end_package = Package(seq = -1, data=b'')
    serialized_end_package = pickle.dumps(end_package)
    server_socket.sendto(serialized_end_package, client_address)
    print("File transfer completed.")
    logger.debug("File transfer completed.")
    return



def receive_ack(server_socket):
    global base, next_seqnum
    while True:
        ack, _ = server_socket.recvfrom(1024)
        print("recv!!!")
        if ack.decode() == '-1':
            stopTimer()
            return
        
        base = int(ack.decode()) + 1
        print(base)
        logger.debug(f"Received ack:  {ack.decode()}")
        if base == next_seqnum:
            logger.debug(f'所有发送的报文均已被收到，停止发送 base: {base}, next_seqnum: {next_seqnum}')
            stopTimer()
        else:
            # 重启计时器
            timer = startTimer()
def main():
    global base, next_seqnum, window_size
    global server_socket, client_address, timer
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', SERVERPORT))
    print("ready to rcv")

    message, client_address = server_socket.recvfrom(1024)
    file_name = message.decode()
    # 将文件打包成packet_size大小的数组，用于后续udp传输
    print(f"File name: {file_name}")
    initWindow(window_size)
    packages = makePackage(file_name, packet_size)

    # 创建发送数据报线程
    send_thread = threading.Thread(target=send_packets, args=(server_socket, client_address, packages))
    send_thread.start()
    receive_thread = threading.Thread(target=receive_ack, args=(server_socket,))
    receive_thread.start()


    send_thread.join()
    receive_thread.join()
    
 
if __name__ == "__main__":
    main()
