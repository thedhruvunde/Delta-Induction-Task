import socket
import threading
import sys
import random
from colorama import Fore, Style, init
init()

HOST = '127.0.0.1'
PORT = 5555

COLORS = [
    Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE,
    Fore.MAGENTA, Fore.CYAN, Fore.WHITE
]
BOLD = Style.BRIGHT
RESET = Style.RESET_ALL

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

user_color = random.choice(COLORS)

# --- Setup ---
while True:
    server_msg = sock.recv(1024).decode()
    print(server_msg, end='')
    user_input = input()
    sock.send(user_input.encode())
    if "Created and joined" in server_msg or "Joined" in server_msg:
        break

# --- Receiver Thread ---
def receive_messages():
    while True:
        try:
            msg = sock.recv(1024).decode()
            if not msg:
                break

            if msg.startswith("Total Active Users"):
                print(f"\n{Fore.CYAN + Style.BRIGHT}[Active Users]{Style.RESET_ALL}")
                print(Fore.YELLOW + msg + Style.RESET_ALL)

            elif msg.startswith("Room Stats"):
                print(f"\n{Fore.CYAN + Style.BRIGHT}[Room Stats]{Style.RESET_ALL}")
                print(Fore.GREEN + msg + Style.RESET_ALL)

            elif msg.startswith("Top 10 by Active Time:") or "Your Rank" in msg:
                print(f"\n{Fore.MAGENTA + Style.BRIGHT}[Leaderboard]{Style.RESET_ALL}")
                print(Fore.MAGENTA + msg + Style.RESET_ALL)

            else:
                sys.stdout.write('\r' + ' ' * 80 + '\r')
                print(msg)

            sys.stdout.write("Type here (or /exit): ")
            sys.stdout.flush()
        except Exception as e:
            print(f"\n[Receive error] {e}")
            break

threading.Thread(target=receive_messages, daemon=True).start()

# --- Sender Loop ---
while True:
    try:
        msg = input("Type here (or /exit): ")
        if msg.lower() == "/exit":
            sock.send(b"/exit")
            break
        elif msg.strip() == "":
            continue
        else:
            colored_name = f"{user_color}{BOLD}You{RESET}"
            formatted = f"{colored_name}\n{msg}"
            sock.send(formatted.encode())
    except KeyboardInterrupt:
        print("\nExiting...")
        sock.send(b"/exit")
        break

sock.close()
