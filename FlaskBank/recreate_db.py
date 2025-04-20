import pymysql
import os
import sys

# Add the current directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import after setting the path
from app import app, db, create_tables

# Connect to MySQL server
try:
    # Connect to the MySQL server without specifying a database
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',  # Default XAMPP MySQL has no password
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    with connection.cursor() as cursor:
        # Drop database if it exists
        cursor.execute("DROP DATABASE IF EXISTS flaskbank")
        print("Database 'flaskbank' dropped if it existed.")

        # Create database
        cursor.execute("CREATE DATABASE flaskbank")
        print("Database 'flaskbank' created successfully.")

    connection.close()
    print("Database reset completed.")

    # Create tables using SQLAlchemy models
    with app.app_context():
        db.create_all()
        print("Database tables created successfully.")

        # Create admin account
        create_tables()
        print("Admin account created.")

    print("Database setup completed successfully.")

except Exception as e:
    print(f"Error: {e}")
