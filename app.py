from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from functools import wraps
import json
from decimal import Decimal, InvalidOperation

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # Change this in production

# Database configuration - UPDATE THESE WITH YOUR MYSQL SETTINGS
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Your MySQL username
    'password': '',  # Your MySQL password (empty for XAMPP default)
    'database': 'Librariya',
    'port': 3306, 
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'autocommit': True 
}

# File upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    """Create database connection with proper error handling"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
        else:
            print("Failed to connect to database")
            return None
    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected database connection error: {e}")
        return None

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Template filters
@app.template_filter('format_price')
def format_price(price):
    """Format price with currency symbol"""
    if price is None:
        return 'N/A'
    return f'৳{price:.2f}'

@app.context_processor
def inject_user():
    return {
        'is_logged_in': 'user_id' in session,
        'user_name': session.get('user_name', ''),
        'site_name': 'Librariya'
    }


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', site_name='Librariya'), 404

@app.route('/user')
@login_required
def user():
    """User profile page"""
    return render_template('user.html',
                           site_name='Librariya',
                           is_logged_in=True,
                           user_name=session.get('user_name', ''))

# Routes
@app.route('/')
def index():
    """Homepage"""
    connection = get_db_connection()
    if not connection:
        # Return basic template if DB connection fails
        return render_template('index.html', 
                             site_name='Librariya',
                             site_description='Your Digital Book Marketplace',
                             is_logged_in=False,
                             stats={'total_books': 0, 'total_users': 0, 'active_listings': 0, 'completed_orders': 0},
                             categories=[],
                             featured_books=[])
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get site stats
        cursor.execute("SELECT COUNT(*) as count FROM books WHERE is_active = 1")
        total_books = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_active = 1 AND user_type = 'customer'")
        total_users = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM book_listings WHERE status = 'active'")
        active_listings = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM orders WHERE order_status = 'delivered'")
        completed_orders = cursor.fetchone()['count']
        
        # Get categories
        cursor.execute("SELECT category_id as id, category_name as name FROM categories WHERE is_active = 1 ORDER BY category_name  LIMIT 8")
        categories = cursor.fetchall()
        
        # Get featured books (latest available books)
        cursor.execute("""
            SELECT b.book_id as id, b.title, b.cover_image as image,
                COALESCE(GROUP_CONCAT(DISTINCT CONCAT(a.first_name, ' ', a.last_name) SEPARATOR ', '), 'Unknown Author') as author,
                COALESCE(MIN(bl.sell_price), 0) as price
            FROM books b 
            LEFT JOIN book_authors ba ON b.book_id = ba.book_id
            LEFT JOIN authors a ON ba.author_id = a.author_id
            LEFT JOIN book_listings bl ON b.book_id = bl.book_id AND bl.status = 'active'
            WHERE b.is_active = 1 
            GROUP BY b.book_id
            ORDER BY b.created_at DESC 
            LIMIT 8
        """)
        featured_books = cursor.fetchall()
        
        stats = {
            'total_books': total_books,
            'total_users': total_users,
            'active_listings': active_listings,
            'completed_orders': completed_orders
        }
        
        return render_template('index.html', 
                             site_name='Librariya',
                             site_description='Your Digital Book Marketplace',
                             stats=stats, 
                             categories=categories,
                             featured_books=featured_books,
                             is_logged_in='user_id' in session,
                             user_name=session.get('user_name', ''))
    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return render_template('index.html', 
                             site_name='Librariya',
                             site_description='Your Digital Book Marketplace',
                             is_logged_in='user_id' in session,
                             stats={'total_books': 0, 'total_users': 0, 'active_listings': 0, 'completed_orders': 0},
                             categories=[],
                             featured_books=[])
    finally:
        if connection:
            connection.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')
        
        connection = get_db_connection()
        if not connection:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Database connection failed'})
            flash('Database connection failed', 'error')
            return render_template('login.html')
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT user_id as id, username, email, password_hash, user_type, first_name, last_name 
                FROM users 
                WHERE username = %s OR email = %s
            """, (username, username))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['user_type'] = user['user_type']
                session['user_name'] = f"{user['first_name']} {user['last_name']}"
                
                # Update last login
                cursor.execute("UPDATE users SET last_login = NOW() WHERE user_id = %s", (user['id'],))
                connection.commit()
                
                if request.is_json:
                    return jsonify({'success': True, 'message': 'Login successful'})
                flash('Login successful!', 'success')
                
                # Redirect based on user type
                if user['user_type'] == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('userdashboard'))
            else:
                if request.is_json:
                    return jsonify({'success': False, 'message': 'Invalid username or password'})
                flash('Invalid username or password', 'error')
        
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            if request.is_json:
                return jsonify({'success': False, 'message': 'Login failed'})
            flash('Login failed', 'error')
        finally:
            connection.close()
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        username = data.get('username')
        email = data.get('email')
        phone = data.get('phone', '')
        password = data.get('password')
        
        connection = get_db_connection()
        if not connection:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Database connection failed'})
            flash('Database connection failed', 'error')
            return render_template('register.html')
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Check if username or email already exists
            cursor.execute("SELECT user_id FROM users WHERE username = %s OR email = %s", (username, email))
            if cursor.fetchone():
                if request.is_json:
                    return jsonify({'success': False, 'message': 'Username or email already exists'})
                flash('Username or email already exists', 'error')
                return render_template('register.html')
            
            # Insert new user
            password_hash = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, first_name, last_name, phone, user_type, is_active, email_verified)
                VALUES (%s, %s, %s, %s, %s, %s, 'customer', TRUE, TRUE)
            """, (username, email, password_hash, first_name, last_name, phone))
            
            connection.commit()
            user_id = cursor.lastrowid
            
            # Create session
            session['user_id'] = user_id
            session['username'] = username
            session['user_type'] = 'customer'
            session['user_name'] = f"{first_name} {last_name}"
            
            if request.is_json:
                return jsonify({'success': True, 'message': 'Registration successful'})
            flash('Registration successful!', 'success')
            return redirect(url_for('userdashboard'))
        
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            connection.rollback()
            if request.is_json:
                return jsonify({'success': False, 'message': 'Registration failed'})
            flash('Registration failed', 'error')
        finally:
            connection.close()
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/books')
def book():
    """Browse books page (mapped to template book.html)"""
    connection = get_db_connection()
    if not connection:
        return render_template('book.html', site_name='Librariya', categories=[], books=[])
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get categories
        cursor.execute("SELECT category_id as id, category_name as name FROM categories WHERE is_active = 1 ORDER BY category_name")
        categories = cursor.fetchall()
        
        # Get search parameters
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        condition = request.args.get('condition', '')
        min_price = request.args.get('min_price', '')
        max_price = request.args.get('max_price', '')
        
        # Build query - FIXED VERSION
        query = """
        SELECT DISTINCT
            b.book_id as id, 
            b.title, 
            b.cover_image as image,
            b.created_at,
            COALESCE(GROUP_CONCAT(DISTINCT CONCAT(a.first_name, ' ', a.last_name) SEPARATOR ', '), 'Unknown Author') as author,
            COALESCE(c.category_name, 'Uncategorized') as category_name,
            COALESCE(MIN(bl.sell_price), 0) as price,
            COALESCE(bl.condition_type, 'good') as condition_type
        FROM books b 
        LEFT JOIN book_authors ba ON b.book_id = ba.book_id
        LEFT JOIN authors a ON ba.author_id = a.author_id
        LEFT JOIN book_categories bc ON b.book_id = bc.book_id
        LEFT JOIN categories c ON bc.category_id = c.category_id
        LEFT JOIN book_listings bl ON b.book_id = bl.book_id AND bl.status = 'active'
        WHERE b.is_active = 1
        """
        params = []
        
        if search:
            query += " AND (b.title LIKE %s OR CONCAT(a.first_name, ' ', a.last_name) LIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
        
        if category:
            query += " AND c.category_id = %s"
            params.append(category)
        
        if condition:
            query += " AND bl.condition_type = %s"
            params.append(condition)
        
        query += """ 
        GROUP BY 
            b.book_id, 
            b.title, 
            b.cover_image, 
            b.created_at,
            c.category_name, 
            bl.condition_type
        """
        
        if min_price or max_price:
            having_conditions = []
            if min_price:
                having_conditions.append("price >= %s")
                params.append(float(min_price))
            if max_price:
                having_conditions.append("price <= %s") 
                params.append(float(max_price))
            query += " HAVING " + " AND ".join(having_conditions)

        sort_param = request.args.get('sort', 'newest')
        if sort_param == 'price_low':
            query += " ORDER BY price ASC"
        elif sort_param == 'price_high':
            query += " ORDER BY price DESC"
        elif sort_param == 'title':
            query += " ORDER BY b.title ASC"
        else:  # newest
            query += " ORDER BY b.created_at DESC"

        cursor.execute(query, params)
        books = cursor.fetchall()
        
        return render_template('book.html', 
                             site_name='Librariya',
                             categories=categories,
                             books=books,
                             is_logged_in='user_id' in session,
                             user_name=session.get('user_name', ''))
    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return render_template('book.html', site_name='Librariya', categories=[], books=[], 
                             is_logged_in='user_id' in session, user_name=session.get('user_name', ''))
    finally:
        if connection:
            connection.close()
            
