import socket
import threading

# Function to receive messages from the server
def receive_messages(client_socket):
    while True:
        try:
            # Receive messages from the server
            message = client_socket.recv(1024).decode("utf-8")
            print(message)
        except ConnectionResetError:
            print("Server connection was closed.")
            break
        except ConnectionAbortedError:
            print("Connection aborted unexpectedly.")
            break
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

# Function to display help information of available commands
def help():
    print("\nCommands:")
    print("/list - List available channels")
    print("/join <channel_name> - Join a channel, if channel doesn't exist, it will be created")
    print("/leave <channel_name> - Leave a channel")
    print("/channel <channel_name> <message> - Send a message to a channel")
    print("/private <nickname> <message> - Send a private message")
    print("/users - List users online")
    print("/help - Show this help message")
    print("/exit - Exit the chat\n")

def exit_chat(client_socket):
    # Send exit message to the server
    client_socket.send("/exit".encode("utf-8"))
    print("Exiting chat...")
    client_socket.close()

def connect_to_server():
     # Create a TCP/IP socket
    host = input("Enter server IP (default 127.0.0.1): ") or "127.0.0.1"
    port = 3000
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
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
        response = client.recv(1024).decode("utf-8")
        if response == "Nickname already in use. Try another one.":
            print("Nickname already in use! Try again.")
            client.close()
        else:
            return client, nickname
    except Exception as e:
        print(f"error: {e}")


# Function to start the client and connect to the server 
def start_client():
    try:
        client, nickname = connect_to_server()
        if client:
            connected = True

            # Start a thread to receive messages from the server
            threading.Thread(target=receive_messages, args=(client,), daemon=True).start()
            
            print(f"\nWelcome to the chat {nickname}!\nType /help for a list of commands.\n")

            # Main loop to send messages to the server
            while connected:
                message = input()
                if message.startswith("/help"):
                    help()
                elif message.startswith("/exit"):
                    exit_chat(client)
                    connected = False
                else: 
                    try: 
                        client.send(message.encode("utf-8", errors="replace"))
                    except (BrokenPipeError, ConnectionRefusedError):
                        print("Server connection lost. Exiting...")
                        connected = False
    except Exception as e:
        print(f"Connection failed: {e}")
        client.close()
        return
    finally:
        client.close()
    
start_client()
