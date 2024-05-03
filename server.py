import socket
import time
import random
import pickle
import threading
import logging

SERVERPORT = 12000
TIMEOUT = 3
packet_size = 1024
window_size = 4
next_seqnum = -1
base = -1
loss_rate = 0.2
timer = None
timer_running = False
receive_complete = False 

logger = logging.getLogger(__name__)
logging.basicConfig(filename='sender.log', level=logging.DEBUG, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
class Package:
    def __init__(self, seq, data):
        self.seq = seq  # 序号
        self.data = data  # 数据

def startTimer():
    global timer_running
    if timer_running == True:
        # logger.info("Timer restart from startTimer")
        stopTimer()
    timer_running = True
    global timer
    timer = threading.Timer(TIMEOUT, handleTimeout)
    timer.start()
    # logger.info('Timer started')
    return timer


def stopTimer():
    global timer_running, timer
    if timer is not None:
        timer_running = False
        timer.cancel()
        # logger.debug("Timer cancelled.")


def handleTimeout():
    global timer_running
    global base, next_seqnum, packages
    if timer_running:
        logger.error(f"Timeout occurred!!! Base: {base}, nextseq: {next_seqnum}")
        # 处理超时逻辑，重新启动starttimer，重传数据包
        stopTimer()
        startTimer()
        
        for i in range(base, next_seqnum):
            serialized_package = pickle.dumps(packages[i])
            # 也有可能丢包
            if random.random() >= loss_rate:
                server_socket.sendto(serialized_package, client_address)
                logger.warning(f"Retransmitted packet {packages[i].seq}")
            else:
                logger.error(f"Loss Retransmitted packet {packages[i].seq}")
            time.sleep(0.3)


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
    lenth = len(packages)
    print(f'package lenth: {lenth}')
    #  for i in range(len(packages)):
    while True:
        # 发送窗口未满
        if next_seqnum == lenth:
            break
        if next_seqnum - base < window_size and next_seqnum < lenth:
            serialized_package = pickle.dumps(packages[next_seqnum])

            # 模拟数据包丢失
            if random.random() >= loss_rate:
                server_socket.sendto(serialized_package, client_address)
                logger.debug(f"Sent packet {packages[next_seqnum].seq}, Base:{base}, nextseq: {next_seqnum}")
            else:
                logger.error(f"Loss packet {packages[next_seqnum].seq}, Base:{base}, nextseq: {next_seqnum}")
            
            time.sleep(1)  # 模拟发送数据包的延迟
            if base == next_seqnum:
                # 开始计时，timeout时间内如果没有收到客户端ack，触发timeout，重新发送base - (nextseq - 1)
                startTimer()
                # logger.debug(f"for the base equal to nextseq: {base}, nextseq: {next_seqnum}")
            next_seqnum += 1

        else:
            print("sending window full, try again 4s later")
            logger.warning(f"sending window full, base: {base}, nextseq: {next_seqnum}")
            time.sleep(4)
            if next_seqnum != base: # 如果超时重传未能将窗口处理好，则重新发送base-nextseq
                next_seqnum = base # 避免一但产生丢包，就只能靠超时重传
                logger.warning('Reset Window')
            
            
    for i in range(lenth-4, lenth):
        serialized_package = pickle.dumps(packages[i])
        server_socket.sendto(serialized_package, client_address)
        logger.debug(f"Sent packet i{i}, Base:{base}, nextseq: {next_seqnum}")
        # make sure the end of file transimited correct

    end_package = Package(seq = -1, data=b'')
    serialized_end_package = pickle.dumps(end_package)
    server_socket.sendto(serialized_end_package, client_address)
    print("File transfer completed.")
    logger.info("File transfer completed.")
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
        logger.debug(f"Received ack: {ack.decode()}, base: {base}, nextseq: {next_seqnum}")
        if base == next_seqnum:
            # logger.debug(f'所有发送的报文均已被收到，停止计时, base: {base}, next_seqnum: {next_seqnum}')
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
    
    server_socket.close()
    
 
if __name__ == "__main__":
    main()
     