@app.route('/books/<int:book_id>')
def book_details(book_id):
    """Book details page with rental options - FIXED VERSION"""
    connection = get_db_connection()
    if not connection:
        return render_template('404.html', site_name='Librariya'), 404
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Fixed query - simpler GROUP BY
        cursor.execute("""
            SELECT DISTINCT b.book_id, b.title, b.isbn, b.description, b.cover_image, 
                   b.pages, b.publication_date, b.language, b.average_rating, 
                   b.total_reviews, b.created_at
            FROM books b 
            WHERE b.book_id = %s AND b.is_active = 1
        """, (book_id,))
        book = cursor.fetchone()
        
        if not book:
            return render_template('404.html', site_name='Librariya'), 404
        
        # Get authors separately to avoid GROUP BY issues
        cursor.execute("""
            SELECT GROUP_CONCAT(DISTINCT CONCAT(a.first_name, ' ', a.last_name) SEPARATOR ', ') as author
            FROM book_authors ba
            JOIN authors a ON ba.author_id = a.author_id
            WHERE ba.book_id = %s
        """, (book_id,))
        author_result = cursor.fetchone()
        book['author'] = author_result['author'] if author_result and author_result['author'] else 'Unknown Author'
        
        # Get categories separately
        cursor.execute("""
            SELECT GROUP_CONCAT(DISTINCT c.category_name SEPARATOR ', ') as category_name
            FROM book_categories bc
            JOIN categories c ON bc.category_id = c.category_id
            WHERE bc.book_id = %s
        """, (book_id,))
        category_result = cursor.fetchone()
        book['category_name'] = category_result['category_name'] if category_result and category_result['category_name'] else 'Uncategorized'
        
        # Get book listings
        cursor.execute("""
            SELECT bl.listing_id, bl.listing_type, bl.condition_type, 
                   bl.sell_price, bl.rent_price_per_month, bl.description as listing_description,
                   bl.location, bl.status,
                   u.username as seller_name, u.rating as seller_rating,
                   u.city as seller_city
            FROM book_listings bl
            JOIN users u ON bl.seller_id = u.user_id
            WHERE bl.book_id = %s AND bl.status = 'active'
            ORDER BY bl.sell_price ASC, bl.rent_price_per_month ASC
        """, (book_id,))
        listings = cursor.fetchall()
        
        # Separate buy and rent options
        buy_options = [l for l in listings if l['listing_type'] in ['sell', 'both'] and l['sell_price'] and l['sell_price'] > 0]
        rent_options = [l for l in listings if l['listing_type'] in ['rent', 'both'] and l['rent_price_per_month'] and l['rent_price_per_month'] > 0]
        
        # Get reviews
        cursor.execute("""
            SELECT r.review_id, r.rating, r.title as review_title, r.review_text, 
                   r.created_at, r.is_verified_purchase,
                   u.username as user_name
            FROM reviews r
            JOIN users u ON r.user_id = u.user_id
            WHERE r.book_id = %s AND r.is_approved = 1
            ORDER BY r.created_at DESC
            LIMIT 10
        """, (book_id,))
        reviews = cursor.fetchall()
        
        # Get related books - simplified query
        cursor.execute("""
            SELECT DISTINCT b2.book_id as id, b2.title, b2.cover_image as image
            FROM books b2
            WHERE b2.book_id != %s AND b2.is_active = 1
            ORDER BY RAND()
            LIMIT 4
        """, (book_id,))
        related_books = cursor.fetchall()
        
        # Get author and price for related books
        for related in related_books:
            cursor.execute("""
                SELECT GROUP_CONCAT(DISTINCT CONCAT(a.first_name, ' ', a.last_name) SEPARATOR ', ') as author
                FROM book_authors ba
                JOIN authors a ON ba.author_id = a.author_id
                WHERE ba.book_id = %s
            """, (related['id'],))
            author_result = cursor.fetchone()
            related['author'] = author_result['author'] if author_result and author_result['author'] else 'Unknown Author'
            
            cursor.execute("""
                SELECT MIN(sell_price) as price
                FROM book_listings
                WHERE book_id = %s AND status = 'active' AND sell_price > 0
            """, (related['id'],))
            price_result = cursor.fetchone()
            related['price'] = price_result['price'] if price_result else None
        
        return render_template('book_details.html', 
                             site_name='Librariya',
                             book=book,
                             buy_options=buy_options,
                             rent_options=rent_options,
                             reviews=reviews,
                             related_books=related_books,
                             is_logged_in='user_id' in session,
                             user_name=session.get('user_name', ''))
    
    except mysql.connector.Error as e:
        print(f"Database error in book_details: {e}")
        return render_template('404.html', site_name='Librariya'), 404
    finally:
        if connection:
            connection.close()


# Additional helper function for better error handling
def get_book_basic_info(book_id):
    """Get basic book information as fallback"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT b.*, 
                   COALESCE(GROUP_CONCAT(DISTINCT CONCAT(a.first_name, ' ', a.last_name) SEPARATOR ', '), 'Unknown Author') as author
            FROM books b 
            LEFT JOIN book_authors ba ON b.book_id = ba.book_id
            LEFT JOIN authors a ON ba.author_id = a.author_id
            WHERE b.book_id = %s AND b.is_active = 1
            GROUP BY b.book_id
        """, (book_id,))
        return cursor.fetchone()
    except mysql.connector.Error as e:
        print(f"Error getting basic book info: {e}")
        return None
    finally:
        if connection:
            connection.close()



