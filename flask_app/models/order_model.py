from flask_app.config.mysqlconnection import connectToMySQL 
from flask_app.models import user_model, product_model
from flask_app import DB
from flask import flash, session
from decimal import Decimal

class Order:
    def __init__( self , data ):
        self.id = data['id']
        self.order_date = data['order_date']
        self.ship_price = data['ship_price']
        self.ship_email = data['ship_email']
        self.ship_phone = data['ship_phone']
        self.ship_name = data['ship_name']
        self.ship_address = data['ship_address']
        self.ship_country = data['ship_country']
        self.ship_city = data['ship_city']
        self.ship_state = data['ship_state']
        self.ship_zip = data['ship_zip']
        self.user_id = session['user_id']
        self.total_price = data['total_price']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        if data['details']:
            self.details = data['details']

# class methods

    @classmethod
    def save(cls, **data ):
        query = """
            INSERT INTO orders ( order_date, ship_price, ship_email, ship_phone, ship_name, ship_address, ship_country, ship_city, ship_state, ship_zip, user_id, total_price, created_at, updated_at ) 
            VALUES ( NOW(), %(ship_price)s, %(ship_email)s, %(ship_phone)s, %(ship_name)s, %(ship_address)s, %(ship_country)s, %(ship_city)s, %(ship_state)s, %(ship_zip)s, %(user_id)s, %(total_price)s, NOW(), NOW() );
            """
        # Calculate the total price of the order
        ship_price = Decimal('6.57')
        total_price = ship_price # start with the shipping price
        prods_in_cart = []
        cart = session.get('cart', {})
        for product_id in cart:
            product = product_model.Product.get_one(product_id)
            if product:
                product.quantity = cart[product_id]
                prods_in_cart.append(product)
        for product in prods_in_cart:
            total_price += product.price * product.quantity # add the price of each item
        tax = total_price * Decimal('0.0875') # calculate the tax as 8.75% of the total price
        total_price += tax # add the tax to the total price
        ship_price = round(ship_price, 2)
        ship_price = str(ship_price)
        total_price = round(total_price, 2)
        total_price = str(total_price)
        order_data = {
            "ship_price": ship_price,
            "ship_email": data["ship_email"],
            "ship_phone": data["ship_phone"],
            "ship_name": data["ship_name"],
            "ship_address": data["ship_address"],
            "ship_country": data["ship_country"],
            "ship_city": data["ship_city"],
            "ship_state": data["ship_state"],
            "ship_zip": data["ship_zip"],
            "user_id": session["user_id"],
            "total_price": total_price,
        }
        # Insert order record into the database and retrieve the ID of the newly inserted order
        order_id = connectToMySQL(DB).query_db(query, order_data)
        # Insert order details for each product into the database
        for product in prods_in_cart:
            query = """
                INSERT INTO order_details ( order_id, product_id, price, quantity ) 
                VALUES ( %(order_id)s, %(product_id)s, %(price)s, %(quantity)s );
                """
            product_data = {
                "order_id": order_id,
                "product_id": product.id,
                "price": product.price,
                "quantity": product.quantity,
            }
            connectToMySQL(DB).query_db(query, product_data)
        # Clear the user's cart
        session.pop('cart', None)
        order_obj = {
            'id': order_id,
            **order_data
            }
        return order_obj

# retrieves 1 order record from the database with all of its associated details, such as the products that were ordered.
    @classmethod
    def get_with_details(cls, order_id):
        order = connectToMySQL(DB).query_db('SELECT * FROM orders WHERE id = %s', (order_id,))[0]
        if not order:
            return None
        order_details = connectToMySQL(DB).query_db('SELECT * FROM order_details WHERE order_id = %s', (order_id,))
        products = []
        for row in order_details:
            product = connectToMySQL(DB).query_db('SELECT * FROM products WHERE id = %s', (row['product_id'],))[0]
            products.append({
                'id': product['id'],
                'name': product['name'],
                'price': row['price'],
                'quantity': row['quantity']
            })
        return {
            'id': order['id'],
            'total_price': order['total_price'],
            'order_date': order['order_date'],
            'ship_price': order['ship_price'],
            'ship_email': order['ship_email'],
            'ship_phone': order['ship_phone'],
            'ship_name': order['ship_name'],
            'ship_address': order['ship_address'],
            'ship_country': order['ship_country'],
            'ship_city': order['ship_city'],
            'ship_state': order['ship_state'],
            'ship_zip': order['ship_zip'],
            'user_id': order['user_id'],
            'created_at': order['created_at'],
            'updated_at': order['updated_at'],
            'products': products
        }

# retrieves ALL order records from the database for a specific user with all of their associated details.
    @classmethod
    def get_all_with_details_for_user(cls, user_id):
        query = """
            SELECT *
            FROM orders o
            JOIN order_details od ON o.id = od.order_id
            JOIN products p ON od.product_id = p.id
            WHERE o.user_id = %(user_id)s;
        """
        data = {
            'user_id': user_id
        }
        results = connectToMySQL(DB).query_db(query, data)
        orders = {}
        for row in results:
            if row['id'] not in orders:
                order_data = {
                    'id': row['id'],
                    'total_price': row['total_price'],
                    'order_date': row['order_date'],
                    'ship_price': row['ship_price'],
                    'ship_email': row['ship_email'],
                    'ship_phone': row['ship_phone'],
                    'ship_name': row['ship_name'],
                    'ship_address': row['ship_address'],
                    'ship_country': row['ship_country'],
                    'ship_city': row['ship_city'],
                    'ship_state': row['ship_state'],
                    'ship_zip': row['ship_zip'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'details': []
                }
                orders[row['id']] = order_data
            detail = {
                'price': row['price'],
                'quantity': row['quantity'],
                'product_id': row['product_id'],
                'product_name': row['name']
            }
            orders[row['id']]['details'].append(detail)
        return [cls(order) for order in orders.values()]


# static methods

    @staticmethod
    def validate_order(data):
        err = {}
        if 'ship_name' in data and len(data['ship_name']) < 3:
            err['ship_name'] = 'Shipping name must be 3 characters or longer.'
        if 'ship_address' in data and len(data['ship_address']) < 3:
            err['ship_address'] = 'Shipping address must be 3 characters or longer.'
        if 'ship_country' in data and data['ship_country'] == '':
            err['ship_country'] = 'Please select a shipping country.'
        if 'ship_city' in data and len(data['ship_city']) < 3:
            err['ship_city'] = 'Shipping city must be 3 characters or longer.'
        if 'ship_state' in data and data['ship_state'] == '':
            err['ship_state'] = 'Please select a shipping state.'
        if 'ship_zip' in data and len(data['ship_zip']) < 5:
            err['ship_zip'] = 'Shipping zip code must be 5 characters or longer.'
        for category, message in err.items():
            flash(message, category)
        return len(err) == 0