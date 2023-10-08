# Product feed
## Description
This project generates a product feed from a sqlite file. The feed is generated in XML format and is saved as `output/feed.xml`.

## Requirements
- Python 3.6+

## Installation
```bash
git clone git@github.com:SamerMakni/product_feed.git`
cd product_feed
```


## Usage
```bash
python3 main.py
```
The feed will be generated in `output/feed.xml`

## Explanation of files and directories
- `main.py`: The main file of the project. It contains the main function that ru,s when the project is executed.
- `config.py`: Contains the configuration of the project. It contains the path to the sqlite file and the path to the output directory.
- `README.md`: This file.
- `utils.py`: Contains utility functions.
- `data/`: Contains the sqlite file.
- `output/`: The directory where the feed is saved.

## Explanation of the code
- `utils.py`:
    - `db_connection()`:
        - We use this decorator function to add a level of abstraction to the connection to the sqlite file. Ensuring reusability and automatic closing of the connection.
        1. `db_connection` function takes an optional argument `db_location` which defaults to `config.database`.
        2. function `func`, which is the function that will be decorated.
        3. `wraps(func)` is a decorator from the functools module.
        4. `wrapper` function takes any number of arguments, inside this function we establish the connection to the sqlite file. Then `func` is executed, the with statement in the wrapper function ensures that the connection is automatically closed.

    - `validate_product()`:
        - This function validates a product according to Google Merchant product data specifications, the specifications can be found [here](https://support.google.com/merchants/answer/7052112?hl=en).

- `main.py`:
    - The main function of the project is `main()`. Explanation of each function below.
    - `additional_image_fetcher()`:
        1. `@db_connection()` is a decorator that will open a connection to the database before function execution and will close the connection after function execution. The connection object is passed to the function as the first parameter.
        2. The query will fetch only the active products (status different than 0).
        3. The query will return a list of tuples. Each tuple will contain the product_id and the image path.
        4. The function will return a dictionary where the keys are the product ids and the values are dictionaries with the product_id and a list of additional image paths, we do this this step to simplify the access to the data. (using keys in this case, rather than using indexes in the case of lists).
    - `product_fetcher()`:
        1. We decorate the function just like the previous function.
        2. The query will fetch all information about the products, except the additional images. since we will fetch them in the previous function. The use of `CASE WHEN` is to convert the availability column to the required format.
        3. We create a dictionary from the zip of the columns and the row.
        4. We check if the product conforms to the specifications using the `validate_product()` function.
        5. The funtion logs the product id and the error message if the product does not conform to the Google Merchant product specifications.
        5. If the product is valid we append it to the results list.
    - `feed_generator()` to generate the feed.
        1. This functions takes a list of products as input, the list is the result of the `product_fetcher()` function.
        2. The function generates an XML feed document using the minidom module and appends various elements to it based on the product data. An alternative method of generating this XML that I have tried is using `dict2xml` libray, but I found it to be much less flexible than using the minidom module.
        4. The sturcture of this XML is based on atom feed sturcture, the specifications can be found [here](https://validator.w3.org/feed/docs/atom.html).
        5. The function writes the generated XML to a file specified in the config file, defaults to `output/feed.xml`.
