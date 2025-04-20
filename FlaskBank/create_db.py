import pymysql

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
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS flaskbank")
        print("Database 'flaskbank' created or already exists.")
    
    connection.close()
    print("Database setup completed successfully.")
    
except Exception as e:
    print(f"Error: {e}")
