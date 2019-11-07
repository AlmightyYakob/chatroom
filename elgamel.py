from random import randint
from crypto.a2.rsa import is_prime


def inefficient_generator(upper_bound):
    pass


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


