from os import getenv
from flask import Flask
from flask_socketio import SocketIO

from utils import param_prompt

app = Flask(__name__)
socketio = SocketIO(app)


host = getenv("SERVER_HOST", default="localhost")
port = int(getenv("SERVER_PORT", default=5000))


@socketio.on("public_keys")
def handle_event():
    socketio.emit("elgamel")


if __name__ == "__main__":
    p_bit_length, secret_key = param_prompt()
    socketio.run(app, host=host, port=port)
