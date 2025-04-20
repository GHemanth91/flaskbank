# FlaskBank - Banking Web Application

FlaskBank is a simple banking web application built with Flask and SQLAlchemy. It provides basic banking functionalities such as user registration, account management, money transfers, deposits, withdrawals, and transaction history.

## Features

- User registration and login
- Admin login
- User dashboard
- Admin dashboard
- Transfer money between users
- Deposit money
- Withdraw money
- View transaction history
- Admin can view all users
- Admin can view all transactions
- Admin can delete user accounts
- Responsive design with Bootstrap

## Installation

1. Clone the repository:
```
git clone <repository-url>
cd FlaskBank
```

2. Create a virtual environment (recommended Python 3.10 or 3.11):
```
python -m venv venv
```

3. Activate the virtual environment:
   - Windows:
   ```
   venv\Scripts\activate
   ```
   - macOS/Linux:
   ```
   source venv/bin/activate
   ```

4. Install the required packages:
```
pip install -r requirements.txt
```

5. Run the application:
```
python app.py
```

6. Open your browser and navigate to `http://127.0.0.1:5000`

## Default Admin Credentials

- Username: admin
- Password: admin123

You can change these in the `.env` file or directly in the `config.py` file.

## Database

The application uses SQLite by default. The database file will be created in the `instance` folder when you first run the application.

## Project Structure

```
FlaskBank/
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── models.py               # Database models
├── requirements.txt        # Project dependencies
├── static/                 # Static files (CSS, JS, images)
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
└── templates/              # HTML templates
    ├── index.html
    ├── register.html
    ├── login.html
    ├── admin_login.html
    ├── dashboard.html
    ├── admin_dashboard.html
    ├── transfer.html
    ├── deposit.html
    ├── withdraw.html
    ├── transactions.html
    ├── all_users.html
    ├── all_transactions.html
    ├── delete_user.html
    ├── includes/
    │   ├── navbar_user.html
    │   └── navbar_admin.html
    └── layout.html         # Base template
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
