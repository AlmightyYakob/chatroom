import threading
import socketio
import time
from flask_socketio import SocketIO
from Crypto.Cipher import AES

from utils import (
    bit_length_prompt,
    secret_key_prompt,
    connection_prompt,
    get_flask_instance,
    get_server_host_and_port,
)
from elgamel import generate_keys, encrypt_message, decrypt_message


BYTE_ENCODING = "utf-8"
AES_TEXT_PAD_CHAR = "\0"
AES_TEXT_PAD_BYTE = bytes(AES_TEXT_PAD_CHAR, encoding=BYTE_ENCODING)

# Event Names
EVENT_AES_KEY = "AES_KEY"
EVENT_MESSAGE = "MESSAGE"
EVENT_PUBLIC_KEYS = "PUBLIC_KEYS"
EVENT_KEYS_EXCHANGED = "KEYS_EXCHANGED"


def unpad_aes_text(text: bytes, pad_char: str = AES_TEXT_PAD_CHAR) -> str:
    decoded = text.decode(encoding=BYTE_ENCODING)

    if (len(decoded) % 16) != 0:
        decoded = decoded[: decoded.index(pad_char)]

    return decoded


def pad_aes_text(text: str, pad_byte: bytes = AES_TEXT_PAD_BYTE) -> bytes:
    byte_text = bytes(text, encoding=BYTE_ENCODING)
    pad_length = (16 - len(byte_text)) % 16
    padded = byte_text + pad_byte * pad_length
    return padded


def padded_aes_key(key: str, pad_byte: bytes = AES_TEXT_PAD_BYTE) -> bytes:
    key = bytes(key, encoding=BYTE_ENCODING)
    pad_lengths = list(
        filter(lambda x: x >= 0, map(lambda x: x - len(key), [16, 24, 32]))
    )

    if not pad_lengths:
        raise Exception("Provided key is too long, must be no longer than 32 bytes.")

    pad_length = pad_lengths[0]
    padded = key + pad_byte * pad_length

    return padded


class Messager:
    """Client that runs a SocketIO Client and Server for two way communication."""

    def __init__(self):
        self.p_bit_length = bit_length_prompt()

        self.p, self.g, self.b, self.a = generate_keys(self.p_bit_length)
        self.pubkeys = (self.p, self.g, self.b)

        self.partner_pubkeys = None
        self.aes_cipher = None
        self.aes_secret_key = None

        self.all_keys_exchanged = False

    def set_aes_cipher(self):
        self.aes_cipher = AES.new(self.aes_secret_key)

    def set_keys_exchanged(self, *args, **kwargs):
        self.all_keys_exchanged = True
        print(f"{'-'*5}SESSION ESTABLISHED{'-'*5}")

    def set_pubkeys(self, data):
        self.partner_pubkeys = (data["p"], data["g"], data["b"])

    def print_message(self, data):
        if data:
            print("[Chat Partner]", unpad_aes_text(self.aes_cipher.decrypt(data)))

    def message_loop(self, sio):
        while not self.all_keys_exchanged:
            time.sleep(0.1)

        while True:
            text = input()
            padded = pad_aes_text(text)
            encrypted = self.aes_cipher.encrypt(padded)

            self.sio.emit(EVENT_MESSAGE, data=encrypted)


class MessagingServer(Messager):
    def __init__(self):
        super().__init__()
        self.host, self.port = get_server_host_and_port()
        self.app = get_flask_instance()
        self.sio = SocketIO(self.app)

        self.sio.on_event(EVENT_PUBLIC_KEYS, self.return_pubkeys)
        self.sio.on_event(EVENT_AES_KEY, self.unencrypt_and_set_aes_key)
        self.sio.on_event(EVENT_MESSAGE, self.print_message)

    def unencrypt_and_set_aes_key(self, data):
        key = decrypt_message(data, self.a, self.p)
        self.aes_secret_key = key

        self.set_aes_cipher()

        self.set_keys_exchanged()
        self.sio.emit(EVENT_KEYS_EXCHANGED)

    def return_pubkeys(self, data):
        self.set_pubkeys(data)
        self.sio.emit(EVENT_PUBLIC_KEYS, data={"p": self.p, "g": self.g, "b": self.b})

    def start_server(self):
        self.sio.run(self.app, host="0.0.0.0", port=self.port)

    def start(self):
        threading.Thread(target=self.start_server).start()
        self.message_loop(self.sio)


class MessagingClient(Messager):
    def __init__(self):
        super().__init__()
        self.aes_secret_key = padded_aes_key(secret_key_prompt())
        self.set_aes_cipher()

        self.sio = socketio.Client()
        self.sio.on(EVENT_PUBLIC_KEYS, handler=self.set_pubkeys_return_aes_key)
        self.sio.on(EVENT_MESSAGE, handler=self.print_message)
        self.sio.on(EVENT_KEYS_EXCHANGED, handler=self.set_keys_exchanged)

    def set_pubkeys_return_aes_key(self, data):
        self.set_pubkeys(data)
        self.sio.emit(
            EVENT_AES_KEY,
            data=encrypt_message(
                self.aes_secret_key.decode(encoding=BYTE_ENCODING), self.partner_pubkeys
            ),
        )

    def start(self):
        ip = connection_prompt()
        self.sio.connect(f"http://{ip}")

        self.sio.emit(EVENT_PUBLIC_KEYS, data={"p": self.p, "g": self.g, "b": self.b})
        self.message_loop(self.sio)
