from app import app, db, create_tables
import os

# Path to the database file
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'flaskbank.db')

# Delete the database file if it exists
if os.path.exists(db_path):
    print(f"Removing existing database: {db_path}")
    os.remove(db_path)
    print("Database removed.")
else:
    print("No existing database found.")

# Create new database tables
with app.app_context():
    print("Creating new database tables...")
    create_tables()
    print("Database tables created successfully.")

print("Database reset complete.")
