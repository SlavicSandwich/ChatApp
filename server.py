import socket
import threading

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = socket.gethostname()
PORT = 5555

serversocket.bind((HOST, PORT))

clients = []
maxnum_of_clients = 2
serversocket.listen(maxnum_of_clients)

def send_msg(conn, id, msg):
    try:
        conn.sendall(msg)

    except ConnectionResetError:
        print(f'[Connection closed] {id}')
        for ind, client in enumerate(clients):
            if client[1] == id:
                clients.pop(ind)


def recv_snd_msg(conn, id):
    while True:
        data_length = int.from_bytes(conn.recv(4), 'big')
        if data_length:
            data = conn.recv(data_length)
            for client in clients:
                if client[1] != id:
                    send_msg(client[0], client[1], data)

def handle_client(conn, id):
    # send_msg(conn, id, f"Welcome to the chat room! Your id is {id}")
    chat_thread = threading.Thread(target=recv_snd_msg, args=(conn, id))
    chat_thread.start()

while True:
    (conn, addr) = serversocket.accept()
    name = conn.recv(1024).decode()
    id = name + str(addr[1])
    clients.append((conn, id))
    print(f'[New Connection] Connected to {id}')
    handle_client(conn, id)