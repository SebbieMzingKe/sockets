import socket
import threading
import random

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind(("localhost", random.randint(8000, 9000)))

name = input("Nickname: ")


def receive():
    while True:
        try:
            message, _ = client.recvfrom(1024)
            print(message.decode())
        except:
            pass

t = threading.Thread(target = receive)
t.start()

client.sendto(f"SIGNUP_TAG: {name}".encode(), ("localhost", 9999))

while True:
    message = input("")  
    if message == "!q":
        client.sendto(f"{name} has left the chat.".encode(), ("localhost", 9999))
        print("You have left the chat.")
        client.close()
        break
    else:
        client.sendto(f"{name}: {message}".encode(), ("localhost", 9999))


