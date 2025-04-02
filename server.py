import socket, threading

# Server conf
HOST = "127.0.0.1"
PORT = 3000
clients = {}
channels = {}

def private_message(client_socket, nickname, recipient, msg):
    if recipient in clients:
        # Send the private message to the recipient
        clients[recipient].send(f"[Private] {nickname}: {msg}".encode("utf-8"))
    else:
        # Notify the sender that the recipient is not found
        client_socket.send(f"User '{recipient}' not found!".encode("utf-8"))

def channel_message(client_socket, nickname, channel_name, msg):
     # Broadcast the message to all clients in the specified channel
    if channel_name in channels:
        if nickname not in channels[channel_name]:
            client_socket.send("You are not in this channel!".encode("utf-8"))
        else:
            # Send the message to all clients in the channel
            for client in channels[channel_name]:       
                clients[client].send(f"[{channel_name}] {nickname}: {msg}".encode("utf-8"))
    else:
        client_socket.send("Channel not found!".encode("utf-8"))

def join_channel(client_socket, nickname, channel_name):
    if channel_name not in channels:
        channels[channel_name] = []
    channels[channel_name].append(nickname)
    client_socket.send(f"Joined channel {channel_name}".encode("utf-8"))

def leave_channel(client_socket, nickname, channel_name):
    if channel_name in channels and nickname in channels[channel_name]:
        channels[channel_name].remove(nickname)
        client_socket.send(f"Left channel {channel_name}".encode("utf-8"))
    else:
        client_socket.send(f"You are not in channel {channel_name}".encode("utf-8"))

# Function to handle client connections and messages
def handle_client(client_socket, nickname):
    while True:
        # Receive messages from the client
        try:
            # Check if the client is still connected
            message = client_socket.recv(1024).decode("utf-8")

            # Handle private messages
            if message.startswith("/private"):
                _, recipient, msg = message.split(" ", 2)
                private_message(client_socket, nickname, recipient, msg)
            
            # List channels
            elif message.startswith("/list"):
                channel_list = ", ".join(channels.keys())
                client_socket.send(f"Available channels: {channel_list}".encode("utf-8"))

            # Hande channel messages
            elif message.startswith("/channel"):
                _, channel_name, msg = message.split(" ", 2)
                channel_message(client_socket, nickname, channel_name, msg)

            # Handle channel joining               
            elif message.startswith("/join"):
                _, channel_name = message.split(" ", 1)
                join_channel(client_socket, nickname, channel_name)

            # Handle channel leaving
            elif message.startswith("/leave"):
                _, channel_name = message.split(" ", 1)
                leave_channel(client_socket, nickname, channel_name)

            # Handle normal messages
            else:
                if message.lower() == "exit":
                    # Handle client exit
                    client_socket.send(f"{nickname} disconnected.".encode("utf-8"))
                    print(f"{nickname} disconnected.")
                    break
                # Broadcast the message to all connected clients if not private message
                broadcast(f"{nickname}: {message}")
        except:
            # Handle disconnection
            print(f"{nickname} disconnected.")
            clients.pop(nickname)
            broadcast(f"{nickname} has left the chat.")
            client_socket.close()
            break

# Function to broadcast messages to all connected clients
def broadcast(message):
    for client_socket in clients.values():
        client_socket.send(message.encode("utf-8"))

# Main server function to start listening for connections and handle clients
def start_server():
    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Set socket options to allow reuse of the address
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind the socket to the address and port
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}: {PORT}")
        
        # Accept incoming connections
        while True:
            client_socket, addr = s.accept()
            nick = client_socket.recv(1024).decode("utf-8")
            clients[nick] = client_socket
            print(f"{nick} connected from {addr}")
            broadcast(f"{nick} has joined the chat.")
            # Start a new thread for each client
            threading.Thread(target=handle_client, args=(client_socket, nick)).start()

start_server()