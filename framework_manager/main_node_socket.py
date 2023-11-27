import socket
import threading
import time
import redis

def handle_slave(connection, client_address, online_nodes, lock):
    try:
        print(f"Connection established with {client_address}")

        with lock:
            # 将新连接的节点添加到在线节点列表中
            online_nodes.append(client_address)
            update_redis_online_nodes(online_nodes)

        while True:
            # 发送心跳消息
            connection.sendall(b'heartbeat')
            time.sleep(5)  # 每 5 秒发送一次心跳消息

            # 接收来自从节点的消息
            data = connection.recv(1024)
            if data:
                print(f"Received data from {client_address}: {data.decode('utf-8')}")
            else:
                break  # 如果连接中断，则退出循环
    except Exception as e:
        print(f"Exception occurred: {e}")
    finally:
        with lock:
            # 将断开连接的节点从在线节点列表中删除
            online_nodes.remove(client_address)
            update_redis_online_nodes(online_nodes)

        # 关闭连接
        connection.close()
        print(f"Connection with {client_address} closed")

def update_redis_online_nodes(online_nodes):
    # 更新 Redis 中的在线节点列表
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.set('online_nodes', ','.join(map(str, online_nodes)))
    print(f"Updated online nodes: {online_nodes}")

def main_node():
    # 创建 socket 对象
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 绑定 IP 地址和端口
    server_address = ('localhost', 8888)
    server_socket.bind(server_address)

    # 监听连接
    server_socket.listen()

    # 在线节点列表
    online_nodes = []

    # 创建锁
    lock = threading.Lock()

    while True:
        print("Waiting for a connection...")
        connection, client_address = server_socket.accept()

        # 为每个从节点创建一个新线程处理连接
        thread = threading.Thread(target=handle_slave, args=(connection, client_address, online_nodes, lock))
        thread.start()

if __name__ == "__main__":
    main_node()
