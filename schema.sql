-- =====================================
-- Librariya Database Schema (DDL) - Fixed Version
-- =====================================

CREATE DATABASE IF NOT EXISTS Librariya;
USE Librariya;

SET FOREIGN_KEY_CHECKS = 0;

-- -------------------------
-- Core: Users, Authors,
-- Publishers, Categories
-- -------------------------

CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    city VARCHAR(100),
    country VARCHAR(100),
    address TEXT,
    wallet_balance DECIMAL(10,2) DEFAULT 0.00,
    rating DECIMAL(3,2) DEFAULT 0.00,
    user_type ENUM('admin','customer','seller') DEFAULT 'customer',
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS authors (
    author_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    biography TEXT,
    nationality VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS publishers (
    publisher_id INT PRIMARY KEY AUTO_INCREMENT,
    publisher_name VARCHAR(255) NOT NULL,
    address VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(150),
    established_year INT,
    website VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -------------------------
-- Books & Ebooks
-- -------------------------

CREATE TABLE IF NOT EXISTS books (
    book_id INT PRIMARY KEY AUTO_INCREMENT,
    isbn VARCHAR(50),
    title VARCHAR(255) NOT NULL,
    subtitle VARCHAR(255),
    description TEXT,
    publisher_id INT,
    publication_date DATE,
    language VARCHAR(50) DEFAULT 'English',
    pages INT,
    cover_image VARCHAR(500),
    average_rating DECIMAL(3,2) DEFAULT 0.00,
    total_reviews INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (publisher_id) REFERENCES publishers(publisher_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS book_authors (
    book_id INT,
    author_id INT,
    author_order INT DEFAULT 1,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(author_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS book_categories (
    book_id INT,
    category_id INT,
    PRIMARY KEY (book_id, category_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS book_listings (
    listing_id INT PRIMARY KEY AUTO_INCREMENT,
    book_id INT NOT NULL,
    seller_id INT NOT NULL,
    listing_type ENUM('sell','rent','both') NOT NULL,
    condition_type ENUM('new','like_new','very_good','good','acceptable') NOT NULL,
    sell_price DECIMAL(10,2),
    rent_price_per_day DECIMAL(10,2),
    rent_price_per_week DECIMAL(10,2),
    rent_price_per_month DECIMAL(10,2),
    description TEXT,
    location VARCHAR(255),
    is_pickup_available BOOLEAN DEFAULT TRUE,
    is_shipping_available BOOLEAN DEFAULT TRUE,
    status ENUM('active','pending','sold','inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (seller_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- -------------------------
-- Stationery
-- -------------------------

CREATE TABLE IF NOT EXISTS stationery_categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stationery_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    item_name VARCHAR(255) NOT NULL,
    category_id INT,
    brand VARCHAR(100),
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES stationery_categories(category_id) ON DELETE SET NULL
);

-- -------------------------
-- Cart (Fixed to match app expectations)
-- -------------------------

CREATE TABLE IF NOT EXISTS cart_items (
    cart_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    listing_id INT NULL,
    stationery_item_id INT NULL,
    quantity INT DEFAULT 1,
    rental_duration INT NULL, -- in days
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (listing_id) REFERENCES book_listings(listing_id) ON DELETE CASCADE,
    FOREIGN KEY (stationery_item_id) REFERENCES stationery_items(item_id) ON DELETE CASCADE
);

-- -------------------------
-- Orders (Fixed to match app expectations)
-- -------------------------

CREATE TABLE IF NOT EXISTS orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    buyer_id INT NOT NULL,
    order_type ENUM('purchase','rental','mixed') DEFAULT 'purchase',
    total_amount DECIMAL(10,2) NOT NULL,
    shipping_address TEXT,
    payment_method ENUM('cash','card','mobile_banking','bank_transfer') DEFAULT 'cash',
    payment_status ENUM('pending','paid','failed','refunded') DEFAULT 'pending',
    order_status ENUM('pending','confirmed','processing','shipped','delivered','cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (buyer_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    listing_id INT NULL,
    stationery_item_id INT NULL,
    quantity INT DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    rental_start_date DATE NULL,
    rental_end_date DATE NULL,
    rental_duration INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (listing_id) REFERENCES book_listings(listing_id) ON DELETE SET NULL,
    FOREIGN KEY (stationery_item_id) REFERENCES stationery_items(item_id) ON DELETE SET NULL
);

-- -------------------------
-- Reviews (Fixed to match app expectations)
-- -------------------------

CREATE TABLE IF NOT EXISTS reviews (
    review_id INT PRIMARY KEY AUTO_INCREMENT,
    book_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    review_text TEXT,
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_book_review (user_id, book_id)
);

-- -------------------------
-- Donations (Fixed - both tables for compatibility)
-- -------------------------

CREATE TABLE IF NOT EXISTS donations (
    donation_id INT PRIMARY KEY AUTO_INCREMENT,
    donor_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT DEFAULT 1,
    condition_type ENUM('new','like_new','very_good','good','acceptable') NOT NULL,
    donation_type ENUM('library','charity','school','community') NOT NULL,
    recipient_organization VARCHAR(255),
    pickup_required BOOLEAN DEFAULT FALSE,
    pickup_address TEXT,
    status ENUM('pending','approved','rejected','completed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS book_donations (
    donation_id INT PRIMARY KEY AUTO_INCREMENT,
    book_id INT NOT NULL,
    donor_id INT NOT NULL,
    recipient_type ENUM('library','charity','school','community') NOT NULL,
    condition_type ENUM('new','like_new','very_good','good','acceptable') NOT NULL,
    quantity INT DEFAULT 1,
    special_notes TEXT,
    status ENUM('pending','approved','rejected','completed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
);

-- -------------------------
-- Quizzes (Fixed to match app expectations)
-- -------------------------

CREATE TABLE IF NOT EXISTS monthly_quiz (
    quiz_id INT PRIMARY KEY AUTO_INCREMENT,
    quiz_title VARCHAR(255) NOT NULL,
    quiz_description TEXT,
    quiz_date DATE NOT NULL,
    quiz_data JSON NOT NULL,
    prize_description VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quiz_participants (
    participant_id INT PRIMARY KEY AUTO_INCREMENT,
    quiz_id INT NOT NULL,
    user_id INT NOT NULL,
    answers JSON,
    score INT DEFAULT 0,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (quiz_id) REFERENCES monthly_quiz(quiz_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_quiz (user_id, quiz_id)
);

-- -------------------------
-- Additional tables for completeness
-- -------------------------

CREATE TABLE IF NOT EXISTS ebooks (
    ebook_id INT PRIMARY KEY AUTO_INCREMENT,
    book_id INT NOT NULL,
    seller_id INT NOT NULL,
    file_path VARCHAR(500),
    file_size BIGINT,
    file_format ENUM('PDF','EPUB','MOBI','AZW','TXT') DEFAULT 'PDF',
    price DECIMAL(10,2) NOT NULL,
    preview_pages INT DEFAULT 0,
    drm_protected BOOLEAN DEFAULT TRUE,
    download_limit INT DEFAULT 3,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (seller_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    type ENUM('system','quiz','order_status','donation','message') DEFAULT 'system',
    title VARCHAR(255) NOT NULL,
    content TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- -------------------------
-- Indexes for performance
-- -------------------------

CREATE INDEX idx_books_active ON books(is_active);
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_created_at ON books(created_at);
CREATE INDEX idx_book_listings_status ON book_listings(status);
CREATE INDEX idx_book_listings_seller ON book_listings(seller_id);
CREATE INDEX idx_orders_buyer ON orders(buyer_id);
CREATE INDEX idx_orders_status ON orders(order_status);
CREATE INDEX idx_cart_items_user ON cart_items(user_id);
CREATE INDEX idx_reviews_book ON reviews(book_id);
CREATE INDEX idx_reviews_approved ON reviews(is_approved);

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE publishers;
DROP TABLE ebooks;
DROP TABLE notifications;
-- From users table:
ALTER TABLE users DROP COLUMN country;
ALTER TABLE users DROP COLUMN address;  -- app uses shipping_address in orders

-- From authors table:
ALTER TABLE authors DROP COLUMN biography;
ALTER TABLE authors DROP COLUMN nationality;

-- From books table:
ALTER TABLE books DROP COLUMN subtitle;
ALTER TABLE books DROP COLUMN publisher_id;  -- since publishers table removed

-- From book_listings table:
ALTER TABLE book_listings DROP COLUMN rent_price_per_day;
ALTER TABLE book_listings DROP COLUMN rent_price_per_week;
-- Only rent_price_per_month is used

-- From stationery_items table:
ALTER TABLE stationery_items DROP COLUMN brand;  -- not used in app

-- Add this after creating the users table in your schema

-- Create admin user with permanent password
INSERT INTO users (
    username, 
    email, 
    password_hash, 
    first_name, 
    last_name, 
    user_type, 
    is_active, 
    email_verified
) VALUES (
    'admin',
    'admin@librariya.com',
    'scrypt:32768:8:1$salt$hash',  -- This will need to be generated
    'System',
    'Administrator', 
    'admin',
    TRUE,
    TRUE
) ON DUPLICATE KEY UPDATE password_hash = VALUES(password_hash);

-- Note: You need to generate the actual hash. Run this Python code to get it:
-- from werkzeug.security import generate_password_hash
-- print(generate_password_hash('admin123'))

-- Create admin user (run after all tables are created)
-- First generate the hash by running: python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('admin123'))"
-- Then replace the placeholder below with the actual hash

-- For immediate setup, run this after creating tables:
INSERT INTO users (
    username, email, password_hash, first_name, last_name, 
    user_type, is_active, email_verified
) VALUES (
    'admin', 
    'admin@librariya.com', 
    'REPLACE_WITH_ACTUAL_HASH',  -- Replace this with generated hash
    'System', 
    'Administrator',
    'admin', 
    TRUE, 
    TRUE
) ON DUPLICATE KEY UPDATE 
    password_hash = VALUES(password_hash),
    is_active = TRUE;
