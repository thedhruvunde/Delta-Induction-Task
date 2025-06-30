import socket
import threading
from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, HSplit
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML

HOST = '127.0.0.1'
PORT = 5555

# Create UI components
chat_display = TextArea(style="class:output-field", scrollbar=True, wrap_lines=True, read_only=True)
input_field = TextArea(height=1, prompt='> ', style="class:input-field")

# Append message to chat box
def print_msg(message):
    chat_display.text += message + '\n'

# Socket and networking
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

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

# Layout
layout = Layout(HSplit([chat_display, input_field]))
style = Style.from_dict({
    "output-field": "bg:#1e1e1e #ffffff",
    "input-field": "bg:#000000 #00ff00"
})

# App
app = Application(layout=layout, key_bindings=kb, full_screen=True, style=style)

# Start receiver thread and run app
threading.Thread(target=receive_messages, daemon=True).start()
app.run()
