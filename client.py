import socket
import threading

# Server Configuration
HOST = "127.0.0.1"
PORT = 3000

# Function to receive messages from the server
def receive_messages(client_socket):
    while True:
        try:
            # Receive messages from the server
            message = client_socket.recv(1024).decode("utf-8")
            print(message)
        except:
            # Handle disconnection
            print("Disconnected from server.")
            client_socket.close()
            break

# Function to start the client and connect to the server 
def start_client():
    # Create a TCP/IP socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    
    # Get the nickname from the user
    nickname = input("Enter your nickname: ")
    client.send(nickname.encode("utf-8"))
    
    # Start a thread to receive messages from the server
    threading.Thread(target=receive_messages, args=(client,)).start()
    
    # Main loop to send messages to the server
    while True:
        message = input()
        if message.lower() == "exit":
            client.send("exit".encode("utf-8"))
            client.close()
            break
        client.send(message.encode("utf-8"))
    
start_client()
