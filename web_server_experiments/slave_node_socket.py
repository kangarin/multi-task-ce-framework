import socket
import time

def slave_node():
    # 创建 socket 对象
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 连接到主节点
    server_address = ('localhost', 8888)
    client_socket.connect(server_address)
    
    while True:
        # 接收来自主节点的心跳消息
        data = client_socket.recv(1024)
        if data:
            print(f"Received heartbeat: {data.decode('utf-8')}")
        else:
            break  # 如果连接中断，则退出循环
        
        # 模拟从节点的工作
        # 在这里可以执行一些任务
        
        time.sleep(3)  # 每 3 秒执行一次任务并等待主节点的心跳消息

        # 向主节点发送消息
        client_socket.sendall(b"Hello from the slave node")
    
    # 关闭连接
    client_socket.close()

if __name__ == "__main__":
    slave_node()
