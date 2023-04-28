from flask_app.config.mysqlconnection import connectToMySQL 
from flask_app import DB, bcrypt
from flask import flash, request
from flask_app.models import order_model
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User:
    def __init__( self , data ):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.reviews = []
        self.orders = []

# class methods

    @classmethod
    def save(cls, **data ): 
        query = """
            INSERT INTO users ( first_name, last_name, email, password, created_at, updated_at ) 
            VALUES ( %(first_name)s, %(last_name)s, %(email)s, %(password)s, NOW(), NOW() );
            """
        data = {
            **data,
            'password': bcrypt.generate_password_hash(data['password'])
            }
        result = connectToMySQL(DB).query_db(query, data)
        return result

    @classmethod
    def get_one(cls, data):
        data = {
            'id': data
            }
        query = """
            SELECT *
            FROM users
            WHERE id = %(id)s;
            """
        result = connectToMySQL(DB).query_db(query, data)
        return cls( result[0] )

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"
        results = connectToMySQL(cls.DB).query_db(query)
        users = []
        for i in results:
            users.append( cls(i) )
        return users

    @classmethod
    def edit_user(cls, **data):
        query = """
            UPDATE users SET 
            first_name = %(first_name)s, 
            last_name = %(last_name)s, 
            email = %(email)s,
            password = %(password)s,
            updated_at = NOW() 
            WHERE id = %(id)s;
            """
        data = {
            **data,
            'password': bcrypt.generate_password_hash(data['password'])
            }
        result = connectToMySQL(DB).query_db(query, data)
        return result


# static methods

    @staticmethod
    def validate_user(data):
        query = """
            SELECT *
            FROM users
            WHERE email = %(email)s;
            """
        result = connectToMySQL(DB).query_db(query,data)
        errors = {}
        if 'first_name' in data and len(data['first_name']) < 2:
            errors['first_name'] = "First name must be at least 2 characters."
        if 'first_name' in data and not data['first_name'].isalpha():
            errors['first_name'] = "First name can contain letters only."
        if 'last_name' in data and len(data['last_name']) < 2:
            errors['last_name'] = "Last name must be at least 2 characters."
        if 'last_name' in data and not data['last_name'].isalpha():
            errors['last_name'] = "Last name can contain letters only."
        if 'email' in data and len(data['email']) == 0:
            errors['email'] = "Email is a required for registration."
        if 'email' in data and not EMAIL_REGEX.match(data['email']): 
            errors['email'] = "Invalid email address!"
        if result:
            errors['email'] = "Email already registered."
        if 'password' in data and len(data['password']) < 2:
            errors['password'] = "Password must be at least 8 characters"
        if 'password' in data and 'confirm_password' in data and data['confirm_password'] != data['password']:
            errors['password'] = "Password fields do not match"
        return errors

    @staticmethod
    def validate_update(data):
        errors = {}
        if 'first_name' in data and len(data['first_name']) < 2:
            errors['first_name'] = "First name must be at least 2 characters."
        if 'first_name' in data and not data['first_name'].isalpha():
            errors['first_name'] = "First name can contain letters only."
        if 'last_name' in data and len(data['last_name']) < 2:
            errors['last_name'] = "Last name must be at least 2 characters."
        if 'last_name' in data and not data['last_name'].isalpha():
            errors['last_name'] = "Last name can contain letters only."
        if 'email' in data and len(data['email']) == 0:
            errors['email'] = "Email is a required for registration."
        if 'email' in data and not EMAIL_REGEX.match(data['email']): 
            errors['email'] = "Invalid email address!"
        if 'password' in data and len(data['password']) < 2:
            errors['password'] = "Password must be at least 8 characters"
        if 'password' in data and 'confirm_password' in data and data['confirm_password'] != data['password']:
            errors['password'] = "Password fields do not match"
        return errors

    @staticmethod
    def validate_login(data):
        y = [1, 2]
        query = """
            SELECT * 
            FROM users 
            WHERE email = %(email)s;
            """
        result = connectToMySQL(DB).query_db(query, data)
        if type(result) != type(y):
            flash('Email/Password not valid')
            return False
        user = User(result[0])
        if not EMAIL_REGEX.match(data['email']):
            flash('Email/Password not valid')
            return False
        if len(data['password']) < 8:
            flash('Email/Password not valid')
            return False
        if not result:
            flash('Email/Password not valid')
            return False
        if not bcrypt.check_password_hash(user.password, data['password']):
            flash('Email/Password not valid')
            return False
        return user