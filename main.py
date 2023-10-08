from util import db_connection


@db_connection()
def additional_image_fetcher(connection):
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
        product_images_dict[product_id]['additional_images'].append(f"https://butopea.com/{image}")

    return product_images_dict


@db_connection()
def product_fetcher(connection):
    cursor = connection.cursor()
    query_string = """
                   SELECT product.product_id AS id,
                          manufacturer.name AS brand,
                          product_description.name AS title,
                          product_description.description,
                          product.image AS image_link,
                          product.quantity AS availability,
                          product.price     
                   FROM PRODUCT
                   
                   INNER JOIN manufacturer ON product.manufacturer_id = manufacturer.manufacturer_id
                   INNER JOIN product_description ON product.product_id = product_description.product_id
                   
                   WHERE product.status <> "0";
                   """
    additional_images = additional_image_fetcher()
    cursor.execute(query_string)
    columns = [column[0] for column in cursor.description] + ["additonal_image_link", "link", "condition"]
    print(columns)
    results = []
    for row in cursor.fetchall():
        try:
            product_images = additional_images[row[0]]
        except:
            product_images = []
            print(f"No additional product images for {row[0]}")
        row = row + (product_images, f"https://butopea.com/p/{row[0]}", "new")
        results.append(dict(zip(columns, row)))
    return results