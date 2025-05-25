# backend_flask/models.py
from flask_login import UserMixin
from flask import current_app
import json # For preferences JSON
from . import db # Import the db module we created

class User(UserMixin):
    def __init__(self, username, id=None, email=None, password_hash=None):
        self.id = id # For SQLite, id will be an integer from autoincrement
        self.username = username
        self.email = email
        self.password_hash = password_hash
        # Preferences, wishlist, cart will be loaded on demand or via helper methods

    # Required by Flask-Login
    def get_id(self):
        return str(self.id) # Flask-Login expects string ID

    @staticmethod
    def get_by_username(username_val):
        database = db.get_db()
        if not database: return None
        cursor = database.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username_val,))
        user_data = cursor.fetchone()
        if user_data:
            # sqlite3.Row allows access by column name
            return User(id=user_data["id"], username=user_data["username"], 
                        email=user_data["email"], password_hash=user_data["password_hash"])
        return None

    @staticmethod
    def get_by_id(user_id):
        database = db.get_db()
        if not database: return None
        try:
            # Flask-Login passes ID as string, convert to int for SQLite
            user_id_int = int(user_id)
            cursor = database.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id_int,))
            user_data = cursor.fetchone()
            if user_data:
                return User(id=user_data["id"], username=user_data["username"], 
                            email=user_data["email"], password_hash=user_data["password_hash"])
        except ValueError: # If user_id cannot be converted to int
            current_app.logger.warning(f"Invalid user_id format for get_by_id: {user_id}")
        except Exception as e:
            current_app.logger.error(f"Error fetching user by ID {user_id}: {e}")
        return None

    # --- Methods for user data, using SQLite ---
    def get_preferences(self):
        database = db.get_db()
        if not database or not self.id: return {}
        cursor = database.cursor()
        cursor.execute("SELECT preferences_json FROM user_preferences WHERE user_id = ?", (self.id,))
        row = cursor.fetchone()
        return json.loads(row["preferences_json"]) if row and row["preferences_json"] else {}

    def save_preferences(self, prefs_dict):
        database = db.get_db()
        if not database or not self.id: return False
        prefs_json = json.dumps(prefs_dict)
        cursor = database.cursor()
        # UPSERT logic: insert if not exists, update if exists
        cursor.execute("""
            INSERT INTO user_preferences (user_id, preferences_json) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET preferences_json = excluded.preferences_json;
        """, (self.id, prefs_json))
        database.commit()
        return True

    def get_wishlist_ids(self):
        database = db.get_db()
        if not database or not self.id: return []
        cursor = database.cursor()
        cursor.execute("SELECT product_id FROM user_wishlist WHERE user_id = ?", (self.id,))
        return [row["product_id"] for row in cursor.fetchall()]

    def add_to_wishlist_db(self, product_id):
        database = db.get_db()
        if not database or not self.id: return False
        try:
            cursor = database.cursor()
            cursor.execute("INSERT OR IGNORE INTO user_wishlist (user_id, product_id) VALUES (?, ?)", (self.id, str(product_id)))
            database.commit()
            return True
        except sqlite3.Error as e:
            current_app.logger.error(f"Error adding to wishlist for user {self.id}, product {product_id}: {e}")
            return False

    def remove_from_wishlist_db(self, product_id):
        database = db.get_db()
        if not database or not self.id: return False
        try:
            cursor = database.cursor()
            cursor.execute("DELETE FROM user_wishlist WHERE user_id = ? AND product_id = ?", (self.id, str(product_id)))
            database.commit()
            return True
        except sqlite3.Error as e:
            current_app.logger.error(f"Error removing from wishlist for user {self.id}, product {product_id}: {e}")
            return False

    def get_cart_items(self): # Returns list of {"product_id": "id", "quantity": int}
        database = db.get_db()
        if not database or not self.id: return []
        cursor = database.cursor()
        cursor.execute("SELECT product_id, quantity FROM user_cart WHERE user_id = ?", (self.id,))
        return [{"product_id": row["product_id"], "quantity": row["quantity"]} for row in cursor.fetchall()]

    def add_to_cart_db(self, product_id, quantity=1):
        database = db.get_db()
        if not database or not self.id: return False
        try:
            cursor = database.cursor()
            # Check if item already in cart to update quantity
            cursor.execute("SELECT quantity FROM user_cart WHERE user_id = ? AND product_id = ?", (self.id, str(product_id)))
            row = cursor.fetchone()
            if row: # Item exists, update quantity
                new_quantity = row["quantity"] + quantity
                if new_quantity <= 0: # If new quantity is 0 or less, remove item
                    self.remove_from_cart_db(product_id)
                else:
                    cursor.execute("UPDATE user_cart SET quantity = ? WHERE user_id = ? AND product_id = ?", (new_quantity, self.id, str(product_id)))
            elif quantity > 0 : # Item not in cart, add new
                cursor.execute("INSERT INTO user_cart (user_id, product_id, quantity) VALUES (?, ?, ?)", (self.id, str(product_id), quantity))
            database.commit()
            return True
        except sqlite3.Error as e:
            current_app.logger.error(f"Error adding/updating cart for user {self.id}, product {product_id}: {e}")
            return False

    def remove_from_cart_db(self, product_id): # Removes entire item
        database = db.get_db()
        if not database or not self.id: return False
        try:
            cursor = database.cursor()
            cursor.execute("DELETE FROM user_cart WHERE user_id = ? AND product_id = ?", (self.id, str(product_id)))
            database.commit()
            return True
        except sqlite3.Error as e:
            current_app.logger.error(f"Error removing from cart for user {self.id}, product {product_id}: {e}")
            return False
            
    def clear_cart_db(self):
        database = db.get_db()
        if not database or not self.id: return False
        try:
            cursor = database.cursor()
            cursor.execute("DELETE FROM user_cart WHERE user_id = ?", (self.id,))
            database.commit()
            return True
        except sqlite3.Error as e:
            current_app.logger.error(f"Error clearing cart for user {self.id}: {e}")
            return False