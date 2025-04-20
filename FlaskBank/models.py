from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin
import uuid

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with Account
    account = db.relationship('Account', backref='user', uselist=False, cascade='all, delete-orphan')

    # Relationships with Transaction
    sent_transactions = db.relationship('Transaction',
                                       foreign_keys='Transaction.sender_id',
                                       backref='sender',
                                       lazy='dynamic',
                                       cascade='all, delete-orphan')

    received_transactions = db.relationship('Transaction',
                                          foreign_keys='Transaction.receiver_id',
                                          backref='receiver',
                                          lazy='dynamic')

    def __init__(self, name, email, phone, password):
        self.name = name
        self.email = email
        self.phone = phone
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.name}>'


class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    balance = db.Column(db.Float, default=0.0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Account {self.id} - User {self.user_id}>'


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(36), unique=True, nullable=False, index=True)  # UUID for transaction ID
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'transfer', 'deposit', 'withdraw'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, sender_id=None, receiver_id=None, amount=0.0, transaction_type='transfer'):
        self.transaction_id = str(uuid.uuid4())  # Generate a unique transaction ID
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.amount = amount
        self.transaction_type = transaction_type

    def __repr__(self):
        return f'<Transaction {self.transaction_id} - {self.transaction_type}>'


class DepositRequest(db.Model):
    __tablename__ = 'deposit_requests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    notes = db.Column(db.String(200), nullable=True)  # For rejection reason or admin notes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with User
    user = db.relationship('User', backref=db.backref('deposit_requests', lazy='dynamic'))

    def __repr__(self):
        return f'<DepositRequest {self.id} - User {self.user_id} - ${self.amount} - {self.status}>'


class Admin(db.Model):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    verification_code = db.Column(db.String(5), nullable=True)  # 5-digit verification code

    def __init__(self, username, password, verification_code=None):
        self.username = username
        self.set_password(password)
        self.verification_code = verification_code

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Admin {self.username}>'
