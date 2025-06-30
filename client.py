import socket
import threading
from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, HSplit
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

# Socket config
HOST = '127.0.0.1'
PORT = 5555
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

# Pre-chat interactive setup (username, room selection)
def setup_connection():
    while True:
        server_msg = sock.recv(1024).decode()
        if not server_msg:
            break
        print(server_msg, end='')  # show prompt
        user_input = input()
        sock.send(user_input.encode())
        if "Created and joined" in server_msg or "Joined" in server_msg:
            break

setup_connection()

# ---- Prompt Toolkit UI ----
chat_display = TextArea(style="class:output-field", scrollbar=True, wrap_lines=True, read_only=True)
input_field = TextArea(height=1, prompt='> ', style="class:input-field")

def print_msg(message):
    chat_display.text += message + '\n'

def receive_messages():
    while True:
        try:
            msg = sock.recv(1024).decode()
            if not msg:
                break
            print_msg(msg)
        except:
            print_msg("[Connection lost]")
            break

def send_input(_):
    msg = input_field.text.strip()
    if msg:
        sock.send(msg.encode())
        if msg.lower() == '/exit':
            app.exit()
    input_field.text = ""

# Key bindings
kb = KeyBindings()
@kb.add('enter')
def _(event):
    send_input(event)

# Layout and styling
layout = Layout(HSplit([chat_display, input_field]))
style = Style.from_dict({
    "output-field": "bg:#1e1e1e #ffffff",
    "input-field": "bg:#000000 #00ff00"
})

# Build app
app = Application(layout=layout, key_bindings=kb, full_screen=True, style=style)

# Run chat thread
threading.Thread(target=receive_messages, daemon=True).start()
app.run()
