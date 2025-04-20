from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from models import db, User, Account, Transaction, Admin, DepositRequest
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
def create_tables():
    with app.app_context():
        db.create_all()
        # Create admin account if it doesn't exist
        admin = Admin.query.filter_by(username=app.config['ADMIN_USERNAME']).first()
        if not admin:
            admin = Admin(username=app.config['ADMIN_USERNAME'],
                        password=app.config['ADMIN_PASSWORD'],
                        verification_code=app.config['ADMIN_VERIFICATION_CODE'])
            db.session.add(admin)
            db.session.commit()
        # Update existing admin with verification code if it doesn't have one
        elif not admin.verification_code:
            admin.verification_code = app.config['ADMIN_VERIFICATION_CODE']
            db.session.commit()

# Routes
@app.route('/')
def index():
    # Render the welcome page without clearing admin session
    print("Welcome page accessed!")
    return render_template('index.html')

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        user_type = request.form.get('user_type')
        admin_code = request.form.get('admin_code')

        # Validate form data
        if not all([name, email, phone, password, confirm_password, user_type]):
            flash('All fields are required', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'danger')
            return render_template('register.html')

        # Check if admin registration and validate admin code
        if user_type == 'admin':
            if not admin_code or len(admin_code) != 5:
                flash('Valid admin verification code is required', 'danger')
                return render_template('register.html')

            # Check if the admin code is valid
            valid_admin = Admin.query.filter_by(verification_code=admin_code).first()
            if not valid_admin:
                flash('Invalid admin verification code', 'danger')
                return render_template('register.html')

        # Create new user
        new_user = User(name=name, email=email, phone=phone, password=password)
        db.session.add(new_user)
        db.session.flush()  # Flush to get the user ID

        # Create account for the user
        new_account = Account(user_id=new_user.id, balance=0.0)
        db.session.add(new_account)

        # If admin registration is successful, create admin account
        if user_type == 'admin' and valid_admin:
            new_admin = Admin(username=email, password=password, verification_code=admin_code)
            db.session.add(new_admin)

        db.session.commit()

        if user_type == 'admin':
            flash('Admin registration successful! Please login as admin.', 'success')
            return redirect(url_for('admin_login'))
        else:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')

# Admin Login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('admin_login.html')

# User Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's account
    account = Account.query.filter_by(user_id=current_user.id).first()

    # Get recent transactions
    recent_transactions = Transaction.query.filter(
        (Transaction.sender_id == current_user.id) |
        (Transaction.receiver_id == current_user.id)
    ).order_by(Transaction.timestamp.desc()).limit(5).all()

    # Get pending deposit requests
    pending_deposit_requests = DepositRequest.query.filter_by(
        user_id=current_user.id,
        status='pending'
    ).order_by(DepositRequest.created_at.desc()).all()

    return render_template('dashboard.html',
                           account=account,
                           transactions=recent_transactions,
                           pending_deposit_requests=pending_deposit_requests)

# Admin Dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        flash('Please login as admin', 'danger')
        return redirect(url_for('admin_login'))

    # Get total users count
    users_count = User.query.count()

    # Get total transactions count
    transactions_count = Transaction.query.count()

    # Get total balance in the system
    total_balance = db.session.query(db.func.sum(Account.balance)).scalar() or 0

    # Get count of pending deposit requests
    pending_deposits_count = DepositRequest.query.filter_by(status='pending').count()

    return render_template('admin_dashboard.html',
                          users_count=users_count,
                          transactions_count=transactions_count,
                          total_balance=total_balance,
                          pending_deposits_count=pending_deposits_count)

