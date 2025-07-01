# === server.py (Modified) ===
import socket
import threading
import time
from collections import defaultdict

HOST = '127.0.0.1'
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
usernames = {}
message_counts = defaultdict(int)
active_users = {}
login_times = {}
total_messages = 0
total_users = set()

def broadcast(message):
    global total_messages
    total_messages += 1
    for client in clients:
        try:
            client.send(message.encode('utf-8'))
        except:
            remove(client)

def remove(client):
    if client in clients:
        username = usernames.get(client, "")
        if username:
            active_users.pop(username, None)
            login_times.pop(username, None)
        clients.remove(client)
        usernames.pop(client, None)

def handle(client):
    username = client.recv(1024).decode('utf-8')
    usernames[client] = username
    active_users[username] = time.time()
    login_times[username] = time.time()
    total_users.add(username)

    welcome = f"{username} joined the chat."
    print(welcome)
    broadcast(welcome)

    while True:
        try:
            message = client.recv(1024).decode('utf-8')

            if message == '/active':
                now = time.time()
                active_list = [u for u in active_users]
                response = f"Total Active Users: {len(active_list)}\n" + '\n'.join(f"- {u}" for u in active_list)
                client.send(response.encode('utf-8'))

            elif message == '/stats':
                username = usernames[client]
                response = f"Total Users: {len(total_users)}\nTotal Messages: {total_messages}\nYour Messages: {message_counts[username]}"
                client.send(response.encode('utf-8'))

            elif message == '/leaderboard':
                now = time.time()
                # Update active times
                active_times = {u: now - login_times.get(u, now) for u in total_users}

                sorted_time = sorted(active_times.items(), key=lambda x: x[1], reverse=True)
                sorted_msg = sorted(message_counts.items(), key=lambda x: x[1], reverse=True)

                user = usernames[client]

                def format_time(seconds):
                    m, s = divmod(int(seconds), 60)
                    h, m = divmod(m, 60)
                    return f"{h}h {m}m"

                time_board = '\n'.join([f"{i+1}. {u} - {format_time(t)}" for i, (u, t) in enumerate(sorted_time[:10])])
                msg_board = '\n'.join([f"{i+1}. {u} - {c} msgs" for i, (u, c) in enumerate(sorted_msg[:10])])

                time_rank = next((i+1 for i, (u, _) in enumerate(sorted_time) if u == user), 'N/A')
                msg_rank = next((i+1 for i, (u, _) in enumerate(sorted_msg) if u == user), 'N/A')

                response = f"Top 10 by Active Time:\n{time_board}\n\nTop 10 by Messages:\n{msg_board}\n\nYour Rank by Time: {time_rank}\nYour Rank by Messages: {msg_rank}"
                client.send(response.encode('utf-8'))

            else:
                username = usernames[client]
                message_counts[username] += 1
                broadcast(f"{username}: {message}")

        except:
            remove(client)
            break

def receive():
    print(f"Server started on {HOST}:{PORT}")
    while True:
        client, address = server.accept()
        clients.append(client)
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

receive()
