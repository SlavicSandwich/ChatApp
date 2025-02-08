import json
import socket
import threading

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import base64
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = socket.gethostname()
PORT = 5555

client.connect((HOST, PORT))

def send_msg(conn):
    while True:
        try:
            msg = input()
            # conn.send(msg.encode())

            encrypted_message, nonce = encrypt_message(key, msg)
            # print(key)
            # print(decrypt_message(key, encrypted_message, nonce))
            # print(encrypted_message)
            # print(base64.urlsafe_b64encode(encrypted_message))
            # print(base64.urlsafe_b64decode(base64.urlsafe_b64encode(encrypted_message)))

            data = {
                "ciphertext": str(base64.urlsafe_b64encode(encrypted_message))[1:],
                "nonce": str(base64.urlsafe_b64encode(nonce))[1:],
            }
            # print(data['ciphertext'])
            json_data = json.dumps(data).encode('utf-8')
            # print(json.loads(json_data.decode('utf-8'))['ciphertext'])

            conn.sendall(len(json_data).to_bytes(4, 'big'))
            conn.sendall(json_data)



        except ConnectionResetError:
            print("Couldn't send message to server, make sure the server is running")


def recv_msg(conn):
    while True:
        try:
            # msg = conn.recv(1024).decode()
            # print(msg)

            data_length = int.from_bytes(conn.recv(4), 'big')

            if data_length:
                data = conn.recv(data_length).decode('utf-8')
                message = json.loads(data)

                ciphertext = base64.urlsafe_b64decode(message['ciphertext'])
                nonce = base64.urlsafe_b64decode(message['nonce'])

                print(decrypt_message(key, ciphertext, nonce))

        except ConnectionResetError or ValueError:
            print("Couldn't send message to server, make sure the server is running")


def encrypt_message(key: bytes, message: str) -> (bytes, bytes):
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, message.encode(), None)
    return ciphertext, nonce


def decrypt_message(key: bytes, ciphertext: bytes, nonce: bytes) -> str:
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode()


def generate_key_from_password(password: str) -> (bytes, bytes):
    salt = b"default_salt_value"

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return key, salt


key, salt = generate_key_from_password(input())

client.send(input().encode())

threading.Thread(target=recv_msg, args=(client,)).start()
threading.Thread(target=send_msg, args=(client,)).start()

