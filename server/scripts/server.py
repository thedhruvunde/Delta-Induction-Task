import socket
import threading
import os
import psycopg2
import bcrypt

# PostgreSQL configuration from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "masalachatdb")
DB_USER = os.getenv("DB_USER", "chatuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "chatpass")

# Setup PostgreSQL connection
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

# Create users table if not exists
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Register a new user
def register_user(conn, username, password):
    cur = conn.cursor()
    try:
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed))
        conn.commit()
        return True
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False
    except Exception as e:
        print("Error registering user:", e)
        conn.rollback()
        return False
    finally:
        cur.close()

# Authenticate a user
def authenticate_user(conn, username, password):
    cur = conn.cursor()
    try:
        cur.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
        result = cur.fetchone()
        if result and bcrypt.checkpw(password.encode(), result[0].encode()):
            return True
        return False
    finally:
        cur.close()

# Handle client connections
clients = []
client_usernames = {}

def broadcast(message, sender_socket=None):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except:
                client.close()
                clients.remove(client)

def handle_client(client_socket, address):
    print(f"[NEW CONNECTION] {address} connected.")

    conn = get_db_connection()

    try:
        client_socket.send(b"Do you want to [register] or [login]? ")
        choice = client_socket.recv(1024).decode().strip()

        client_socket.send(b"Enter username: ")
        username = client_socket.recv(1024).decode().strip()

        client_socket.send(b"Enter password: ")
        password = client_socket.recv(1024).decode().strip()

        if choice.lower() == "register":
            if register_user(conn, username, password):
                client_socket.send(b"Registration successful.\n")
            else:
                client_socket.send(b"Username already exists or registration error.\n")
                client_socket.close()
                return
        elif choice.lower() == "login":
            if authenticate_user(conn, username, password):
                client_socket.send(b"Login successful.\n")
            else:
                client_socket.send(b"Invalid credentials.\n")
                client_socket.close()
                return
        else:
            client_socket.send(b"Invalid option. Disconnecting.\n")
            client_socket.close()
            return

        clients.append(client_socket)
        client_usernames[client_socket] = username
        broadcast(f"[{username}] has joined the chat!\n".encode(), client_socket)

        while True:
            msg = client_socket.recv(1024)
            if not msg:
                break
            broadcast(f"[{username}] {msg.decode()}".encode(), client_socket)

    except Exception as e:
        print(f"Error handling client {address}: {e}")
    finally:
        print(f"[DISCONNECT] {address} disconnected.")
        if client_socket in clients:
            clients.remove(client_socket)
            broadcast(f"[{client_usernames.get(client_socket)}] has left the chat.\n".encode())
        client_socket.close()
        conn.close()

def start_server():
    init_db()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 5555))
    server.listen()
    print("[SERVER STARTED] Listening on port 5555...")

    while True:
        client_socket, address = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, address))
        thread.start()

if __name__ == "__main__":
    start_server()
