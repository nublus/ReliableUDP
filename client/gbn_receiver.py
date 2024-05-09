# 使用python3.7以上,此文件需要严格约束数据类型
from __future__ import annotations
from socket import *
import pickle
import random
import logging

class Package:
    def __init__(self, seq, data):
        self.seq = seq  # 序号
        self.data = data  # 数据

    
def gbn_rec(n, s, fname):
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='rcv.log', level=logging.DEBUG, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
    
    server_name = '8.137.79.215'
    server_port = 12000
    client_socket = socket(AF_INET, SOCK_DGRAM)
    window_size = n


    server_address = (server_name, 12000)  # 替换为实际的服务器 IP 地址和端口号

    client_socket.sendto(fname.encode(), server_address)

    loss_rate = 0.1
    expected = 0
    with open('../testcase/'+fname, 'wb') as f:
        # sr_pack: SR_pack= SR_pack()
        while True:
            data, server_address = client_socket.recvfrom(2048)
            received_package: Package = pickle.loads(data)
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