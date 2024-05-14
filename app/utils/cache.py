from pathlib import Path
import hashlib
import json
from functools import wraps
import inspect
import os


text_cache = Path(os.path.join(os.getcwd(), 'cache'))


def sha1(input_string):
    """Helper to hash input strings"""
    try:

        # Step 5: Create a new SHA-1 hash object
        hash_object = hashlib.sha1()

        # Step 6: Update the hash object with the bytes-like object
        hash_object.update(input_string.encode('utf-8'))

        # Step 7: Get the hexadecimal representation of the hash
        return hash_object.hexdigest()
    except Exception as e:
        raise ValueError(input_string) from e


def stored(func):
    """
    implements nix-like durable memoisation of function results.

    Lazy way to avoid recomputing expensive calls. Expects results to be JSON-serializable
    """
    @wraps(func)
    def CACHE(*args, **kwargs):
        name = func.__name__
        meta = {}

        meta["name"] = name
        meta["func"] = inspect.getsource(func)
        # meta["args"] = args
        meta["kwargs"] = kwargs

        js = json.dumps(meta)
        sha = hashlib.sha1(js.encode('utf-8'))

        digest = sha.hexdigest()

        path = text_cache / f"{digest}-{name}.json"

        if path.exists():
            with path.open('r') as r:
                cached = json.load(r)
            return cached["result"]
        result = func(*args, **kwargs)
        meta["result"] = result
        with path.open('w') as w:
            json.dump(meta, w)
        return result

    return CACHE