@app.route('/add_books', methods=['GET', 'POST'])
@login_required
def add_books():
    """Add new book listing (uses add_books.html template)"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection failed', 'error')
        return redirect(url_for('userdashboard'))
    
    if request.method == 'POST':
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get form data
            title = request.form.get('title')
            author = request.form.get('author')
            isbn = request.form.get('isbn', '')
            description = request.form.get('description', '')
            category_id = request.form.get('category_id')
            condition_type = request.form.get('condition_type')
            price = request.form.get('price')
            rent_price = request.form.get('rent_price')
            location = request.form.get('location', '')
            
            # Handle author
            author_parts = author.split(' ', 1) if author else ['Unknown', '']
            first_name = author_parts[0]
            last_name = author_parts[1] if len(author_parts) > 1 else ''
            
            # Insert or get author
            cursor.execute("SELECT author_id FROM authors WHERE LOWER(first_name) = LOWER(%s) AND LOWER(last_name) = LOWER(%s)", 
                          (first_name, last_name))
            author_row = cursor.fetchone()
            
            if author_row:
                author_id = author_row['author_id']
            else:
                cursor.execute("INSERT INTO authors (first_name, last_name) VALUES (%s, %s)", 
                              (first_name, last_name))
                author_id = cursor.lastrowid
            
            # Insert book
            cursor.execute("""
                INSERT INTO books (title, isbn, description, is_active)
                VALUES (%s, %s, %s, 1)
            """, (title, isbn, description))
            book_id = cursor.lastrowid
            
            # Link book and author
            cursor.execute("INSERT INTO book_authors (book_id, author_id) VALUES (%s, %s)", 
                          (book_id, author_id))
            
            # Link book and category
            if category_id:
                cursor.execute("INSERT INTO book_categories (book_id, category_id) VALUES (%s, %s)", 
                              (book_id, category_id))
            
            # Determine listing type
            listing_type = 'sell'
            if price and rent_price:
                listing_type = 'both'
            elif rent_price and not price:
                listing_type = 'rent'
            
            # Insert listing
            cursor.execute("""
                INSERT INTO book_listings (book_id, seller_id, listing_type, condition_type, 
                                         sell_price, rent_price_per_month, description, location, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'active')
            """, (book_id, session['user_id'], listing_type, condition_type, 
                  price if price else None, rent_price if rent_price else None, 
                  description, location))
            
            connection.commit()
            flash('Book added successfully!', 'success')
            return redirect(url_for('book_details', book_id=book_id))
            
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            connection.rollback()
            flash('Error adding book. Please try again.', 'error')
        finally:
            connection.close()
    
    # GET request - show form
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT category_id as id, category_name as name FROM categories WHERE is_active = 1 ORDER BY category_name")
        categories = cursor.fetchall()
        
        return render_template('add_books.html', 
                             site_name='Librariya',
                             site_description='Your Digital Book Marketplace',
                             categories=categories,
                             is_logged_in='user_id' in session,
                             user_name=session.get('user_name', ''))
    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return redirect(url_for('userdashboard'))
    finally:
        if connection:
            connection.close()



@app.route('/admin/manage_books')
@admin_required
def admin_manage_books():
    """Admin - View and manage all books"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection failed', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT b.book_id, b.title, b.isbn, b.is_active, b.created_at,
                   GROUP_CONCAT(DISTINCT CONCAT(a.first_name, ' ', a.last_name) SEPARATOR ', ') as authors,
                   COUNT(DISTINCT bl.listing_id) as listing_count
            FROM books b
            LEFT JOIN book_authors ba ON b.book_id = ba.book_id
            LEFT JOIN authors a ON ba.author_id = a.author_id
            LEFT JOIN book_listings bl ON b.book_id = bl.book_id
            GROUP BY b.book_id
            ORDER BY b.created_at DESC
        """)
        books = cursor.fetchall()
        
        return render_template('admin_simple.html',
                             page='books', items=books, title='Books Management',
                             site_name='Librariya', is_logged_in=True,
                             user_name=session.get('user_name', ''))
    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        flash('Error loading books', 'error')
        return redirect(url_for('admin_dashboard'))
    finally:
        if connection:
            connection.close()

@app.route('/admin/manage_users')
@admin_required
def admin_manage_users():
    """Admin - View and manage all users"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection failed', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT user_id, username, email, first_name, last_name, 
                   user_type, is_active, created_at, last_login
            FROM users
            WHERE user_type != 'admin'
            ORDER BY created_at DESC
        """)
        users = cursor.fetchall()
        
        return render_template('admin_simple.html',
                             page='users', items=users, title='Users Management',
                             site_name='Librariya', is_logged_in=True,
                             user_name=session.get('user_name', ''))
    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        flash('Error loading users', 'error')
        return redirect(url_for('admin_dashboard'))
    finally:
        if connection:
            connection.close()

@app.route('/admin/manage_orders')
@admin_required
def admin_manage_orders():
    """Admin - View and manage all orders"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection failed', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT o.order_id, o.total_amount, o.order_status, o.payment_status,
                   o.created_at, u.username as buyer_name,
                   COUNT(oi.order_item_id) as item_count
            FROM orders o
            JOIN users u ON o.buyer_id = u.user_id
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY o.order_id
            ORDER BY o.created_at DESC
        """)
        orders = cursor.fetchall()
        
        return render_template('admin_simple.html',
                             page='orders', items=orders, title='Orders Management',
                             site_name='Librariya', is_logged_in=True,
                             user_name=session.get('user_name', ''))
    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        flash('Error loading orders', 'error')
        return redirect(url_for('admin_dashboard'))
    finally:
        if connection:
            connection.close()

@app.route('/admin/manage_donations')
@admin_required
def admin_manage_donations():
    """Admin - View and manage donations"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection failed', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        cursor = connection.cursor(dictionary=True)
        
       
        try:
            cursor.execute("""
                SELECT d.donation_id, d.status, d.created_at, d.quantity,
                       b.title as book_title, u.username as donor_name
                FROM donations d
                JOIN books b ON d.book_id = b.book_id
                JOIN users u ON d.donor_id = u.user_id
                ORDER BY d.created_at DESC
            """)
        except:
            cursor.execute("""
                SELECT bd.donation_id, bd.status, bd.created_at, bd.quantity,
                       b.title as book_title, u.username as donor_name
                FROM book_donations bd
                JOIN books b ON bd.book_id = b.book_id
                JOIN users u ON bd.donor_id = u.user_id
                ORDER BY bd.created_at DESC
            """)
        
        donations = cursor.fetchall()
        
        return render_template('admin_simple.html',
                             page='donations', items=donations, title='Donations Management',
                             site_name='Librariya', is_logged_in=True,
                             user_name=session.get('user_name', ''))
    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        flash('Error loading donations', 'error')
        return redirect(url_for('admin_dashboard'))
    finally:
        if connection:
            connection.close()

@app.route('/admin/manage_stationery')
@admin_required
def admin_manage_stationery():
    """Admin - View and manage stationery"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection failed', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT s.item_id, s.item_name, s.price, s.stock_quantity, 
                   s.is_active, sc.category_name
            FROM stationery_items s
            LEFT JOIN stationery_categories sc ON s.category_id = sc.category_id
            ORDER BY s.created_at DESC
        """)
        stationery = cursor.fetchall()
        
        
        cursor.execute("SELECT * FROM stationery_categories WHERE is_active = 1")
        categories = cursor.fetchall()
        
        return render_template('admin_simple.html',
                             page='stationery', items=stationery, categories=categories,
                             title='Stationery Management',
                             site_name='Librariya', is_logged_in=True,
                             user_name=session.get('user_name', ''))
    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        flash('Error loading stationery', 'error')
        return redirect(url_for('admin_dashboard'))
    finally:
        if connection:
            connection.close()

# admin

@app.route('/admin/action', methods=['POST'])
@admin_required
def admin_action():
    """Handle all admin actions"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    
    try:
        cursor = connection.cursor()
        data = request.get_json()
        action = data.get('action')
        item_type = data.get('type')
        item_id = data.get('id')
        
        success = False
        message = ''
        
        # Book 
        if item_type == 'book': 
            if action == 'delete':
                cursor.execute("UPDATE books SET is_active = 0 WHERE book_id = %s", (item_id,))
                cursor.execute("UPDATE book_listings SET status = 'inactive' WHERE book_id = %s", (item_id,))
                success = True 
                message = 'Book deleted successfully'
            elif action == 'toggle':
                cursor.execute("UPDATE books SET is_active = NOT is_active WHERE book_id = %s", (item_id,))
                success = True
                message = 'Book status updated'
        
        # User
        elif item_type == 'user':
            if action == 'delete':
                cursor.execute("UPDATE users SET is_active = 0, email = CONCAT('deleted_', user_id, '@deleted.com') WHERE user_id = %s AND user_type != 'admin'", (item_id,))
                success = True
                message = 'User deleted successfully'
            elif action == 'toggle':
                cursor.execute("UPDATE users SET is_active = NOT is_active WHERE user_id = %s AND user_type != 'admin'", (item_id,))
                success = True
                message = 'User status updated'
        
        # Order
        elif item_type == 'order':
            if action == 'cancel':
                cursor.execute("UPDATE orders SET order_status = 'cancelled' WHERE order_id = %s", (item_id,))
                success = True
                message = 'Order cancelled successfully'
            elif action == 'update_status':
                status = data.get('status', 'confirmed')
                cursor.execute("UPDATE orders SET order_status = %s WHERE order_id = %s", (status, item_id))
                success = True
                message = 'Order status updated'
        
        # Donation
        elif item_type == 'donation':
            if action == 'approve':
                try:
                    cursor.execute("UPDATE donations SET status = 'approved' WHERE donation_id = %s", (item_id,))
                except:
                    cursor.execute("UPDATE book_donations SET status = 'approved' WHERE donation_id = %s", (item_id,))
                success = True
                message = 'Donation approved'
            elif action == 'reject':
                try:
                    cursor.execute("UPDATE donations SET status = 'rejected' WHERE donation_id = %s", (item_id,))
                except:
                    cursor.execute("UPDATE book_donations SET status = 'rejected' WHERE donation_id = %s", (item_id,))
                success = True
                message = 'Donation rejected'
        
        # Stationery 
        elif item_type == 'stationery':
            if action == 'delete':
                cursor.execute("UPDATE stationery_items SET is_active = 0 WHERE item_id = %s", (item_id,))
                success = True
                message = 'Item deleted successfully'
            elif action == 'toggle':
                cursor.execute("UPDATE stationery_items SET is_active = NOT is_active WHERE item_id = %s", (item_id,))
                success = True
                message = 'Item status updated'
            elif action == 'add':
                name = data.get('name')
                category_id = data.get('category_id')
                price = data.get('price')
                stock = data.get('stock')
                cursor.execute("""
                    INSERT INTO stationery_items (item_name, category_id, price, stock_quantity, is_active)
                    VALUES (%s, %s, %s, %s, 1)
                """, (name, category_id, price, stock))
                success = True
                message = 'Item added successfully'
        
        if success:
            connection.commit()
        
        return jsonify({'success': success, 'message': message})
    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        if connection:
            connection.rollback()
        return jsonify({'success': False, 'message': 'Database error occurred'})
    finally:
        if connection:
            connection.close()

@app.route('/cancel_order', methods=['POST'])
@login_required
def cancel_order():
    """Cancel an order"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    
    try:
        cursor = connection.cursor()
        data = request.get_json()
        order_id = data.get('order_id')
        
        # if order belongs to user and can be cancelled 
        cursor.execute("""
            SELECT order_status FROM orders 
            WHERE order_id = %s AND buyer_id = %s
        """, (order_id, session['user_id']))
        
        order = cursor.fetchone()
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'})
        
        if order[0] not in ['pending', 'confirmed']:
            return jsonify({'success': False, 'message': 'Order cannot be cancelled'})
        
        # Update order
        cursor.execute("""
            UPDATE orders SET order_status = 'cancelled' 
            WHERE order_id = %s AND buyer_id = %s
        """, (order_id, session['user_id']))
        
        connection.commit()
        return jsonify({'success': True, 'message': 'Order cancelled successfully'})
    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        connection.rollback()
        return jsonify({'success': False, 'message': 'Failed to cancel order'})
    finally:
        if connection:
            connection.close()

