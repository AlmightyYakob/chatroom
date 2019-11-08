from random import randint
from crypto.a2.rsa import is_prime, pulverizer

# from Crypto.Cipher import AES

from typing import Iterable


def generator(p):
    """
    fast way to do a generator
    let p = 2q + 1 where q = (p-1) / 2
    test: if g ≠ 1 and g^2 ≠ 1 and g^q ≠ 1 then g is a generator
    note: there are gonig to be p/2 valid generators so just picking
    a random number to test is probably the best way to do it
    """
    q = int((p - 1) / 2)

    valid = False
    while not valid:
        g = randint(2, p - 1)  # pick a random number to test, dont include 1
        if pow(g, 2, p) != 1 and pow(g, q, p) != 1:
            valid = True

    return g


def generate_keys(key_length: int):
    """
    Generates the (p, g, b, a), with p being key_length bits large.
    Returns Tuple of (p, g, b, a) if successful, or (None, None, None, None) if not.
    """

    lower = pow(2, key_length - 1)
    upper = pow(2, key_length) - 1

    p = randint(lower, upper) | 1
    while not is_prime(p):
        p = randint(lower, upper) | 1

    g = generator(p)
    a = randint(1, p - 1)  # a is secret
    b = pow(g, a, p)

    return (p, g, b, a)


def encrypt_message(msg: str, pubkeys: Iterable[int]) -> Iterable[Iterable[int]]:
    p, g, b = pubkeys
    encrypted = []

    for char in msg:
        beta = randint(1, p - 1)
        half_mask = pow(g, beta, p)
        full_mask = pow(b, beta, p)

        cipher = ord(char) * full_mask % p

        encrypted.append((cipher, half_mask))

    return encrypted


def decrypt_message(msg: Iterable[Iterable[int]], a: float, p: float) -> str:
    decrypted = []

    for cipher, half_mask in msg:
        _, _, temp = pulverizer(p, pow(half_mask, a, p))
        x = cipher * temp % p
        decrypted.append(chr(x))

    return "".join(decrypted)
