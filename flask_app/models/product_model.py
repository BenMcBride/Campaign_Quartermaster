from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import DB

class Product:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.description = data['description']
        self.price = data['price']
        self.category_id = data['category_id']
        self.img = data['img']

    @classmethod
    def get_products_by_category(cls, category_name):
        category_query = "SELECT id FROM categories WHERE name = %s"
        connectToMySQL(DB).query_db(category_query, (category_name,))
        query = """
            SELECT products.id, products.name, products.price, products.description, products.img, categories.name AS category_id
            FROM products
            JOIN categories ON products.category_id = categories.id
            WHERE categories.name = %s;
            """
        results = connectToMySQL(DB).query_db(query, (category_name,))
        products = []
        for result in results:
            products.append(cls(result))
        return products
    
    @classmethod
    def get_one(cls, id):
        query = "SELECT * FROM products WHERE id = %(id)s;"
        result = connectToMySQL(DB).query_db(query, {'id': id})
        return cls(result[0])