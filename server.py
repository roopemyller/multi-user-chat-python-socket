import socket, threading

# Server conf
HOST = "127.0.0.1"
PORT = 3000
clients = {}
channels = {}

# Function to broadcast messages to all connected clients
def broadcast(message, nickname=""):
    # Broadcast to all users
    for client_socket in clients.values():
        try:
            # Options for message from user and message from "server" e.g disconnections etc.
            if nickname == "":
                client_socket.send(f"[General] {message}".encode("utf-8"))
            else:    
                client_socket.send(f"[General] {nickname}: {message}".encode("utf-8"))
        except (ConnectionResetError, BrokenPipeError):
            print(f"failed to send message to {nickname}")

# Function to send private messages to a specific client
def private_message(client_socket, nickname, recipient, msg):
    if recipient in clients:
        # Send the private message to the recipient
        clients[recipient].send(f"[Private] {nickname}: {msg}".encode("utf-8"))
    else:
        # Notify the sender that the recipient is not found
        client_socket.send(f"User '{recipient}' not found!".encode("utf-8"))

# Function to handle channel messages
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

# Function to handle joining and leaving channels
def join_channel(client_socket, nickname, channel_name):
    if channel_name not in channels:
        channels[channel_name] = []
    channels[channel_name].append(nickname)
    broadcast(f"{nickname} joined channel {channel_name}")

# Function to handle client disconnection
def leave_channel(client_socket, nickname, channel_name):
    if channel_name in channels and nickname in channels[channel_name]:
        channels[channel_name].remove(nickname)
        broadcast(f"{nickname} left channel {channel_name}")
    else:
        client_socket.send(f"You are not in channel {channel_name}".encode("utf-8"))

# Function to handle client exit
def exit_chat(nickname):
    if nickname in clients:
        del clients[nickname]
    for channel in channels.values():
        if nickname in channel:
            channel.remove(nickname)
    
    broadcast(f"{nickname} disconnected.")
    print(f"{nickname} disconnected.")

# Function to handle listing available channels
def list_channels(client_socket):
    if channels:
        channel_list = ", ".join(channels.keys())
        client_socket.send(f"Available channels: {channel_list}".encode("utf-8"))
    else:
        client_socket.send("No active channels.".encode("utf-8"))

# Function to handle client connections and messages
def handle_client(client_socket, nickname):
    while True:
        # Receive messages from the client
        try:
            # Check if the client is still connected
            message = client_socket.recv(1024).decode("utf-8")
            try:
                # Handle private messages
                if message.startswith("/private"):
                    parts = message.split(" ", 2)
                    if len(parts) < 3:
                        client_socket.send("Invalid usage of command /private".encode("utf-8"))
                    else:
                        _, recipient, msg = parts
                        private_message(client_socket, nickname, recipient, msg)
                    
                # List channels
                elif message.startswith("/list"):
                    list_channels(client_socket)

                # Hande channel messages
                elif message.startswith("/channel"):
                    parts = message.split(" ", 2)
                    if len(parts) < 3:
                        client_socket.send("Invalid usage of command /channel".encode("utf-8"))
                    else:
                        _, channel_name, msg = parts
                        channel_message(client_socket, nickname, channel_name, msg)

                # Handle channel joining               
                elif message.startswith("/join"):
                    parts = message.split(" ", 1)
                    if len(parts) < 2:
                        client_socket.send("Invalid usage of command /join, channel name should not contain whitespaces".encode("utf-8"))
                    else:
                        _, channel_name = parts
                        join_channel(client_socket, nickname, channel_name)

                # Handle channel leaving
                elif message.startswith("/leave"):
                    parts = message.split(" ", 1)
                    if len(parts) < 2:
                        client_socket.send("Invalid usage of command /leave, channel name should not contain whitespaces".encode("utf-8"))
                    else:
                        _, channel_name = parts
                        leave_channel(client_socket, nickname, channel_name)
                
                # Handle client exit
                elif message.startswith("/exit"):
                    exit_chat(nickname)
                    break

                # Handle list users
                elif message.startswith("/users"):
                    client_list = ", ".join(clients.keys())
                    client_socket.send(f"Online users: {client_list}".encode("utf-8"))
                
                # Handle invalid commands
                elif message.startswith("/"):
                    client_socket.send("Invalid command!")

                # Handle normal messages to everyone
                else:
                    broadcast(message, nickname)
            except Exception as e:
                print(f"Error prosessing command {message}: {e}")
                client_socket.send("Invalid command format.".encode("utf-8"))
        except:
            # Handle disconnection
            print(f"{nickname} disconnected.")
            if nickname in clients:
                clients.pop(nickname)
            broadcast(f"{nickname} has left the chat.")
            client_socket.close()
            break

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
            threading.Thread(target=handle_client, args=(client_socket, nick), daemon=True).start()

start_server()