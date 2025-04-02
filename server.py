import socket, threading

# Server conf
HOST = "127.0.0.1"
PORT = 3000
clients = {}

def handle_client(client_socket, nickname):
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if message.startswith("/private"):
                _, recipient, private_msg = message.split(" ", 2)
                if recipient in clients:
                    clients[recipient].send(f"[Private] {nickname}: {private_msg}".encode("utf-8"))
                else:
                    client_socket.send("User not found!".encode("utf-8"))
            else:
                broadcast(f"{nickname}: {message}")
        except:
            print(f"{nickname} disconnected.")
            clients.pop(nickname)
            broadcast(f"{nickname} has left the chat.")
            client_socket.close()
            break

# Broadcast message to all clients
def broadcast(message):
    for client_socket in clients.values():
        client_socket.send(message.encode("utf-8"))

def start_server():

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}: {PORT}")
        
        while True:
            client_socket, addr = s.accept()
            nick = client_socket.recv(1024).decode("utf-8")
            clients[nick] = client_socket
            print(f"{nick} connected from {addr}")
            broadcast(f"\n{nick} has joined the chat.")
            threading.Thread(target=handle_client, args=(client_socket, nick)).start()

start_server()