@app.route('/donate_books', methods=['GET', 'POST'])
@login_required
def donate_books():
    """Book donation page"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection failed', 'error')
        return redirect(url_for('index'))

    try:
        if request.method == 'POST':
            cursor = connection.cursor(dictionary=True)

            # Get form data safely
            title = request.form.get('title')
            author = request.form.get('author')
            isbn = request.form.get('isbn', '')
            description = request.form.get('description', '')
            category_id = request.form.get('category_id')
            condition_type = request.form.get('condition_type')
            quantity = int(request.form.get('quantity', 1))
            recipient_type = request.form.get('recipient_type', 'library')
            recipient_organization = request.form.get('recipient_organization', '')
            special_notes = request.form.get('special_notes', '')

            # Handle author
            author_parts = author.split(' ', 1) if author else ['Unknown', '']
            first_name = author_parts[0]
            last_name = author_parts[1] if len(author_parts) > 1 else ''

            cursor.execute("SELECT author_id FROM authors WHERE first_name=%s AND last_name=%s",
                           (first_name, last_name))
            author_row = cursor.fetchone()

            if author_row:
                author_id = author_row['author_id']
            else:
                cursor.execute("INSERT INTO authors (first_name, last_name) VALUES (%s, %s)",
                               (first_name, last_name))
                author_id = cursor.lastrowid

            # Insert or fetch book
            cursor.execute("SELECT book_id FROM books WHERE title=%s AND isbn=%s", (title, isbn))
            book_row = cursor.fetchone()

            if book_row:
                book_id = book_row['book_id']
            else:
                cursor.execute("""
                    INSERT INTO books (title, isbn, description, is_active)
                    VALUES (%s, %s, %s, 1)
                """, (title, isbn, description))
                book_id = cursor.lastrowid

                cursor.execute("INSERT INTO book_authors (book_id, author_id) VALUES (%s, %s)",
                               (book_id, author_id))

            # Always ensure category mapping
            if category_id:
                cursor.execute("SELECT 1 FROM book_categories WHERE book_id=%s AND category_id=%s",
                               (book_id, category_id))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO book_categories (book_id, category_id) VALUES (%s, %s)",
                                   (book_id, category_id))

            # Insert donation record - check if table exists and use correct name
            try:
                cursor.execute("""
                    INSERT INTO donations (donor_id, book_id, quantity, condition_type, donation_type,
                                         recipient_organization, pickup_required, pickup_address, status)
                    VALUES (%s, %s, %s, %s, %s, %s, TRUE, %s, 'pending')
                """, (session['user_id'], book_id, quantity, condition_type, recipient_type,
                      recipient_organization, request.form.get('pickup_address', '')))
            except mysql.connector.Error:
                # Fallback to book_donations table if donations doesn't exist
                cursor.execute("""
                    INSERT INTO book_donations (book_id, donor_id, recipient_type, condition_type,
                                               quantity, special_notes, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, 'pending', NOW())
                """, (book_id, session['user_id'], recipient_type, condition_type, quantity, special_notes))

            connection.commit()
            flash('Thank you for your generous donation! We will process it shortly.', 'success')
            return redirect(url_for('userdashboard'))

        # GET request
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT category_id as id, category_name as name FROM categories WHERE is_active=1 ORDER BY category_name")
        categories = cursor.fetchall()

        return render_template('donate_books.html',
                               site_name='Librariya',
                               categories=categories,
                               is_logged_in='user_id' in session,
                               user_name=session.get('user_name', ''))

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        connection.rollback()
        flash('Error processing donation. Please try again.', 'error')
        return redirect(url_for('donate_books'))
    finally:
        connection.close()
@app.route('/add_to_cart_ajax', methods=['POST'])
@login_required
def add_to_cart_ajax():
    """Add item to cart via AJAX"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    
    try:
        cursor = connection.cursor(dictionary=True)
        data = request.get_json()
        
        listing_id = data.get('listing_id')
        stationery_item_id = data.get('stationery_item_id')
        quantity = int(data.get('quantity', 1))
        rental_duration = data.get('rental_duration')
        
        # Validate input
        if not listing_id and not stationery_item_id:
            return jsonify({'success': False, 'message': 'No item specified'})
        
        if quantity < 1:
            quantity = 1
        
        # Check if item exists and is available
        if listing_id:
            cursor.execute("""
                SELECT bl.*, b.title 
                FROM book_listings bl 
                JOIN books b ON bl.book_id = b.book_id 
                WHERE bl.listing_id = %s AND bl.status = 'active'
            """, (listing_id,))
            listing = cursor.fetchone()
            
            if not listing:
                return jsonify({'success': False, 'message': 'Book listing not found or unavailable'})
            
            item_name = listing['title']
            
        elif stationery_item_id:
            cursor.execute("""
                SELECT * FROM stationery_items 
                WHERE item_id = %s AND is_active = 1
            """, (stationery_item_id,))
            stationery = cursor.fetchone()
            
            if not stationery:
                return jsonify({'success': False, 'message': 'Stationery item not found or unavailable'})
            
            if stationery['stock_quantity'] < quantity:
                return jsonify({'success': False, 'message': f'Only {stationery["stock_quantity"]} items in stock'})
            
            item_name = stationery['item_name']
        
        # Check if item already in cart
        cursor.execute("""
            SELECT cart_id, quantity FROM cart_items 
            WHERE user_id = %s AND 
                  (listing_id = %s OR stationery_item_id = %s) AND
                  COALESCE(rental_duration, 0) = COALESCE(%s, 0)
        """, (session['user_id'], listing_id, stationery_item_id, rental_duration))
        
        existing_item = cursor.fetchone()
        
        if existing_item:
            # Update quantity
            new_quantity = existing_item['quantity'] + quantity
            cursor.execute("""
                UPDATE cart_items 
                SET quantity = %s, added_at = CURRENT_TIMESTAMP
                WHERE cart_id = %s
            """, (new_quantity, existing_item['cart_id']))
            message = f'Updated {item_name} quantity to {new_quantity}'
        else:
            # Insert new item
            cursor.execute("""
                INSERT INTO cart_items (user_id, listing_id, stationery_item_id, quantity, rental_duration, added_at)
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (session['user_id'], listing_id, stationery_item_id, quantity, rental_duration))
            message = f'{item_name} added to cart'
        
        connection.commit()
        
        # Get updated cart count
        cursor.execute("SELECT COALESCE(SUM(quantity), 0) as count FROM cart_items WHERE user_id = %s", (session['user_id'],))
        cart_count = cursor.fetchone()['count']
        
        return jsonify({
            'success': True, 
            'message': message,
            'cart_count': cart_count
        })
    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        if connection:
            connection.rollback()
        return jsonify({'success': False, 'message': 'Database error occurred'})
    except Exception as e:
        print(f"Error: {e}")
        if connection:
            connection.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'})
    finally:
        if connection:
            connection.close()
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout process - FIXED DECIMAL VERSION"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection failed', 'error')
        return redirect(url_for('cart'))
    
    if request.method == 'POST':
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get cart items with validation
            cursor.execute("""
                SELECT ci.*, 
                       bl.sell_price, bl.rent_price_per_month, bl.status as listing_status,
                       si.price as stationery_price, si.stock_quantity,
                       b.title as book_title,
                       si.item_name as stationery_name
                FROM cart_items ci
                LEFT JOIN book_listings bl ON ci.listing_id = bl.listing_id
                LEFT JOIN books b ON bl.book_id = b.book_id
                LEFT JOIN stationery_items si ON ci.stationery_item_id = si.item_id
                WHERE ci.user_id = %s
            """, (session['user_id'],))
            
            cart_items = cursor.fetchall()
            if not cart_items:
                flash('Your cart is empty', 'error')
                return redirect(url_for('cart'))
            
            # Validate cart items availability
            for item in cart_items:
                if item['listing_id'] and item['listing_status'] != 'active':
                    flash(f'Book "{item["book_title"]}" is no longer available', 'error')
                    return redirect(url_for('cart'))
                
                if item['stationery_item_id'] and (not item['stock_quantity'] or item['stock_quantity'] < item['quantity']):
                    flash(f'Insufficient stock for "{item["stationery_name"]}"', 'error')
                    return redirect(url_for('cart'))
            
            # Calculate total amount - FIXED VERSION
            total_amount = Decimal('0')
            for item in cart_items:
                try:
                    quantity = Decimal(str(item['quantity'] or 1))
                    
                    if item['listing_id']:
                        if item['rental_duration'] and item['rental_duration'] > 0:
                            monthly_rate = Decimal(str(item['rent_price_per_month'] or 0))
                            duration_days = Decimal(str(item['rental_duration']))
                            duration_months = duration_days / Decimal('30')
                            item_total = monthly_rate * duration_months * quantity
                        else:
                            sell_price = Decimal(str(item['sell_price'] or 0))
                            item_total = sell_price * quantity
                    elif item['stationery_item_id']:
                        stationery_price = Decimal(str(item['stationery_price'] or 0))
                        item_total = stationery_price * quantity
                    else:
                        item_total = Decimal('0')
                    
                    total_amount += item_total
                except (ValueError, InvalidOperation, TypeError) as e:
                    print(f"Error calculating item total: {e}")
                    continue  # Skip items with invalid prices
            
            # Get form data with validation
            full_name = request.form.get('full_name', '').strip()
            phone = request.form.get('phone', '').strip()
            shipping_address = request.form.get('shipping_address', '').strip()
            city = request.form.get('city', '').strip()
            postal_code = request.form.get('postal_code', '').strip()
            payment_method = request.form.get('payment_method', 'cash_on_delivery')
            order_notes = request.form.get('order_notes', '').strip()
            
            # Validate required fields
            if not all([full_name, phone, shipping_address, city]):
                flash('Please fill in all required fields', 'error')
                return render_template('checkout.html',
                                     site_name='Librariya',
                                     cart_items=cart_items,
                                     total=total_amount,
                                     is_logged_in=True,
                                     user_name=session.get('user_name', ''))
            
            # Format complete shipping address
            complete_address = f"{shipping_address}, {city}"
            if postal_code:
                complete_address += f", {postal_code}"
            
            # Determine order type
            has_rentals = any(item['rental_duration'] and item['rental_duration'] > 0 for item in cart_items)
            has_purchases = any(not item['rental_duration'] or item['rental_duration'] == 0 for item in cart_items)
            
            if has_rentals and has_purchases:
                order_type = 'mixed'
            elif has_rentals:
                order_type = 'rental'
            else:
                order_type = 'purchase'
            
            # Create order
            cursor.execute("""
                INSERT INTO orders (buyer_id, order_type, total_amount, shipping_address, 
                                  payment_method, payment_status, order_status)
                VALUES (%s, %s, %s, %s, %s, 'pending', 'pending')
            """, (session['user_id'], order_type, total_amount, complete_address, payment_method))
            
            order_id = cursor.lastrowid
            
            # Create order items - FIXED VERSION
            for item in cart_items:
                try:
                    quantity = int(item['quantity'] or 1)
                    
                    if item['listing_id']:
                        if item['rental_duration'] and item['rental_duration'] > 0:
                            # Rental item
                            monthly_rate = Decimal(str(item['rent_price_per_month'] or 0))
                            duration_days = Decimal(str(item['rental_duration']))
                            duration_months = duration_days / Decimal('30')
                            unit_price = monthly_rate * duration_months
                            total_price = unit_price * Decimal(str(quantity))
                            
                            rental_start = datetime.now().date()
                            rental_end = rental_start + timedelta(days=int(item['rental_duration']))
                            
                            cursor.execute("""
                                INSERT INTO order_items (order_id, listing_id, quantity, unit_price, 
                                                        total_price, rental_start_date, rental_end_date, rental_duration)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """, (order_id, item['listing_id'], quantity, unit_price,
                                  total_price, rental_start, rental_end, item['rental_duration']))
                        else:
                            # Purchase item
                            unit_price = Decimal(str(item['sell_price'] or 0))
                            total_price = unit_price * Decimal(str(quantity))
                            
                            cursor.execute("""
                                INSERT INTO order_items (order_id, listing_id, quantity, unit_price, total_price)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (order_id, item['listing_id'], quantity, unit_price, total_price))
                    
                    elif item['stationery_item_id']:
                        unit_price = Decimal(str(item['stationery_price'] or 0))
                        total_price = unit_price * Decimal(str(quantity))
                        
                        cursor.execute("""
                            INSERT INTO order_items (order_id, stationery_item_id, quantity, unit_price, total_price)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (order_id, item['stationery_item_id'], quantity, unit_price, total_price))
                        
                        # Update stationery stock
                        cursor.execute("""
                            UPDATE stationery_items 
                            SET stock_quantity = stock_quantity - %s 
                            WHERE item_id = %s
                        """, (quantity, item['stationery_item_id']))
                
                except (ValueError, TypeError, InvalidOperation) as e:
                    print(f"Error processing order item: {e}")
                    continue
            
            # Clear cart
            cursor.execute("DELETE FROM cart_items WHERE user_id = %s", (session['user_id'],))
            
            connection.commit()
            flash('Order placed successfully!', 'success')
            return redirect(url_for('order_details', order_id=order_id))
        
        except mysql.connector.Error as e:
            print(f"Database error in checkout: {e}")
            if connection:
                connection.rollback()
            flash('Error processing order. Please try again.', 'error')
            return redirect(url_for('cart'))
        except Exception as e:
            print(f"Unexpected error in checkout: {e}")
            if connection:
                connection.rollback()
            flash('An unexpected error occurred. Please try again.', 'error')
            return redirect(url_for('cart'))
        finally:
            if connection:
                connection.close()
    
    # GET request - show checkout form - FIXED VERSION
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get cart items for display
        cursor.execute("""
            SELECT ci.*, 
                   b.title as book_title, b.cover_image,
                   bl.sell_price, bl.rent_price_per_month, bl.condition_type,
                   si.item_name as stationery_name, si.price as stationery_price, si.image_url as stationery_image
            FROM cart_items ci
            LEFT JOIN book_listings bl ON ci.listing_id = bl.listing_id
            LEFT JOIN books b ON bl.book_id = b.book_id
            LEFT JOIN stationery_items si ON ci.stationery_item_id = si.item_id
            WHERE ci.user_id = %s
        """, (session['user_id'],))
        
        cart_items = cursor.fetchall()
        
        if not cart_items:
            flash('Your cart is empty', 'info')
            return redirect(url_for('cart'))
        
        # Calculate total - FIXED VERSION
        total = Decimal('0')
        for item in cart_items:
            try:
                quantity = Decimal(str(item['quantity'] or 1))
                
                if item['listing_id']:
                    if item['rental_duration'] and item['rental_duration'] > 0:
                        monthly_rate = Decimal(str(item['rent_price_per_month'] or 0))
                        duration_days = Decimal(str(item['rental_duration']))
                        duration_months = duration_days / Decimal('30')
                        item_total = monthly_rate * duration_months * quantity
                    else:
                        sell_price = Decimal(str(item['sell_price'] or 0))
                        item_total = sell_price * quantity
                elif item['stationery_item_id']:
                    stationery_price = Decimal(str(item['stationery_price'] or 0))
                    item_total = stationery_price * quantity
                else:
                    item_total = Decimal('0')
                
                total += item_total
            except (ValueError, TypeError, InvalidOperation) as e:
                print(f"Error calculating total for item: {e}")
                continue
        
        return render_template('checkout.html',
                             site_name='Librariya',
                             cart_items=cart_items,
                             total=total,
                             is_logged_in=True,
                             user_name=session.get('user_name', ''))
    
    except mysql.connector.Error as e:
        print(f"Database error loading checkout: {e}")
        flash('Error loading checkout page', 'error')
        return redirect(url_for('cart'))
    finally:
        if connection:
            connection.close()

def setup_admin():
    """Create or update admin user with fixed password"""
    try:
        # Generate password hash for 'admin123'
        password_hash = generate_password_hash('admin123')
        
        # Connect to database
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Insert or update admin user
        query = """
        INSERT INTO users (
            username, email, password_hash, first_name, last_name, 
            user_type, is_active, email_verified
        ) VALUES (
            'admin', 'admin@librariya.com', %s, 'System', 'Administrator',
            'admin', TRUE, TRUE
        ) ON DUPLICATE KEY UPDATE 
            password_hash = VALUES(password_hash),
            is_active = TRUE,
            email_verified = TRUE
        """
        
        cursor.execute(query, (password_hash,))
        connection.commit()
        
        print("✅ Admin user created/updated successfully!")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Email: admin@librariya.com")
        
    except mysql.connector.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    setup_admin()

@app.route('/orders/<int:order_id>')
@login_required
def order_details(order_id):
    """Order details page"""
    connection = get_db_connection()
    if not connection:
        return render_template('404.html', site_name='Librariya'), 404
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get order details
        cursor.execute("""
            SELECT * FROM orders 
            WHERE order_id = %s AND buyer_id = %s
        """, (order_id, session['user_id']))
        
        order = cursor.fetchone()
        if not order:
            return render_template('404.html', site_name='Librariya'), 404
        
        # Get order items
        cursor.execute("""
            SELECT oi.*, 
                   b.title as book_title, b.cover_image,
                   si.item_name as stationery_name,
                   u.username as seller_name
            FROM order_items oi
            LEFT JOIN book_listings bl ON oi.listing_id = bl.listing_id
            LEFT JOIN books b ON bl.book_id = b.book_id
            LEFT JOIN users u ON bl.seller_id = u.user_id
            LEFT JOIN stationery_items si ON oi.stationery_item_id = si.item_id
            WHERE oi.order_id = %s
        """, (order_id,))
        
        order_items = cursor.fetchall()
        
        return render_template('order_details.html',
                             site_name='Librariya',
                             order=order,
                             order_items=order_items,
                             is_logged_in=True,
                             user_name=session.get('user_name', ''))
    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return render_template('404.html', site_name='Librariya'), 404
    finally:
        if connection:
            connection.close()

@app.route('/rentals')
@login_required
def rentals():
    """User's rental items page"""
    connection = get_db_connection()
    if not connection:
        return render_template('rentals.html', site_name='Librariya', rentals=[])
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT oi.*, o.order_status, o.created_at as order_date,
                   b.title as book_title, b.cover_image,
                   u.username as seller_name,
                   DATEDIFF(oi.rental_end_date, CURDATE()) as days_remaining
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            LEFT JOIN book_listings bl ON oi.listing_id = bl.listing_id
            LEFT JOIN books b ON bl.book_id = b.book_id
            LEFT JOIN users u ON bl.seller_id = u.user_id
            WHERE o.buyer_id = %s AND oi.rental_duration IS NOT NULL
            ORDER BY oi.rental_end_date ASC
        """, (session['user_id'],))
        
        rentals = cursor.fetchall()
        
        return render_template('rentals.html',
                             site_name='Librariya',
                             rentals=rentals,
                             is_logged_in=True,
                             user_name=session.get('user_name', ''))
    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return render_template('rentals.html', site_name='Librariya', rentals=[])
    finally:
        if connection:
            connection.close()

@app.route('/privacy')
def privacy():
    return render_template('privacy.html', site_name='Librariya', is_logged_in='user_id' in session)

@app.route('/terms')
def terms():
    return render_template('terms.html', site_name='Librariya', is_logged_in='user_id' in session)

@app.route('/contact')
def contact():
    return render_template('contact.html', site_name='Librariya', is_logged_in='user_id' in session)

@app.route('/dashboard')
@login_required
def dashboard():
    """Dynamic dashboard redirect based on user type"""
    if session.get('user_type') == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('userdashboard'))
    

@app.route('/userdashboard')
@login_required
def userdashboard():
    """User dashboard – renders userdashboard.html"""
    connection = get_db_connection()
    if not connection:
        return render_template('userdashboard.html', 
                             site_name='Librariya',
                             my_listings=[], my_orders=[], 
                             stats={'wallet_balance': 0, 'total_listings': 0, 'total_orders': 0, 'avg_rating': 0},
                             is_logged_in='user_id' in session,
                             user_name=session.get('user_name', ''))
    
    try:
        cursor = connection.cursor(dictionary=True)
        user_id = session['user_id']
        
        #user's listings
        cursor.execute("""
            SELECT bl.listing_id, bl.sell_price, bl.status, b.title
            FROM book_listings bl
            JOIN books b ON bl.book_id = b.book_id
            WHERE bl.seller_id = %s
            ORDER BY bl.created_at DESC
        """, (user_id,))
        my_listings = cursor.fetchall()
        
        # user's orders  
        cursor.execute("""
            SELECT o.order_id, o.total_amount, o.order_status, o.created_at,
                   COUNT(oi.order_item_id) as item_count
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.buyer_id = %s
            GROUP BY o.order_id
            ORDER BY o.created_at DESC
        """, (user_id,))
        my_orders = cursor.fetchall()
        
        # user stats
        cursor.execute("SELECT wallet_balance FROM users WHERE user_id = %s", (user_id,))
        user_data = cursor.fetchone()
        wallet_balance = user_data['wallet_balance'] if user_data else 0
        
        cursor.execute("SELECT COUNT(*) as count FROM book_listings WHERE seller_id = %s", (user_id,))
        total_listings = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM orders WHERE buyer_id = %s", (user_id,))
        total_orders = cursor.fetchone()['count']
        
        cursor.execute("SELECT AVG(rating) as avg FROM reviews WHERE user_id = %s", (user_id,))
        avg_rating_result = cursor.fetchone()
        avg_rating = avg_rating_result['avg'] if avg_rating_result['avg'] else 0
        
        stats = {
            'wallet_balance': wallet_balance,
            'total_listings': total_listings,
            'total_orders': total_orders,
            'avg_rating': float(avg_rating) if avg_rating else 0
        }
        
        return render_template('userdashboard.html',
                             site_name='Librariya',
                             my_listings=my_listings, 
                             my_orders=my_orders, 
                             stats=stats,
                             is_logged_in='user_id' in session,
                             user_name=session.get('user_name', ''))
    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return render_template('userdashboard.html', 
                             site_name='Librariya',
                             my_listings=[], my_orders=[], 
                             stats={'wallet_balance': 0, 'total_listings': 0, 'total_orders': 0, 'avg_rating': 0},
                             is_logged_in='user_id' in session,
                             user_name=session.get('user_name', ''))
    finally:
        if connection:
            connection.close()

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    """Monthly quiz page"""
    connection = get_db_connection()
    if not connection:
        return render_template('quiz.html', 
                             site_name='Librariya',
                             quiz_active=False,
                             is_logged_in='user_id' in session,
                             user_name=session.get('user_name', ''))
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # current month's
        cursor.execute("""
            SELECT * FROM monthly_quiz 
            WHERE MONTH(quiz_date) = MONTH(NOW()) 
            AND YEAR(quiz_date) = YEAR(NOW()) 
            AND is_active = 1 
            LIMIT 1
        """)
        current_quiz = cursor.fetchone()
        
        if not current_quiz:
            return render_template('quiz.html', 
                                 site_name='Librariya',
                                 quiz_active=False,
                                 is_logged_in='user_id' in session,
                                 user_name=session.get('user_name', ''))
        
        if request.method == 'POST' and 'user_id' in session:
            # user already participated
            cursor.execute("""
                SELECT * FROM quiz_participants 
                WHERE user_id = %s AND quiz_id = %s
            """, (session['user_id'], current_quiz['quiz_id']))
            
            if cursor.fetchone():
                flash('You have already participated in this month\'s quiz!', 'warning')
                return redirect(url_for('quiz'))
            
            # answers
            answers = {}
            score = 0
            total_questions = 0
            
            for key, value in request.form.items():
                if key.startswith('question_'):
                    question_num = key.split('_')[1]
                    answers[question_num] = value
                    total_questions += 1
                    
            #Calculate score
            score = len(answers) * 10 
            
            # Save participation
            cursor.execute("""
                INSERT INTO quiz_participants (quiz_id, user_id, answers, score, completed_at)
                VALUES (%s, %s, %s, %s, NOW())
            """, (current_quiz['quiz_id'], session['user_id'], json.dumps(answers), score))
            
            connection.commit()
            flash(f'Quiz completed! Your score: {score}%', 'success')
            
            return render_template('quiz.html',
                                 site_name='Librariya',
                                 quiz_active=True,
                                 quiz=current_quiz,
                                 completed=True,
                                 score=score,
                                 is_logged_in='user_id' in session,
                                 user_name=session.get('user_name', ''))
        
        return render_template('quiz.html',
                             site_name='Librariya',
                             quiz_active=True,
                             quiz=current_quiz,
                             is_logged_in='user_id' in session,
                             user_name=session.get('user_name', ''))
    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return render_template('quiz.html', 
                             site_name='Librariya',
                             quiz_active=False,
                             is_logged_in='user_id' in session,
                             user_name=session.get('user_name', ''))
    finally:
        if connection:
            connection.close()

@app.errorhandler(500)
def internal_error(error):
    return render_template('404.html', site_name='Librariya'), 500

# Add try-catch to all database operations:
    try:
        cursor.execute(query, params)
        results = cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        results = []

@app.route('/stationery')
def stationery():
    """Stationery items page"""
    connection = get_db_connection()
    if not connection:
        return render_template('stationery.html', 
                             site_name='Librariya',
                             categories=[], items=[],
                             is_logged_in='user_id' in session,
                             user_name=session.get('user_name', ''))
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get stationery categories
        cursor.execute("SELECT * FROM stationery_categories WHERE is_active = 1 ORDER BY category_name")
        categories = cursor.fetchall()
        
        # Get search parameters
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        min_price = request.args.get('min_price', '')
        max_price = request.args.get('max_price', '')
        
        # Build query
        query = """
            SELECT s.*, sc.category_name
            FROM stationery_items s
            LEFT JOIN stationery_categories sc ON s.category_id = sc.category_id
            WHERE s.is_active = 1 AND s.stock_quantity > 0
        """
        params = []
        
        if search:
            query += " AND (s.item_name LIKE %s OR s.description LIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
        
        if category:
            query += " AND s.category_id = %s"
            params.append(category)
        
        if min_price and max_price:
            query += " AND s.price BETWEEN %s AND %s"
            params.extend([min_price, max_price])
        elif min_price:
            query += " AND s.price >= %s"
            params.append(min_price)
        elif max_price:
            query += " AND s.price <= %s"
            params.append(max_price)
        
        query += " ORDER BY s.created_at DESC"
        
        cursor.execute(query, params)
        items = cursor.fetchall()
        
        return render_template('stationery.html',
                             site_name='Librariya',
                             categories=categories,
                             items=items,
                             is_logged_in='user_id' in session,
                             user_name=session.get('user_name', ''))
    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return render_template('stationery.html', 
                             site_name='Librariya',
                             categories=[], items=[],
                             is_logged_in='user_id' in session,
                             user_name=session.get('user_name', ''))
    finally:
        if connection:
            connection.close()

@app.route('/stationery/<int:item_id>')
def stationery_details(item_id):
    """Stationery item details page"""
    connection = get_db_connection()
    if not connection:
        return render_template('404.html', site_name='Librariya'), 404
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT s.*, sc.category_name
            FROM stationery_items s
            LEFT JOIN stationery_categories sc ON s.category_id = sc.category_id
            WHERE s.item_id = %s AND s.is_active = 1
        """, (item_id,))
        item = cursor.fetchone()
        
        if not item:
            return render_template('404.html', site_name='Librariya'), 404
        
        # Get related items
        cursor.execute("""
            SELECT s.*, sc.category_name
            FROM stationery_items s
            LEFT JOIN stationery_categories sc ON s.category_id = sc.category_id
            WHERE s.category_id = %s AND s.item_id != %s AND s.is_active = 1
            ORDER BY RAND()
            LIMIT 4
        """, (item['category_id'], item_id))
        related_items = cursor.fetchall()
        
        return render_template('stationery_details.html',
                             site_name='Librariya',
                             item=item,
                             related_items=related_items,
                             is_logged_in='user_id' in session,
                             user_name=session.get('user_name', ''))
    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return render_template('404.html', site_name='Librariya'), 404
    finally:
        if connection:
            connection.close()

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection failed', 'error')
        return redirect(url_for('index'))
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get admin statistics
        try:
            cursor.execute("SELECT COUNT(*) as count FROM books WHERE is_active = 1")
            result = cursor.fetchone()
            total_books = result['count'] if result else 0
        except mysql.connector.Error:
            total_books = 0

        try:
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE user_type = 'customer' AND is_active = 1") 
            result = cursor.fetchone()
            total_users = result['count'] if result else 0
        except mysql.connector.Error:
            total_users = 0

        try:
            cursor.execute("SELECT COUNT(*) as count FROM book_listings WHERE status = 'active'")
            result = cursor.fetchone()
            active_listings = result['count'] if result else 0
        except mysql.connector.Error:
            active_listings = 0

        try:
            cursor.execute("SELECT COUNT(*) as count FROM orders WHERE order_status IN ('delivered', 'completed')")
            result = cursor.fetchone()
            completed_orders = result['count'] if result else 0
        except mysql.connector.Error:
            completed_orders = 0
        stats = {
            'total_books': total_books,
            'total_users': total_users,
            'active_listings': active_listings,
            'completed_orders': completed_orders
        }
        # Get recent books for admin dashboard
        cursor.execute("""
            SELECT b.title, 
                COALESCE(bl.status, 'inactive') as status,
                COALESCE(bl.sell_price, 0) as price
            FROM books b 
            LEFT JOIN book_listings bl ON b.book_id = bl.book_id 
            WHERE b.is_active = 1 
            ORDER BY b.created_at DESC 
            LIMIT 5
        """)
        recent_books = cursor.fetchall() or []

        # Get recent users for admin dashboard
        cursor.execute("""
            SELECT username, 
                is_active, 
                DATE_FORMAT(created_at, '%Y-%m-%d') as join_date
            FROM users 
            WHERE user_type = 'customer' 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        recent_users = cursor.fetchall() or []

        # Get recent orders for admin dashboard
        cursor.execute("""
            SELECT CONCAT('ORD', LPAD(order_id, 3, '0')) as order_number,
                order_status,
                total_amount
            FROM orders 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        recent_orders = cursor.fetchall() or []
        return render_template('admin.html', 
                             site_name='Librariya',
                             stats=stats,
                             recent_books=recent_books,
                             recent_users=recent_users,
                             recent_orders=recent_orders,
                             admin_name=session.get('user_name', 'Admin'),
                             is_logged_in='user_id' in session,
                             user_name=session.get('user_name', ''))
    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        flash('Error loading admin dashboard', 'error')
        return redirect(url_for('index'))
    finally:
        if connection:
            connection.close()


# Fixed Flask routes for cart functionality - DECIMAL COMPATIBLE

from decimal import Decimal, InvalidOperation

@app.route('/update_cart_quantity', methods=['POST'])
@login_required
def update_cart_quantity():
    """Update cart item quantity - DECIMAL COMPATIBLE VERSION"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get and validate input data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
            
        cart_id = data.get('cart_id')
        quantity = data.get('quantity')
        
        # Validate cart_id
        if not cart_id:
            return jsonify({'success': False, 'message': 'Cart ID is required'})
        
        # Convert and validate quantity
        try:
            quantity = int(quantity)
            if quantity < 1:
                quantity = 1
            elif quantity > 99:
                quantity = 99
        except (TypeError, ValueError):
            return jsonify({'success': False, 'message': 'Invalid quantity value'})
        
        # Verify cart item belongs to current user
        cursor.execute("""
            SELECT ci.*, si.stock_quantity, si.item_name as stationery_name,
                   b.title as book_title
            FROM cart_items ci
            LEFT JOIN stationery_items si ON ci.stationery_item_id = si.item_id
            LEFT JOIN book_listings bl ON ci.listing_id = bl.listing_id
            LEFT JOIN books b ON bl.book_id = b.book_id
            WHERE ci.cart_id = %s AND ci.user_id = %s
        """, (cart_id, session['user_id']))
        
        cart_item = cursor.fetchone()
        if not cart_item:
            return jsonify({'success': False, 'message': 'Cart item not found'})
        
        # Check stock for stationery items
        if cart_item['stationery_item_id'] and cart_item['stock_quantity'] is not None:
            if quantity > cart_item['stock_quantity']:
                return jsonify({
                    'success': False, 
                    'message': f'Only {cart_item["stock_quantity"]} items available in stock'
                })
        
        # Update quantity in database
        cursor.execute("""
            UPDATE cart_items 
            SET quantity = %s, added_at = CURRENT_TIMESTAMP
            WHERE cart_id = %s AND user_id = %s
        """, (quantity, cart_id, session['user_id']))
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': 'Failed to update quantity'})
        
        connection.commit()
        
        # Get updated cart count
        cursor.execute("""
            SELECT COALESCE(SUM(quantity), 0) as count 
            FROM cart_items 
            WHERE user_id = %s
        """, (session['user_id'],))
        
        cart_count_result = cursor.fetchone()
        cart_count = cart_count_result['count'] if cart_count_result else 0
        
        # Get item name for response
        item_name = cart_item['book_title'] or cart_item['stationery_name'] or 'Item'
        
        return jsonify({
            'success': True, 
            'message': f'{item_name} quantity updated to {quantity}',
            'cart_count': cart_count,
            'new_quantity': quantity
        })
    
    except mysql.connector.Error as e:
        print(f"Database error in update_cart_quantity: {e}")
        if connection:
            connection.rollback()
        return jsonify({'success': False, 'message': 'Database error occurred'})
    except Exception as e:
        print(f"Unexpected error in update_cart_quantity: {e}")
        if connection:
            connection.rollback()
        return jsonify({'success': False, 'message': 'An unexpected error occurred'})
    finally:
        if connection:
            connection.close()


@app.route('/remove_from_cart', methods=['POST'])
@login_required
def remove_from_cart():
    """Remove item from cart - FIXED VERSION"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get input data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
            
        cart_id = data.get('cart_id')
        
        if not cart_id:
            return jsonify({'success': False, 'message': 'Cart ID is required'})
        
        # Get item details before deletion for response message
        cursor.execute("""
            SELECT ci.*, si.item_name as stationery_name, b.title as book_title
            FROM cart_items ci
            LEFT JOIN stationery_items si ON ci.stationery_item_id = si.item_id
            LEFT JOIN book_listings bl ON ci.listing_id = bl.listing_id
            LEFT JOIN books b ON bl.book_id = b.book_id
            WHERE ci.cart_id = %s AND ci.user_id = %s
        """, (cart_id, session['user_id']))
        
        cart_item = cursor.fetchone()
        if not cart_item:
            return jsonify({'success': False, 'message': 'Cart item not found'})
        
        item_name = cart_item['book_title'] or cart_item['stationery_name'] or 'Item'
        
        # Remove item from cart
        cursor.execute("""
            DELETE FROM cart_items 
            WHERE cart_id = %s AND user_id = %s
        """, (cart_id, session['user_id']))
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': 'Failed to remove item'})
        
        connection.commit()
        
        # Get updated cart count
        cursor.execute("""
            SELECT COALESCE(SUM(quantity), 0) as count 
            FROM cart_items 
            WHERE user_id = %s
        """, (session['user_id'],))
        
        cart_count_result = cursor.fetchone()
        cart_count = cart_count_result['count'] if cart_count_result else 0
        
        return jsonify({
            'success': True, 
            'message': f'{item_name} removed from cart',
            'cart_count': cart_count
        })
    
    except mysql.connector.Error as e:
        print(f"Database error in remove_from_cart: {e}")
        if connection:
            connection.rollback()
        return jsonify({'success': False, 'message': 'Database error occurred'})
    except Exception as e:
        print(f"Unexpected error in remove_from_cart: {e}")
        if connection:
            connection.rollback()
        return jsonify({'success': False, 'message': 'An unexpected error occurred'})
    finally:
        if connection:
            connection.close()


@app.route('/get_cart_items_ajax')
@login_required
def get_cart_items_ajax():
    """Get cart items via AJAX for dynamic updates - DECIMAL COMPATIBLE"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get cart items with complete details
        cursor.execute("""
            SELECT ci.cart_id, ci.quantity, ci.rental_duration,
                   -- Book details
                   b.title AS book_title, b.cover_image,
                   bl.sell_price, bl.rent_price_per_month, bl.condition_type,
                   u.username AS seller_name,
                   -- Stationery details
                   si.item_name AS stationery_name, 
                   si.price AS stationery_price, 
                   si.image_url AS stationery_image,
                   si.stock_quantity
            FROM cart_items ci
            LEFT JOIN book_listings bl ON ci.listing_id = bl.listing_id
            LEFT JOIN books b ON bl.book_id = b.book_id
            LEFT JOIN users u ON bl.seller_id = u.user_id
            LEFT JOIN stationery_items si ON ci.stationery_item_id = si.item_id
            WHERE ci.user_id = %s
            ORDER BY ci.added_at DESC
        """, (session['user_id'],))
        
        cart_items = cursor.fetchall()
        
        # Calculate totals using Decimal
        total_amount = Decimal('0')
        total_quantity = 0
        
        for item in cart_items:
            total_quantity += item['quantity']
            
            # Calculate item total based on type using Decimal
            try:
                if item.get('rental_duration') and item['rental_duration'] > 0:
                    # Rental calculation
                    monthly_rate = Decimal(str(item.get('rent_price_per_month') or 0))
                    duration_days = Decimal(str(item['rental_duration']))
                    duration_months = duration_days / Decimal('30')
                    item_total = monthly_rate * duration_months * Decimal(str(item['quantity']))
                else:
                    # Purchase calculation
                    unit_price = Decimal(str(item.get('sell_price') or item.get('stationery_price') or 0))
                    item_total = unit_price * Decimal(str(item['quantity']))
                
                total_amount += item_total
                item['calculated_total'] = float(item_total)  # Convert to float for JSON
            except (ValueError, InvalidOperation):
                item['calculated_total'] = 0.0
        
        return jsonify({
            'success': True,
            'cart_items': cart_items,
            'total_amount': float(total_amount),  # Convert to float for JSON
            'total_quantity': total_quantity
        })
    
    except mysql.connector.Error as e:
        print(f"Database error in get_cart_items_ajax: {e}")
        return jsonify({'success': False, 'message': 'Database error occurred'})
    except Exception as e:
        print(f"Unexpected error in get_cart_items_ajax: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred'})
    finally:
        if connection:
            connection.close()


@app.route('/cart')
@login_required
def cart():
    """Shopping cart page - DECIMAL COMPATIBLE VERSION"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection failed', 'error')
        return render_template('cart.html',
                             site_name='Librariya',
                             cart_items=[],
                             total=Decimal('0'),
                             is_logged_in=True,
                             user_name=session.get('user_name', ''))
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get cart items with all necessary details
        cursor.execute("""
            SELECT ci.cart_id, ci.quantity, ci.rental_duration, ci.added_at,
                   -- Book details
                   b.title AS book_title, b.cover_image,
                   bl.sell_price, bl.rent_price_per_month, bl.condition_type,
                   u.username AS seller_name,
                   -- Stationery details
                   si.item_name AS stationery_name, 
                   si.price AS stationery_price, 
                   si.image_url AS stationery_image,
                   si.stock_quantity
            FROM cart_items ci
            LEFT JOIN book_listings bl ON ci.listing_id = bl.listing_id
            LEFT JOIN books b ON bl.book_id = b.book_id
            LEFT JOIN users u ON bl.seller_id = u.user_id
            LEFT JOIN stationery_items si ON ci.stationery_item_id = si.item_id
            WHERE ci.user_id = %s
            ORDER BY ci.added_at DESC
        """, (session['user_id'],))
        
        cart_items = cursor.fetchall()
        
        # Calculate total with proper Decimal handling
        total = Decimal('0')
        for item in cart_items:
            try:
                quantity = int(item.get('quantity', 1))
                
                if item.get('rental_duration') and item['rental_duration'] > 0:
                    # Rental calculation using Decimal
                    monthly_rate = Decimal(str(item.get('rent_price_per_month') or 0))
                    duration_days = Decimal(str(item['rental_duration']))
                    duration_months = duration_days / Decimal('30')
                    item_total = monthly_rate * duration_months * Decimal(str(quantity))
                else:
                    # Purchase calculation using Decimal
                    unit_price = Decimal(str(item.get('sell_price') or item.get('stationery_price') or 0))
                    item_total = unit_price * Decimal(str(quantity))
                
                total += item_total
                item['calculated_total'] = item_total
            except (TypeError, ValueError, InvalidOperation) as e:
                print(f"Error calculating item total: {e}")
                item['calculated_total'] = Decimal('0')
        
        return render_template('cart.html',
                             site_name='Librariya',
                             cart_items=cart_items,
                             total=total,
                             is_logged_in=True,
                             user_name=session.get('user_name', ''))
    
    except mysql.connector.Error as e:
        print(f"Database error in cart: {e}")
        flash('Error loading cart', 'error')
        return render_template('cart.html',
                             site_name='Librariya',
                             cart_items=[],
                             total=Decimal('0'),
                             is_logged_in=True,
                             user_name=session.get('user_name', ''))
    finally:
        if connection:
            connection.close()


@app.route('/get_cart_count')
@login_required
def get_cart_count():
    """Get current cart item count for display in header"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'count': 0})
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT COALESCE(SUM(quantity), 0) as count FROM cart_items WHERE user_id = %s", (session['user_id'],))
        result = cursor.fetchone()
        cart_count = result['count'] if result else 0
        return jsonify({'count': cart_count})
    
    except mysql.connector.Error as e:
        print(f"Database error in get_cart_count: {e}")
        return jsonify({'count': 0})
    finally:
        if connection:
            connection.close()


@app.route('/test_db')
def test_db():
    """Test database connection"""
    connection = get_db_connection()
    if not connection:
        return "❌ Failed to connect to database"
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM books")
        count = cursor.fetchone()[0]
        return f"✅ Connected! Found {count} books"
    except Exception as e:
        return f"❌ Query failed: {e}"
    finally:
        if connection:
            connection.close()
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)