# Transfer Money
@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    if request.method == 'POST':
        receiver_email = request.form.get('receiver_email')
        amount = float(request.form.get('amount'))

        # Validate amount
        if amount <= 0:
            flash('Amount must be greater than zero', 'danger')
            return render_template('transfer.html')

        # Get sender's account
        sender_account = Account.query.filter_by(user_id=current_user.id).first()

        # Check if sender has sufficient balance
        if sender_account.balance < amount:
            flash('Insufficient balance', 'danger')
            return render_template('transfer.html')

        # Get receiver's account
        receiver = User.query.filter_by(email=receiver_email).first()
        if not receiver:
            flash('Receiver not found', 'danger')
            return render_template('transfer.html')

        receiver_account = Account.query.filter_by(user_id=receiver.id).first()

        # Update balances
        sender_account.balance -= amount
        receiver_account.balance += amount

        # Create transaction record
        transaction = Transaction(
            sender_id=current_user.id,
            receiver_id=receiver.id,
            amount=amount,
            transaction_type='transfer'
        )

        db.session.add(transaction)
        db.session.commit()

        flash('Transfer successful!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('transfer.html')

# Deposit Money - Create Deposit Request
@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    if request.method == 'POST':
        amount = float(request.form.get('amount'))

        # Validate amount
        if amount <= 0:
            flash('Amount must be greater than zero', 'danger')
            return render_template('deposit.html')

        # Create deposit request
        deposit_request = DepositRequest(
            user_id=current_user.id,
            amount=amount,
            status='pending'
        )

        db.session.add(deposit_request)
        db.session.commit()

        flash('Deposit request submitted! An admin will review your request.', 'success')
        return redirect(url_for('dashboard'))

    # Get pending deposit requests for the user
    pending_requests = DepositRequest.query.filter_by(
        user_id=current_user.id,
        status='pending'
    ).order_by(DepositRequest.created_at.desc()).all()

    return render_template('deposit.html', pending_requests=pending_requests)

# Withdraw Money
@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    if request.method == 'POST':
        amount = float(request.form.get('amount'))

        # Validate amount
        if amount <= 0:
            flash('Amount must be greater than zero', 'danger')
            return render_template('withdraw.html')

        # Get user's account
        account = Account.query.filter_by(user_id=current_user.id).first()

        # Check if user has sufficient balance
        if account.balance < amount:
            flash('Insufficient balance', 'danger')
            return render_template('withdraw.html')

        # Update balance
        account.balance -= amount

        # Create transaction record
        transaction = Transaction(
            sender_id=current_user.id,
            amount=amount,
            transaction_type='withdraw'
        )

        db.session.add(transaction)
        db.session.commit()

        flash('Withdrawal successful!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('withdraw.html')

# View User Transactions
@app.route('/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
    search_query = request.args.get('transaction_id', '')

    if search_query:
        # Search for a specific transaction by ID
        transaction = Transaction.query.filter(
            ((Transaction.sender_id == current_user.id) | (Transaction.receiver_id == current_user.id)) &
            (Transaction.transaction_id == search_query)
        ).first()

        if transaction:
            user_transactions = [transaction]
            flash(f'Transaction found: {search_query}', 'success')
        else:
            user_transactions = []
            flash(f'No transaction found with ID: {search_query}', 'warning')
    else:
        # Get all user transactions
        user_transactions = Transaction.query.filter(
            (Transaction.sender_id == current_user.id) |
            (Transaction.receiver_id == current_user.id)
        ).order_by(Transaction.timestamp.desc()).all()

    return render_template('transactions.html', transactions=user_transactions, search_query=search_query)

# Admin - View All Users
@app.route('/admin/users')
def all_users():
    if 'admin_id' not in session:
        flash('Please login as admin', 'danger')
        return redirect(url_for('admin_login'))

    users = User.query.all()
    return render_template('all_users.html', users=users)

# Admin - View All Transactions
@app.route('/admin/transactions', methods=['GET', 'POST'])
def all_transactions():
    if 'admin_id' not in session:
        flash('Please login as admin', 'danger')
        return redirect(url_for('admin_login'))

    search_query = request.args.get('transaction_id', '')

    if search_query:
        # Search for a specific transaction by ID
        transaction = Transaction.query.filter(Transaction.transaction_id == search_query).first()

        if transaction:
            transactions = [transaction]
            flash(f'Transaction found: {search_query}', 'success')
        else:
            transactions = []
            flash(f'No transaction found with ID: {search_query}', 'warning')
    else:
        # Get all transactions
        transactions = Transaction.query.order_by(Transaction.timestamp.desc()).all()

    return render_template('all_transactions.html', transactions=transactions, search_query=search_query)

# Admin - Delete User
@app.route('/admin/delete_user/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    if 'admin_id' not in session:
        flash('Please login as admin', 'danger')
        return redirect(url_for('admin_login'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.name} has been deleted', 'success')
        return redirect(url_for('all_users'))

    return render_template('delete_user.html', user=user)

# Admin - Manage Accounts
@app.route('/admin/accounts')
def manage_accounts():
    if 'admin_id' not in session:
        flash('Please login as admin', 'danger')
        return redirect(url_for('admin_login'))

    accounts = Account.query.all()
    return render_template('admin_manage_accounts.html', accounts=accounts)

# Admin - Edit Account
@app.route('/admin/edit_account/<int:account_id>', methods=['GET', 'POST'])
def edit_account(account_id):
    if 'admin_id' not in session:
        flash('Please login as admin', 'danger')
        return redirect(url_for('admin_login'))

    account = Account.query.get_or_404(account_id)

    if request.method == 'POST':
        # Update user information
        account.user.name = request.form.get('user_name')
        account.user.email = request.form.get('email')

        # Update account balance
        new_balance = float(request.form.get('balance'))
        account.balance = new_balance

        db.session.commit()
        flash(f'Account for {account.user.name} has been updated', 'success')
        return redirect(url_for('manage_accounts'))

    return render_template('edit_account.html', account=account)

# Admin - Delete Account
@app.route('/admin/delete_account/<int:account_id>', methods=['GET', 'POST'])
def delete_account(account_id):
    if 'admin_id' not in session:
        flash('Please login as admin', 'danger')
        return redirect(url_for('admin_login'))

    account = Account.query.get_or_404(account_id)

    if request.method == 'POST':
        user = account.user
        db.session.delete(account)
        db.session.delete(user)
        db.session.commit()
        flash(f'Account for {user.name} has been deleted', 'success')
        return redirect(url_for('manage_accounts'))

    return render_template('delete_account.html', account=account)

# Admin - View Deposit Requests
@app.route('/admin/deposit-requests')
def admin_deposit_requests():
    if 'admin_id' not in session:
        flash('Please login as admin', 'danger')
        return redirect(url_for('admin_login'))

    # Get all deposit requests, with pending ones first
    deposit_requests = DepositRequest.query.order_by(
        # Order by status (pending first) and then by date (newest first)
        DepositRequest.status.desc(),
        DepositRequest.created_at.desc()
    ).all()

    return render_template('admin_deposit_requests.html', deposit_requests=deposit_requests)

# Admin - Approve Deposit Request
@app.route('/admin/deposit-requests/<int:request_id>/approve')
def approve_deposit(request_id):
    if 'admin_id' not in session:
        flash('Please login as admin', 'danger')
        return redirect(url_for('admin_login'))

    deposit_request = DepositRequest.query.get_or_404(request_id)

    # Only allow approving pending requests
    if deposit_request.status != 'pending':
        flash('This request has already been processed', 'warning')
        return redirect(url_for('admin_deposit_requests'))

    # Get user's account
    account = Account.query.filter_by(user_id=deposit_request.user_id).first()

    # Update account balance
    account.balance += deposit_request.amount

    # Create transaction record
    transaction = Transaction(
        receiver_id=deposit_request.user_id,
        amount=deposit_request.amount,
        transaction_type='deposit'
    )

    # Update deposit request status
    deposit_request.status = 'approved'
    deposit_request.notes = 'Approved by admin'

    db.session.add(transaction)
    db.session.commit()

    flash(f'Deposit request of ${deposit_request.amount:.2f} for {deposit_request.user.name} has been approved', 'success')
    return redirect(url_for('admin_deposit_requests'))

# Admin - Reject Deposit Request
@app.route('/admin/deposit-requests/<int:request_id>/reject', methods=['POST'])
def reject_deposit(request_id):
    if 'admin_id' not in session:
        flash('Please login as admin', 'danger')
        return redirect(url_for('admin_login'))

    deposit_request = DepositRequest.query.get_or_404(request_id)

    # Only allow rejecting pending requests
    if deposit_request.status != 'pending':
        flash('This request has already been processed', 'warning')
        return redirect(url_for('admin_deposit_requests'))

    # Update deposit request status
    deposit_request.status = 'rejected'
    deposit_request.notes = request.form.get('notes') or 'Rejected by admin'

    db.session.commit()

    flash(f'Deposit request of ${deposit_request.amount:.2f} for {deposit_request.user.name} has been rejected', 'warning')
    return redirect(url_for('admin_deposit_requests'))

# Logout
@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('You have been logged out', 'info')

    if 'admin_id' in session:
        session.pop('admin_id', None)
        flash('Admin logged out', 'info')

    # Always redirect to the welcome page
    print("Redirecting to welcome page after logout")
    return redirect(url_for('index'))

# Default route for any undefined routes - redirect to welcome page
@app.route('/<path:undefined_route>')
def handle_undefined_route(undefined_route):
    print(f"Undefined route accessed: {undefined_route}, redirecting to welcome page")
    flash("Page not found. Redirected to welcome page.", "warning")
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Initialize database tables
    create_tables()

    print("\n\n===== FlaskBank Application Starting =====")
    print("Starting page: http://127.0.0.1:5000/ (Welcome Page)")
    print("All undefined routes will redirect to the welcome page")
    print("===========================================\n")

    app.run(debug=True)
