import logging
from os import getenv
from flask import Flask
from flask_socketio import SocketIO

from utils import param_prompt
from elgamel import generate_keys, encrypt_message, decrypt_message

app = Flask(__name__)
sio = SocketIO(app)

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

host = getenv("SERVER_HOST", default="localhost")
port = int(getenv("SERVER_PORT", default=5000))

p_bit_length, secret_key = param_prompt()
p, g, b, a = generate_keys(p_bit_length)
client_pubkeys = None


@sio.on("public_keys")
def handle_event(data):
    global client_pubkeys
    client_pubkeys = (data["p"], data["g"], data["b"])
    sio.emit("public_keys", data={"p": p, "g": g, "b": b})


@sio.on("message")
def print_message(data):
    print("client:", decrypt_message(data, a=a, p=p))


if __name__ == "__main__":
    sio.run(app, host=host, port=port)
