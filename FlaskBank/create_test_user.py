from app import app, db
from models import User, Account

def create_test_user():
    with app.app_context():
        # Check if test user already exists
        existing_user = User.query.filter_by(email='test@example.com').first()
        if existing_user:
            print("Test user already exists.")
            return
        
        # Create test user
        test_user = User(
            name='Test User',
            email='test@example.com',
            phone='1234567890',
            password='password123'
        )
        db.session.add(test_user)
        db.session.flush()  # Flush to get the user ID
        
        # Create account for the test user
        test_account = Account(user_id=test_user.id, balance=1000.0)
        db.session.add(test_account)
        
        db.session.commit()
        print("Test user created successfully.")
        print("Email: test@example.com")
        print("Password: password123")

if __name__ == "__main__":
    create_test_user()
