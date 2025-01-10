import socket
import threading

choice = input("Do you want to be a server(1) or a client(2)?")

match choice:
    case "1":
        ip = input("Please type the ip to which it should listen")
        port = int(input("Please select the port"))
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((ip, port))
        server.listen()

        client, _ = server.accept()

    case "2":
        ip = input("Please select the ip to connect to")
        port = int(input("Please select the port"))

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((ip, port))

    case _:
        exit()



def sending_messages(c):
    while True:
        message = input()
        c.send(message.encode())


def receivin_messages(c):
    while True:
        print("Partner: " + c.recv(1024).decode())

threading.Thread(target=sending_messages, args=(client, )).start()
threading.Thread(target=receivin_messages, args=(client, )).start()



