import sqlite3
from functools import wraps

def db_connection(db_location="./data.sqlite"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with sqlite3.connect(db_location) as db_conn:
                rv = func(db_conn, *args, **kwargs)
            return rv
        return wrapper
    return decorator
