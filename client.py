from socket import *
import pickle
class Package:
    def __init__(self, seq, data):
        self.seq = seq  # 序号
        self.data = data  # 数据


server_name = 'hostip'
server_port = 12000
client_socket = socket(AF_INET, SOCK_DGRAM)

server_address = (server_name, 12000)  # 替换为实际的服务器 IP 地址和端口号
filename = "testfile.c"
client_socket.sendto(filename.encode(), server_address)

with open(filename, 'wb') as f:
    while True:
        data, server_address = client_socket.recvfrom(2048)
        received_package = pickle.loads(data)
        if received_package.seq == -1:
            # 接收到结束通知，退出循环
            print("File transfer completed.")
            break
        f.write(received_package.data)

# 关闭客户端 socket
# client_socket.close()
# while True:
#     data, server_address = client_socket.recvfrom(2048)

#     # 反序列化收到的数据
#     received_package = pickle.loads(data)

#     # 打印收到的数据
#     print(f"Received Package - Seq: {received_package.seq}, Data: {received_package.data}")

    # 关闭客户端 socket
client_socket.close()


