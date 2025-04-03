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

# Function to display help information of available commands
def help():
    print("\nCommands:")
    print("/list - List available channels")
    print("/join <channel_name> - Join a channel, if channel doesn't exist, it will be created")
    print("/leave <channel_name> - Leave a channel")
    print("/channel <channel_name> <message> - Send a message to a channel")
    print("/private <nickname> <message> - Send a private message")
    print("/help - Show this help message")
    print("/exit - Exit the chat\n")

def exit_chat(client_socket):
    # Send exit message to the server
    client_socket.send("/exit".encode("utf-8"))
    print("Exiting chat...")
    client_socket.close()

# Function to start the client and connect to the server 
def start_client():
    # Create a TCP/IP socket

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        
        # Get the nickname from the user
        while True:
            nickname = input("Enter your nickname: ")
            if "/" in nickname:
                print("Nickname cannot contain '/'")
            elif len(nickname) > 20:
                print("Nickname cannot be longer than 20 characters")
            else:
                break
        # Send the nickname to the server
        client.send(nickname.encode("utf-8", errors="replace"))
        
        # Start a thread to receive messages from the server
        threading.Thread(target=receive_messages, args=(client,)).start()
        
        print("\nWelcome to the chat!")
        print("Type /help for a list of commands.")
        print("Happy chatting!\n")

        # Main loop to send messages to the server
        while True:
            message = input()

            if message.startswith("/help"):
                help()
            elif message.startswith("/exit"):
                exit_chat(client)
                break
            else: 
                client.send(message.encode("utf-8", errors="replace"))
    except ConnectionRefusedError:
        print("Connection refused. Is the server running?")
        client.close()
        return
    except ConnectionResetError:
        print("Server connection was forcibly closed. The server might have been stopped.")
        client.close()
        return
    except ConnectionAbortedError:
        print("Connection aborted. Please try again.")
        client.close()
        return
    except Exception as e:
        print(f"Connection failed: {e}")
        client.close()
        return
    
start_client()
