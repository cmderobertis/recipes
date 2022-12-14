from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import recipe
from flask_app import flash, session
import re


DATABASE = 'recipes'
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


class User:
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.recipes = []

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"
        results = connectToMySQL(DATABASE).query_db(query)
        users = []
        for user in results:
            users.append(cls(user))
        return users

    @classmethod
    def save(cls, data):
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s, NOW(), NOW());"
        return connectToMySQL(DATABASE).query_db(query, data)

    @classmethod
    def get_one(cls, data):
        query = "SELECT * FROM users WHERE id = %(id)s;"
        result = connectToMySQL(DATABASE).query_db(query, data)
        user = User(result[0])
        return user

    @classmethod
    def update(cls, data):
        query = "UPDATE users SET first_name = %(first_name)s, last_name = %(last_name)s, email = %(email)s WHERE id = %(id)s;"
        return connectToMySQL(DATABASE).query_db(query, data)

    @classmethod
    def delete(cls, data):
        query = "DELETE FROM users WHERE id = %(id)s;"
        return connectToMySQL(DATABASE).query_db(query, data)

    @classmethod
    def get_by_email(cls, data):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        result = connectToMySQL(DATABASE).query_db(query, data)
        # no matching user
        if len(result) < 1:
            return False
        return cls(result[0])

    @classmethod
    # note, if you need to get user with recipes directly associated with them, copy this and change the query to connect users directly to recipes
    def get_user_with_recipes(cls, data):
        query = "SELECT * FROM users LEFT JOIN favorites ON favorites.user_id = users.id LEFT JOIN recipes ON favorites.recipe_id = recipes.id WHERE users.id = %(id)s;"
        results = connectToMySQL(DATABASE).query_db(query, data)
        # results will be a list of user objects with the recipe attached to each row.
        user = cls(results[0])
        # print(user)
        for row_from_db in results:
            # Now we parse the user data to make instances of users and add them into our list.
            recipe_data = {
                "id": row_from_db["recipes.id"],
                'user_id': row_from_db["recipes.user_id"],
                "name": row_from_db["name"],
                "description": row_from_db["description"],
                'instructions': row_from_db["instructions"],
                'date_made': row_from_db["date_made"],
                'under_30': row_from_db["under_30"],
                "created_at": row_from_db["recipes.created_at"],
                "updated_at": row_from_db["recipes.updated_at"]
            }
            # Only append to recipes list if the recipe exists.
            print(row_from_db)
            if row_from_db['name']:
                user.recipes.append(recipe.Recipe(recipe_data))
        return user

    # @classmethod
    # def get_user_without_recipes(cls, data):
    #     query = "SELECT * FROM users LEFT JOIN favorites ON favorites.user_id = users.id LEFT JOIN recipes ON favorites.recipe_id != recipes.id WHERE users.id = %(id)s;"
    #     results = connectToMySQL(DATABASE).query_db(query, data)
    #     # results will be a list of user objects with the recipe attached to each row.
    #     user = cls(results[0])
    #     # print(user)
    #     for row_from_db in results:
    #         # Now we parse the user data to make instances of users and add them into our list.
    #         recipe_data = {
    #             "id": row_from_db["recipes.id"],
    #             'user_id': row_from_db["recipes.user_id"],
    #             "name": row_from_db["name"],
    #             "description": row_from_db["description"],
    #             'instructions': row_from_db["instructions"],
    #             'date_made': row_from_db["date_made"],
    #             'under_30': row_from_db["under_30"],
    #             "created_at": row_from_db["recipes.created_at"],
    #             "updated_at": row_from_db["recipes.updated_at"]
    #         }
    #         # Only append to recipes list if the recipe exists.
    #         print(row_from_db)
    #         if row_from_db['name']:
    #             user.recipes.append(recipe.Recipe(recipe_data))
    #     return user

    @classmethod
    def get_users_and_recipes(cls, data):
        query = "SELECT * FROM users LEFT JOIN favorites ON favorites.user_id = users.id LEFT JOIN recipes ON favorites.recipe_id = recipes.id WHERE users.id = %(id)s;"
        results = connectToMySQL(DATABASE).query_db(query, data)
        # results will be a list of user objects with the recipe attached to each row.
        user = cls(results[0])
        print(user)
        for row_from_db in results:
            # Now we parse the user data to make instances of users and add them into our list.
            recipe_data = {
                "id": row_from_db["recipes.id"],
                "name": row_from_db["name"],
                "description": row_from_db["description"],
                'instructions': row_from_db["instructions"],
                'date_made': row_from_db["date_made"],
                'under_30': row_from_db["under_30"],
                "created_at": row_from_db["recipes.created_at"],
                "updated_at": row_from_db["recipes.updated_at"]
            }
        return user

    @staticmethod
    def validate_user(form: dict) -> bool:
        is_valid = True
        if len(form['first_name']) < 2:
            is_valid = False
            flash('Name must be at least 2 characters', 'first_name')
        if not form['first_name'].isalpha():
            is_valid = False
            flash('Only letters are allowed', 'first_name')
        if len(form['last_name']) < 2:
            is_valid = False
            flash('Name must be at least 2 characters', 'last_name')
        if not form['last_name'].isalpha():
            is_valid = False
            flash('Only letters are allowed.', 'last_name')
        if not EMAIL_REGEX.match(form['email']):
            is_valid = False
            flash('Invalid email address.', 'email')
        if not 'user_id' in session:
            data = {'email': form['email']}
            user_in_db = User.get_by_email(data)
            if user_in_db:
                is_valid = False
                flash('Email is already in use. Try using it to log in.', 'email')
        if 'password' in form:
            if form['password'] != form['password_confirmation']:
                is_valid = False
                flash('Passwords must match.', 'password')
            if len(form['password']) < 8:
                is_valid = False
                flash('Password must be at least 8 characters.', 'password')
        return is_valid
