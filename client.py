from socket import *
import pickle
import os
import random
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='rcv.log', level=logging.DEBUG, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
class Package:
    def __init__(self, seq, data):
        self.seq = seq  # 序号
        self.data = data  # 数据

server_name = 'localhost'
server_port = 12000
client_socket = socket(AF_INET, SOCK_DGRAM)

server_address = (server_name, 12000)  # 替换为实际的服务器 IP 地址和端口号
filename = "../test_file/lex.yy.c"
client_socket.sendto(filename.encode(), server_address)

loss_rate = 0.1
expected = 0

with open('lex.yy.c', 'wb') as f:
    while True:
        data, server_address = client_socket.recvfrom(2048)
        received_package = pickle.loads(data)
        ack = received_package.seq
        
        if received_package.seq == -1:
            # 接收到结束通知，退出循环
            logger.debug("File transfer completed.")
            # 结束发送-1
            client_socket.sendto(str(-1).encode(), server_address)
            break

        elif ack == expected:
            logger.debug(f'rev expected seq {ack}')
            f.write(received_package.data)
            expected += 1
            # 模拟丢包
            if random.random() >= loss_rate:
                client_socket.sendto(str(ack).encode(), server_address)
                logger.debug(f'sending ack success: {ack}')
            else:
                logger.error(f"Fail to sending ack: {ack}")
        
        else:
            # 不符合预期，发送最大接受包
            # if random.random() >= loss_rate:
            client_socket.sendto(str(expected -1).encode(), server_address)
            logger.warning(f'Expected seq: {expected}, but receive: {ack}')


client_socket.close()