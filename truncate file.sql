-- Disable foreign key checks temporarily
SET FOREIGN_KEY_CHECKS = 0;

-- Truncate all tables
TRUNCATE TABLE cart_items;
TRUNCATE TABLE order_items;
TRUNCATE TABLE orders;
TRUNCATE TABLE book_listings;
TRUNCATE TABLE book_authors;
TRUNCATE TABLE book_categories;
TRUNCATE TABLE books;
TRUNCATE TABLE authors;
TRUNCATE TABLE publishers;
TRUNCATE TABLE categories;
TRUNCATE TABLE stationery_items;
TRUNCATE TABLE stationery_categories;
TRUNCATE TABLE reviews;
TRUNCATE TABLE donations;
TRUNCATE TABLE book_donations;
TRUNCATE TABLE monthly_quiz;
TRUNCATE TABLE quiz_participants;
TRUNCATE TABLE ebooks;
TRUNCATE TABLE notifications;
TRUNCATE TABLE users;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;
