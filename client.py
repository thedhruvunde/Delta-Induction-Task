import socket
import threading
from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, HSplit
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

HOST = '127.0.0.1'
PORT = 5555

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

# --- Phase 1: Setup using normal input/output ---
def blocking_input_phase():
    while True:
        server_msg = sock.recv(1024).decode()
        print(server_msg, end='')  # print server message
        user_input = input()       # get user input
        sock.send(user_input.encode())
        if "Created and joined" in server_msg or "Joined" in server_msg:
            break

blocking_input_phase()

# --- Phase 2: Real-time chat with prompt_toolkit UI ---

# UI elements
chat_display = TextArea(style="class:output-field", scrollbar=True, wrap_lines=True, read_only=True)
input_field = TextArea(height=1, prompt='> ', style="class:input-field", multiline=False)

def print_msg(msg):
    chat_display.buffer.insert_text(msg + '\n', move_cursor_to_end=True)

def receive_messages():
    while True:
        try:
            msg = sock.recv(1024).decode()
            if not msg:
                break
            print_msg(msg)
        except Exception as e:
            print_msg(f"[Connection Error: {e}]")
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

# Layout
layout = Layout(HSplit([chat_display, input_field]), focused_element=input_field)

# Style
style = Style.from_dict({
    "output-field": "bg:#1e1e1e #ffffff",
    "input-field": "bg:#000000 #00ff00"
})

# App
app = Application(layout=layout, key_bindings=kb, full_screen=True, style=style)

# Start receiving messages
threading.Thread(target=receive_messages, daemon=True).start()
app.run()
