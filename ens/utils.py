
from web3 import Web3


def dict_copy(func):
    "copy dict keyword args, to avoid modifying caller's copy"
    def proxy(*args, **kwargs):
        new_kwargs = {}
        for var in kwargs:
            if isinstance(kwargs[var], dict):
                new_kwargs[var] = dict(kwargs[var])
            else:
                new_kwargs[var] = kwargs[var]
        return func(*args, **new_kwargs)
    return proxy


def ensure_hex(data):
    if isinstance(data, (bytes, bytearray)):
        return Web3.toHex(data)
    return data
