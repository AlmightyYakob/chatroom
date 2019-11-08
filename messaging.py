import threading
import socketio
import time
from flask_socketio import SocketIO

from utils import (
    param_prompt,
    connection_prompt,
    get_flask_instance,
    get_server_host_and_port,
)
from elgamel import generate_keys, encrypt_message, decrypt_message


class Messager:
    """Client that runs a SocketIO Client and Server for two way communication."""

    def __init__(self):
        self.p_bit_length, self.aes_secret_key = param_prompt()
        self.p, self.g, self.b, self.a = generate_keys(self.p_bit_length)
        self.partner_pubkeys = None

    def set_pubkeys(self, data):
        self.partner_pubkeys = (data["p"], data["g"], data["b"])

    def print_message(self, data):
        print("other person =>", decrypt_message(data, self.a, self.p))

    def message_loop(self, sio):
        while not self.partner_pubkeys:
            time.sleep(1)

        while True:
            text = input()
            encrypted = encrypt_message(text, pubkeys=(self.partner_pubkeys))
            self.sio.emit("message", data=encrypted)


class MessagingServer(Messager):
    def __init__(self):
        super().__init__()
        self.host, self.port = get_server_host_and_port()
        self.app = get_flask_instance()
        self.sio = SocketIO(self.app)

        self.sio.on_event("public_keys", self.return_pubkeys)
        self.sio.on_event("message", self.print_message)

    def start_server(self):
        self.sio.run(self.app, host=self.host, port=self.port)

    def return_pubkeys(self, data):
        self.set_pubkeys(data)
        self.sio.emit("public_keys", data={"p": self.p, "g": self.g, "b": self.b})

    def start(self):
        threading.Thread(target=self.start_server).start()
        self.message_loop(self.sio)


class MessagingClient(Messager):
    def __init__(self):
        super().__init__()
        self.sio = socketio.Client()
        self.sio.on("public_keys", handler=self.set_pubkeys)
        self.sio.on("message", handler=self.print_message)

    def start(self):
        ip = connection_prompt()
        self.sio.connect(f"http://{ip}")
        self.sio.emit("public_keys", data={"p": self.p, "g": self.g, "b": self.b})
        self.message_loop(self.sio)
