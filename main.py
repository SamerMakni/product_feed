from utils import db_connection, validate_product
from xml.dom import minidom 
import time
import config
import os

@db_connection()
def additional_image_fetcher(connection):
    """
    Fetch product information from the database and prepare it for export.
    
    Args:
        connection: Database connection object.

    Returns:
        dict: A dictionary where keys are product IDs and values are dictionaries containing
              product information including the product ID and a list of additional image URLs.
              Example: 
              {
                  'product_id': {
                      'id': 'product_id',
                      'additional_images': ['image_url1', 'image_url2', ...]
                  },
                  ...
              }
    """
    cursor = connection.cursor()
    query_string = """
                    SELECT product_image.product_id,
                           product_image.image
                    FROM product_image
                    
                    INNER JOIN product ON product.product_id = product_image.product_id

                    WHERE product.status <> "0"
                    ORDER BY product_image.sort_order
                   """
    cursor.execute(query_string)
    rows = cursor.fetchall()

    product_images_dict = {}
    for row in rows:
        product_id, image = row
        if product_id not in product_images_dict:
            product_images_dict[product_id] = {'id': product_id, 'additional_images': []}
        product_images_dict[product_id]['additional_images'].append(f"{config.base_url}/{image}")
    return product_images_dict



@db_connection()
def product_fetcher(connection):
    """
    Fetch product information from the database and prepare it for further use.

    Args:
        connection: Database connection object.

    Returns:
        list: A list of dictionaries containing product information. Each dictionary represents a product 
              and includes the following keys:
               ['id','brand','title','description','image_link','availability','price','additional_image_link','link','condition','currency']
    """
    cursor = connection.cursor()
    query_string = """
                   SELECT product.product_id AS id,
                          manufacturer.name AS brand,
                          product_description.name AS title,
                          product_description.description,
                          product.image AS image_link,                   
                          CASE
                            WHEN product.quantity > 0 THEN 'In stock'
                            ELSE 'Out of stock'
                          END AS availability,
                          product.price     
                   FROM PRODUCT
                   
                   INNER JOIN manufacturer ON product.manufacturer_id = manufacturer.manufacturer_id
                   INNER JOIN product_description ON product.product_id = product_description.product_id

                   WHERE product.status <> "0";
                   """
    additional_images = additional_image_fetcher()
    cursor.execute(query_string)
    columns = [column[0] for column in cursor.description] + ["additional_image_link", "link", "condition", "currency"]
    print(columns)
    results = []
    for row in cursor.fetchall():
        try:
            product_images = additional_images[row[0]]
        except:
            product_images = []
        row = row + (product_images, f"{config.base_url}/p/{row[0]}", "new", "HUF")
        product = dict(zip(columns, row))
        valid_row = validate_product(product)
        if valid_row:
            results.append(product)
        else:
            print(f"Product {product['id']} does not conform to Google Merchant specifications (check validate_product in utils.py).")
    return results


def feed_generator(products):
    """
    Generate an XML product feed.

    Args:
        products (list): A list of dictionaries containing product information. 
    Returns:
        None
    """
    root = minidom.Document()  
    xml = root.createElement('feed')  
    xml.setAttribute('xmlns', 'http://www.w3.org/2005/Atom')
    xml.setAttribute('xmlns:g', 'http://base.google.com/ns/1.0')
    root.appendChild(xml)

    title = root.createElement('title')
    title.appendChild(root.createTextNode('Product Feed'))
    xml.appendChild(title)

    link = root.createElement('link')
    link.setAttribute('href', config.base_url)
    xml.appendChild(link)

    updated = root.createElement('updated')
    updated.appendChild(root.createTextNode(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
    xml.appendChild(updated)

    for product in products:
        entry = root.createElement('entry')
        xml.appendChild(entry)

        id = root.createElement('g:id')
        id.appendChild(root.createTextNode(product['id']))
        entry.appendChild(id)

        title = root.createElement('g:title')
        title.appendChild(root.createTextNode(product['title']))
        entry.appendChild(title)

        description = root.createElement('g:description')
        description.appendChild(root.createTextNode(product['description']))
        entry.appendChild(description)

        link = root.createElement('g:link')
        link.appendChild(root.createTextNode(product['link']))
        entry.appendChild(link)

        image_link = root.createElement('g:image_link')
        image_link.appendChild(root.createTextNode(f"{config.base_url}/{product['image_link']}"))
        entry.appendChild(image_link)
        try:
            additional_images = product['additional_image_link']['additional_images']
            for additional_image_link in additional_images:
                additional_image_linkNode = root.createElement('g:additional_image_link')
                additional_image_linkNode.appendChild(root.createTextNode(additional_image_link))
                entry.appendChild(additional_image_linkNode)      
        except:
            pass
        availability = root.createElement('g:availability')
        availability.appendChild(root.createTextNode(product['availability']))
        entry.appendChild(availability)

        price = root.createElement('g:price')
        price.appendChild(root.createTextNode(f"{product['price']} {product['currency']}"))
        entry.appendChild(price)

        brand = root.createElement('g:brand')
        brand.appendChild(root.createTextNode(product['brand']))
        entry.appendChild(brand)

        condition = root.createElement('g:condition')
        condition.appendChild(root.createTextNode(product['condition']))
        entry.appendChild(condition)

    xml_str = root.toprettyxml(indent ="\t")
    os.makedirs(os.path.dirname(config.file_output), exist_ok=True)
    with open(config.file_output, "w") as f: 
        f.write(xml_str) 
        print(f"Succefully created {config.file_output}")


feed_generator(product_fetcher())