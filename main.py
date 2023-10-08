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