# 使用python3.7以上,此文件需要严格约束数据类型
from __future__ import annotations
from socket import *
import pickle
import random
import logging
import heapq


class Package:
    def __init__(self, seq, data):
        self.seq = seq  # 序号
        self.data = data  # 数据
    # 提供一个堆排序时的比较方法
    def __lt__(self, other:Package):
        return self.seq < other.seq
    # 定义打印规则
    def __repr__(self):
        return f"Package(seq={self.seq}, data={self.data})"

# 用小顶堆来作为接收窗口,以序号排序,大小与发送窗口应当一致
class SR_pack:
    def __init__(self):
        self.heap:heapq=[]
    def push(self, item):
        heapq.heappush(self.heap, item)

    def pop(self):
        return heapq.heappop(self.heap)

    def peek(self) -> Package:
        return self.heap[0]

    def size(self):
        return len(self.heap)


def sr_rec(n, s, fname):
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
        sr_pack: SR_pack= SR_pack()
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

                '''
                    关键逻辑:
                    SR中存储的包都是序号大于expected的包,当等于expected的包到来时,
                    就意味着之前缓存的包可以出队了,和所到包连续的一系列包都可以成功出队,
                    这里注意同步要调整ack和expected的值
                '''
                while(sr_pack.size()!=0 and sr_pack.peek().seq==expected):
                    f.write(sr_pack.peek().data)
                    ack += 1
                    expected += 1
                    sr_pack.pop()
                
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

                # 将收到的包暂存在sr_pack中,如果已经满了就不再缓存,直接丢弃,但是也可以使用更好的策略
                # 比如实际上缓存的包序号时连续的是最好的,因为重发往往会连续重发多个,缓存不连续的包可能会舍弃很多

                if(sr_pack.size()<window_size):
                    sr_pack.push(received_package)


    client_socket.close()