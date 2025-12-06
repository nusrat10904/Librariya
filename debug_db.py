#!/usr/bin/env python3
"""
Debug script to check Flask app database connection and data
Run this script to diagnose why books aren't showing up
"""

import mysql.connector
from werkzeug.security import generate_password_hash

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

def check_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("✅ Database connection successful!")
            return connection
        else:
            print("❌ Database connection failed!")
            return None
    except mysql.connector.Error as e:
        print(f"❌ Database connection error: {e}")
        print("💡 Make sure:")
        print("   - MySQL/XAMPP is running")
        print("   - Database 'Librariya' exists")
        print("   - Username/password are correct")
        return None

def check_tables(connection):
    """Check if required tables exist"""
    print("\n🔍 Checking database tables...")
    cursor = connection.cursor()
    
    required_tables = ['books', 'authors', 'categories', 'book_listings', 'book_authors', 'book_categories', 'users']
    
    try:
        cursor.execute("SHOW TABLES")
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        print(f"📋 Found tables: {existing_tables}")
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            print("💡 Run the schema.sql file to create missing tables")
            return False
        else:
            print("✅ All required tables exist!")
            return True
            
    except mysql.connector.Error as e:
        print(f"❌ Error checking tables: {e}")
        return False

def check_data(connection):
    """Check if tables have data"""
    print("\n🔍 Checking table data...")
    cursor = connection.cursor(dictionary=True)
    
    # Check books
    try:
        cursor.execute("SELECT COUNT(*) as count FROM books")
        book_count = cursor.fetchone()['count']
        print(f"📚 Books in database: {book_count}")
        
        if book_count == 0:
            print("❌ No books found in database!")
            print("💡 Run the sampledata.sql file to add sample books")
            return False
        
        # Check authors
        cursor.execute("SELECT COUNT(*) as count FROM authors")
        author_count = cursor.fetchone()['count']
        print(f"👤 Authors in database: {author_count}")
        
        # Check categories  
        cursor.execute("SELECT COUNT(*) as count FROM categories")
        category_count = cursor.fetchone()['count']
        print(f"📂 Categories in database: {category_count}")
        
        # Check book listings
        cursor.execute("SELECT COUNT(*) as count FROM book_listings WHERE status = 'active'")
        listing_count = cursor.fetchone()['count']
        print(f"🏪 Active book listings: {listing_count}")
        
        if listing_count == 0:
            print("⚠️  No active book listings found!")
            print("💡 Books need listings to be visible on the browse page")
        
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Error checking data: {e}")
        return False

def show_sample_query_result(connection):
    """Show what the book query should return"""
    print("\n🔍 Testing the actual book query from app.py...")
    cursor = connection.cursor(dictionary=True)
    
    try:
        # This is the same query used in your app.py book() function
        query = """
        SELECT DISTINCT
            b.book_id as id, 
            b.title, 
            b.cover_image as image,
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
        GROUP BY 
            b.book_id, 
            b.title, 
            b.cover_image, 
            c.category_name, 
            bl.condition_type
        ORDER BY b.created_at DESC 
        LIMIT 5
        """
        
        cursor.execute(query)
        books = cursor.fetchall()
        
        print(f"📖 Query returned {len(books)} books:")
        for book in books:
            print(f"   - {book['title']} by {book['author']} (₹{book['price']})")
        
        if len(books) == 0:
            print("❌ Query returned no books!")
            print("💡 This means the query or data has an issue")
        else:
            print("✅ Query working correctly!")
            
    except mysql.connector.Error as e:
        print(f"❌ Error running book query: {e}")

def add_sample_data_if_missing(connection):
    """Add minimal sample data if none exists"""
    print("\n🔍 Checking if we need to add sample data...")
    cursor = connection.cursor()
    
    try:
        # Check if we have any books
        cursor.execute("SELECT COUNT(*) FROM books")
        book_count = cursor.fetchone()[0]
        
        if book_count == 0:
            print("📝 Adding sample data...")
            
            # Add sample author
            cursor.execute("""
                INSERT INTO authors (first_name, last_name, biography, nationality)
                VALUES ('J.K.', 'Rowling', 'Author of Harry Potter series', 'British')
            """)
            author_id = cursor.lastrowid
            
            # Add sample category
            cursor.execute("""
                INSERT INTO categories (category_name, description, is_active)
                VALUES ('Fiction', 'Fiction books including novels', TRUE)
            """)
            category_id = cursor.lastrowid
            
            # Add sample book
            cursor.execute("""
                INSERT INTO books (title, description, is_active, created_at)
                VALUES ('Harry Potter Test Book', 'Sample book for testing', TRUE, NOW())
            """)
            book_id = cursor.lastrowid
            
            # Link book and author
            cursor.execute("""
                INSERT INTO book_authors (book_id, author_id, author_order)
                VALUES (%s, %s, 1)
            """, (book_id, author_id))
            
            # Link book and category
            cursor.execute("""
                INSERT INTO book_categories (book_id, category_id)
                VALUES (%s, %s)
            """, (book_id, category_id))
            
            # Add sample user for listing
            password_hash = generate_password_hash('password123')
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, first_name, last_name, user_type, is_active, email_verified)
                VALUES ('testuser', 'test@example.com', %s, 'Test', 'User', 'seller', TRUE, TRUE)
            """, (password_hash,))
            user_id = cursor.lastrowid
            
            # Add sample listing
            cursor.execute("""
                INSERT INTO book_listings (book_id, seller_id, listing_type, condition_type, sell_price, status, created_at)
                VALUES (%s, %s, 'sell', 'good', 25.00, 'active', NOW())
            """, (book_id, user_id))
            
            connection.commit()
            print("✅ Sample data added successfully!")
            
        else:
            print(f"✅ Database already has {book_count} books")
            
    except mysql.connector.Error as e:
        print(f"❌ Error adding sample data: {e}")
        connection.rollback()

def main():
    print("🚀 Librariya Database Diagnostic Tool")
    print("=" * 50)
    
    # Step 1: Test connection
    connection = check_database_connection()
    if not connection:
        return
    
    # Step 2: Check tables
    tables_ok = check_tables(connection)
    if not tables_ok:
        connection.close()
        return
    
    # Step 3: Check data
    data_ok = check_data(connection)
    
    # Step 4: Add sample data if needed
    if not data_ok:
        add_sample_data_if_missing(connection)
    
    # Step 5: Test the actual query
    show_sample_query_result(connection)
    
    print("\n" + "=" * 50)
    print("🎯 Next steps:")
    print("1. Make sure XAMPP/MySQL is running")
    print("2. Run your Flask app: python app.py")
    print("3. Visit: http://127.0.0.1:5000/books")
    print("4. If still no books, check Flask console for errors")
    
    connection.close()

if __name__ == "__main__":
    main()