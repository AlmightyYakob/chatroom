import os
import sys
import socketio

from elgamel import generate_keys
from utils import param_prompt

# sio = socketio.AsyncClient()
sio = socketio.Client()

SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_PORT = os.getenv("SERVER_PORT")
ip = sys.argv[1] if len(sys.argv) > 1 else f"http://{SERVER_HOST}:{SERVER_PORT}"

p_bit_length, secret_key = param_prompt()
p, g, b, a = generate_keys(p_bit_length)

sio.connect(ip)
sio.emit("public_keys", data={"p": p, "g": g, "b": b})


@sio.on("public_keys")
def handle(data):
    print("CLIENT", data)
