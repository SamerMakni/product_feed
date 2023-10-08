import sqlite3
from functools import wraps
import config

def db_connection(db_location=config.database):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with sqlite3.connect(db_location) as db_conn:
                rv = func(db_conn, *args, **kwargs)
            return rv
        return wrapper
    return decorator


def validate_product(product):
    if not (product.get('id') and 1 <= len(product['id']) <= 50):
        return False
    
    if not (product.get('title') and 1 <= len(product['title']) <= 150):
        return False
    
    if not (product.get('description') and 1 <= len(product['description']) <= 5000):
        return False
    
    additional_images = product.get('additional_image_link', [])
    if not len(additional_images) <= 10:
        return False
    if not all(isinstance(img, str) and 1 <= len(img) <= 2000 for img in additional_images):
        return False
    
    valid_availabilities = ['In stock', 'Out of stock', 'Preorder', 'Backorder']
    if product.get('availability') not in valid_availabilities:
        return False
    
    price = product.get('price')
    if not (price and price.replace('.', '', 1).isdigit() and float(price) != 0 and len(price.split('.')[1]) == 4):
        return False
    
    if not (product.get('brand') and 1 <= len(product['brand']) <= 70):
        return False
    return True