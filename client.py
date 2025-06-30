import socket
import threading
import readline
import sys
from colorama import Fore, Style, init
init()

HOST = '127.0.0.1'
PORT = 5555

COLOR_MAP = {
    'RED': Fore.RED,
    'GREEN': Fore.GREEN,
    'YELLOW': Fore.YELLOW,
    'BLUE': Fore.BLUE,
    'MAGENTA': Fore.MAGENTA,
    'CYAN': Fore.CYAN,
    'WHITE': Fore.WHITE
}

def parse_color_tags(msg):
    for name, code in COLOR_MAP.items():
        msg = msg.replace(f"<{name}>", code)
    return msg + Style.RESET_ALL

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if not msg:
                break
            msg = parse_color_tags(msg)

            # Save current input
            current_input = readline.get_line_buffer()
            sys.stdout.write("\r" + " " * (len(current_input) + 40) + "\r")  # Clear line
            print("\n" + msg)
            sys.stdout.write(Fore.YELLOW + f"Type here (or /exit): {current_input}" + Style.RESET_ALL)
            sys.stdout.flush()
        except:
            print("Connection closed.")
            break

def send_messages(sock):
    while True:
        try:
            msg = input(Fore.YELLOW + "Type here (or /exit): " + Style.RESET_ALL)
            sock.send(msg.encode())
            if msg.strip().lower() == "/exit":
                break
        except:
            break

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()
    send_messages(sock)
    sock.close()

if __name__ == "__main__":
    main()
