import socket
import threading

# Server Configuration
HOST = "127.0.0.1"
PORT = 3000

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            print(message)
        except:
            print("Disconnected from server.")
            client_socket.close()
            break

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    
    nickname = input("Enter your nickname: ")
    client.send(nickname.encode("utf-8"))
    
    threading.Thread(target=receive_messages, args=(client,)).start()
    
    while True:
        message = input()
        if message.lower() == "exit":
            client.close()
            break
        client.send(message.encode("utf-8"))
    
if __name__ == "__main__":
    start_client()
