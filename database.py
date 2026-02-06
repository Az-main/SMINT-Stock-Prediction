"""
Database module for SMINT Stock Prediction Application
Handles user authentication with SQLite and password hashing
"""

import sqlite3
import hashlib
from datetime import datetime

# Database file path
DATABASE_PATH = "smint.db"


def get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enables column access by name
    return conn


def init_database():
    """Initialize the database and create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Create default admin user if not exists
    if not user_exists("admin"):
        create_user("admin", "admin@smint.com", "password123")


def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(username, email, password):
    """
    Create a new user in the database.
    Returns: (success: bool, message: str)
    """
    # Check if username already exists
    if user_exists(username):
        return False, "Username already exists."
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Hash the password before storing
        password_hash = hash_password(password)
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
        ''', (username, email, password_hash, datetime.now()))
        
        conn.commit()
        conn.close()
        return True, f"Account created successfully for {username}!"
    
    except sqlite3.Error as e:
        return False, f"Database error: {str(e)}"


def verify_user(username, password):
    """
    Verify user credentials.
    Returns: (success: bool, message: str)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Hash the entered password to compare
        password_hash = hash_password(password)
        
        cursor.execute('''
            SELECT * FROM users 
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return True, f"Welcome back, {username}!"
        else:
            return False, "Incorrect username or password."
    
    except sqlite3.Error as e:
        return False, f"Database error: {str(e)}"


def user_exists(username):
    """Check if a username already exists in the database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM users WHERE username = ?', (username,))
        exists = cursor.fetchone() is not None
        
        conn.close()
        return exists
    
    except sqlite3.Error:
        return False


def get_user_info(username):
    """Get user information by username."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, created_at 
            FROM users WHERE username = ?
        ''', (username,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "created_at": user["created_at"]
            }
        return None
    
    except sqlite3.Error:
        return None


def get_all_users():
    """Get all users (admin function)."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, email, created_at FROM users')
        users = cursor.fetchall()
        
        conn.close()
        return [dict(user) for user in users]
    
    except sqlite3.Error:
        return []
