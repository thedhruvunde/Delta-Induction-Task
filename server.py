### server.py
import socket
import threading
import time
import sqlite3
import random
from datetime import datetime

HOST = '127.0.0.1'
PORT = 5555

clients = {}  # socket: {username, room, join_time, message_count, color}
rooms = {}  # room_id: {"clients": set(), "is_private": bool, "created_by": username, "name": str}
lock = threading.Lock()

COLORS = ["RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE"]

# Setup SQLite database
conn = sqlite3.connect('chatmasaladb.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, total_messages INTEGER, total_time_online REAL)''')
c.execute('''CREATE TABLE IF NOT EXISTS messages (username TEXT, room TEXT, content TEXT, timestamp TEXT)''')
conn.commit()

def generate_room_id():
    while True:
        room_id = str(random.randint(100000, 999999))
        if room_id not in rooms:
            return room_id

def broadcast(msg, room, sender_socket):
    with lock:
        for client in rooms.get(room, {}).get("clients", []):
            try:
                client.send(msg.encode())
            except:
                client.close()
                remove_client(client)

def remove_client(client):
    with lock:
        user = clients.get(client, {})
        if user:
            room = user['room']
            username = user['username']
            join_time = user['join_time']
            total_time = time.time() - join_time
            message_count = user['message_count']

            c.execute("INSERT OR IGNORE INTO users (username, total_messages, total_time_online) VALUES (?, 0, 0)", (username,))
            c.execute("UPDATE users SET total_messages = total_messages + ?, total_time_online = total_time_online + ? WHERE username = ?",
                      (message_count, total_time, username))
            conn.commit()

            if room in rooms:
                rooms[room]["clients"].discard(client)
            del clients[client]
            client.close()

def handle_client(client):
    try:
        client.send("Enter username: ".encode())
        username = client.recv(1024).decode().strip()

        client.send("Choose an option:\n1. Create Room\n2. Join Room\nEnter 1 or 2: ".encode())
        option = client.recv(1024).decode().strip()

        if option == '1':
            client.send("Do you want to make the room private? (yes/no): ".encode())
            private_input = client.recv(1024).decode().strip().lower()
            is_private = private_input == 'yes'
            client.send("Enter a name for your room: ".encode())
            room_name = client.recv(1024).decode().strip()
            room_id = generate_room_id()
            rooms[room_id] = {"clients": set(), "is_private": is_private, "created_by": username, "name": room_name}
            client.send(f"Created and joined {'private' if is_private else 'public'} room {room_name} with ID {room_id}".encode())
        elif option == '2':
            client.send("Choose how to join:\n1. Join by Room ID\n2. See list of public rooms\nEnter 1 or 2: ".encode())
            join_option = client.recv(1024).decode().strip()

            if join_option == '1':
                client.send("Enter 6-digit Room ID: ".encode())
                room_id = client.recv(1024).decode().strip()
                if room_id not in rooms:
                    client.send("Room does not exist. Disconnecting...".encode())
                    client.close()
                    return
                if rooms[room_id]["is_private"]:
                    client.send("This room is private. Enter creator's username to join: ".encode())
                    creator = client.recv(1024).decode().strip()
                    if creator != rooms[room_id]["created_by"]:
                        client.send("Access denied. Disconnecting...".encode())
                        client.close()
                        return
            elif join_option == '2':
                public_rooms = [(rid, data['name'], len(data['clients'])) for rid, data in rooms.items() if not data['is_private']]
                if not public_rooms:
                    client.send("No public rooms available. Disconnecting...".encode())
                    client.close()
                    return
                room_list_msg = "Available Public Rooms:\n" + "\n".join([f"{name} (ID: {rid}) - {count} users" for rid, name, count in public_rooms]) + "\nEnter Room ID to join: "
                client.send(room_list_msg.encode())
                room_id = client.recv(1024).decode().strip()
                if room_id not in rooms or rooms[room_id]["is_private"]:
                    client.send("Invalid room selection. Disconnecting...".encode())
                    client.close()
                    return
            else:
                client.send("Invalid selection. Disconnecting...".encode())
                client.close()
                return
        else:
            client.send("Invalid option. Disconnecting...".encode())
            client.close()
            return

        color = random.choice(COLORS)
        with lock:
            rooms[room_id]["clients"].add(client)
            clients[client] = {
                'username': username,
                'room': room_id,
                'join_time': time.time(),
                'message_count': 0,
                'color': color
            }

        broadcast(f"[{username} has joined the room]", room_id, client)

        while True:
            msg = client.recv(1024).decode()
            if msg.strip().lower() == "/exit":
                break
            if msg.strip().lower() == "/chclr":
                color_list = "\n".join([f"<{clr}> {clr}" for clr in COLORS])
                client.send(("Choose a color from the list:\n" + color_list + "\nYour choice: ").encode())
                new_color = client.recv(1024).decode().strip().upper()
                if new_color in COLORS:
                    clients[client]['color'] = new_color
                    client.send(f"Color changed to {new_color}".encode())
                else:
                    client.send("Invalid color name.".encode())
                continue

            username_colored = f"<{clients[client]['color']}>\033[1m{username}\033[0m"
            message_data = f"{username_colored}\n\033[97m{msg}\033[0m"
            broadcast(message_data, room_id, client)

            with lock:
                clients[client]['message_count'] += 1
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                c.execute("INSERT INTO messages (username, room, content, timestamp) VALUES (?, ?, ?, ?)",
                          (username, room_id, msg, timestamp))
                conn.commit()
    except:
        pass
    finally:
        remove_client(client)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client, addr = server.accept()
        print(f"Connected by {addr}")
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

if __name__ == "__main__":
    start_server()
