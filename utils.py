import logging
from flask import Flask
from os import getenv
from flask_socketio import SocketIO

from typing import Tuple


def get_server_host_and_port() -> str:
    host = getenv("SERVER_HOST", default="localhost")
    port = int(getenv("SERVER_PORT", default=5000))
    return (host, port)


def get_flask_instance() -> SocketIO:
    app = Flask(__name__)
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    return app


def param_prompt() -> Tuple:
    p_bit_length = int(input("Choose p bit-length: "))
    secret_key = input("Specify secret key: ")

    return (p_bit_length, secret_key)


def connection_prompt() -> str:
    hostname = input("Enter partner ip (with port): ")
    return hostname
