from random import randint
from crypto.a2.rsa import is_prime


def inefficient_generator(p):
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

    g = inefficient_generator(p)  # get the generator
    a = randint(1, p - 1)  # this is the secret key
    b = pow(g, a, p)

    return (p, g, b, a)
