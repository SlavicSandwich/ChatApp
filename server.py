import socket
import threading

import select

INTERVAL = 0.4


class ClientInfo:
    def __init__(self, id, socket):
        # self.name = name
        self.id = id
        self.socket = socket


class Server:
    def __init__(self, port, ip="localhost", maxclients=2):
        self.ip = ip
        self.port = port
        self.connected_clients = []
        self.client_ids = set()
        self.max_clients = maxclients

        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((self.ip, self.port))
        self.serversocket.listen(self.max_clients)
        self.is_running = False

    def run_server(self):
        self.is_running = True
        while self.is_running:
            client_socket, client_address = self.serversocket.accept()
            self.new_client(client_socket, client_address)

    def stop_server(self):
        self.is_running = False

    def broadcast_message(self, id_from, data, data_length):
        for client in self.connected_clients:
            if client.id != id_from:
                try:
                    client.socket.send(data_length.to_bytes(4, 'big'))
                    client.socket.send(data)

                except Exception as e:
                    print(e)

    def new_client(self, socket, address):
        # name = socket.recv(1024).decode()
        id = address[1]
        client = ClientInfo(id, socket)
        self.client_ids.add(id)
        self.connected_clients.append(client)
        thread = threading.Thread(target=self.handle_client, args=(client,))
        thread.start()

    def handle_client(self, client: ClientInfo):
        while True:
            if client.id not in self.client_ids:
                break
            data_length = int.from_bytes(client.socket.recv(4), "big")
            if data_length:
                data = client.socket.recv(data_length)
                self.broadcast_message(client.id, data, data_length)

    #         data_length = int.from_bytes(conn.recv(4), 'big')
    #         if data_length:
    #             data = conn.recv(data_length)
    #             for client in clients:
    #                 if client[1] != id:
    #                     send_msg(client[0], client[1], data, data_length)

    def remove_client(self, client: ClientInfo):
        client.socket.close()
        for index, val in enumerate(self.connected_clients):
            if val.id == client.id:
                self.client_ids.remove(client.id)
                self.connected_clients.pop(index)
                break


def is_port_available(port):
    try:
        host_ip = socket.gethostbyname(socket.gethostname())
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.bind((host_ip, port))
        return True

    except:
        return False

# obj = Server(socket.gethostname(), 5555)
# threading.Thread(target=obj.run_server()).start()


# serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# HOST = socket.gethostname()
# PORT = 5555
#
# serversocket.bind((HOST, PORT))
#
# clients = []
# maxnum_of_clients = 2
# serversocket.listen(maxnum_of_clients)
#
# def send_msg(conn, id, msg, length):
#     try:
#         conn.sendall(length.to_bytes(4, 'big'))
#         conn.sendall(msg)
#
#     except ConnectionResetError:
#         print(f'[Connection closed] {id}')
#         for ind, client in enumerate(clients):
#             if client[1] == id:
#                 clients.pop(ind)
#
#
# def recv_snd_msg(conn, id):
#     while True:
#         data_length = int.from_bytes(conn.recv(4), 'big')
#         if data_length:
#             data = conn.recv(data_length)
#             for client in clients:
#                 if client[1] != id:
#                     send_msg(client[0], client[1], data, data_length)
#
# def handle_client(conn, id):
#     # send_msg(conn, id, f"Welcome to the chat room! Your id is {id}")
#     chat_thread = threading.Thread(target=recv_snd_msg, args=(conn, id))
#     chat_thread.start()
#
# while True:
#     (conn, addr) = serversocket.accept()
#     name = conn.recv(1024).decode()
#     id = name + str(addr[1])
#     clients.append((conn, id))
#     print(f'[New Connection] Connected to {id}')
#     handle_client(conn, id)
