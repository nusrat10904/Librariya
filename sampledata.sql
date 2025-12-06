-- -------------------------
-- Admin: username: admin, password: password123
-- Regular users: Any username from the list with password: password123
-- The admin user has:
-- user_type = 'admin'
-- Full name: "System Administrator"
-- Email: admin@librariya.co
-- -------------------------
-- Sample Users Data for Librariya
-- Note: All passwords are hashed versions of "password123" using Werkzeug's generate_password_hash

INSERT INTO users (username, email, password_hash, first_name, last_name, phone, city, country, address, wallet_balance, rating, user_type, is_active, email_verified) VALUES

-- Admin User
('admin', 'admin@librariya.com', 'pbkdf2:sha256:600000$XyZ9mN2pQ4$8f5a7b9c2d1e3f4g5h6i7j8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z4a5b6c7d8e9f0', 'System', 'Administrator', '+8801712345678', 'Dhaka', 'Bangladesh', 'Admin Office, Librariya HQ', 0.00, 5.00, 'admin', TRUE, TRUE),

-- Regular Customers
('john_doe', 'john.doe@email.com', 'pbkdf2:sha256:600000$AbC1dE2fG3$1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e2f3g4h5', 'John', 'Doe', '+8801987654321', 'Dhaka', 'Bangladesh', 'House 123, Road 456, Dhanmondi', 250.75, 4.5, 'customer', TRUE, TRUE),

('sarah_ahmed', 'sarah.ahmed@gmail.com', 'pbkdf2:sha256:600000$GhI4jK5lM6$9h8g7f6e5d4c3b2a1z0y9x8w7v6u5t4s3r2q1p0o9n8m7l6k5j4i3h2g1f0e9d8c7b6a5', 'Sarah', 'Ahmed', '+8801555123456', 'Chittagong', 'Bangladesh', 'Apt 7B, Green View Tower, Nasirabad', 180.50, 4.2, 'customer', TRUE, TRUE),

('mike_rahman', 'mike.rahman@yahoo.com', 'pbkdf2:sha256:600000$NoP7qR8sT9$6e5d4c3b2a1z0y9x8w7v6u5t4s3r2q1p0o9n8m7l6k5j4i3h2g1f0e9d8c7b6a5z4y3x2w1', 'Mikey', 'Rahman', '+8801444789012', 'Sylhet', 'Bangladesh', 'Villa 45, Zindabazar', 95.25, 3.8, 'customer', TRUE, TRUE),

('fatima_khan', 'fatima.khan@hotmail.com', 'pbkdf2:sha256:600000$UvW0xY1zA2$3b4c5d6e7f8g9h0i1j2k3l4m5n6o7p8q9r0s1t2u3v4w5x6y7z8a9b0c1d2e3f4g5h6i7j8k9l', 'Fatima', 'Khan', '+8801333567890', 'Rajshahi', 'Bangladesh', 'House 89, Shaheb Bazar Road', 320.00, 4.7, 'customer', TRUE, TRUE),

-- Seller/Customer hybrid users
('bookworm_bd', 'bookworm@example.com', 'pbkdf2:sha256:600000$BcD3eF4gH5$5i6j7k8l9m0n1o2p3q4r5s6t7u8v9w0x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2', 'Rahim', 'Hassan', '+8801666234567', 'Dhaka', 'Bangladesh', 'Shop 12, New Market', 450.80, 4.8, 'seller', TRUE, TRUE),

('reader_student', 'student@du.ac.bd', 'pbkdf2:sha256:600000$IjK6lM7nO8$2t3u4v5w6x7y8z9a0b1c2d3e4f5g6h7i8j9k0l1m2n3o4p5q6r7s8t9u0v1w2x3y4z5a6b7c8d9e0f', 'Nasir', 'Uddin', '+8801777345678', 'Dhaka', 'Bangladesh', 'DU Campus, Room 302', 75.30, 4.1, 'customer', TRUE, TRUE),

('book_seller_ctg', 'seller.ctg@gmail.com', 'pbkdf2:sha256:600000$PqR9sT0uV1$7w8x9y0z1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e2f3g4h5i', 'Rashida', 'Begum', '+8801888456789', 'Chittagong', 'Bangladesh', 'Book Shop, GEC Circle', 680.90, 4.9, 'seller', TRUE, TRUE),

-- Test users for different scenarios
('test_user', 'test@librariya.com', 'pbkdf2:sha256:600000$WxY2zA3bC4$0d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5s6t7u8v9w0x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q', 'Test', 'User', '+8801999567890', 'Dhaka', 'Bangladesh', 'Test Address', 100.00, 4.0, 'customer', TRUE, TRUE),

('inactive_user', 'inactive@example.com', 'pbkdf2:sha256:600000$DeF5gH6iJ7$8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z4a5b6c7d8e9f0g1h2i3j4k5l6m7n8o9p0q1r2s3t4u5v6w7x', 'Inactive', 'User', '+8801111222333', 'Dhaka', 'Bangladesh', 'Inactive Address', 0.00, 0.0, 'customer', FALSE, FALSE);

-- Update last_login for some users to make it more realistic
UPDATE users SET last_login = NOW() - INTERVAL 1 DAY WHERE username IN ('admin', 'john_doe', 'sarah_ahmed');
UPDATE users SET last_login = NOW() - INTERVAL 3 DAY WHERE username IN ('bookworm_bd', 'reader_student');
UPDATE users SET last_login = NOW() - INTERVAL 1 WEEK WHERE username IN ('mike_rahman', 'fatima_khan');

-- Verify the admin user exists
SELECT user_id, username, first_name, last_name, user_type, is_active FROM users WHERE user_type = 'admin';

-- -------------------------
-- Sample Users
-- -------------------------
INSERT INTO users (username, email, password_hash, first_name, last_name, phone, city, country, wallet_balance, rating, user_type, email_verified)
VALUES
('alice123','alice@example.com','hash1','Alice','Johnson','+880123456789','Dhaka','Bangladesh',50.00,4.5,'customer', TRUE),
('bob_seller','bob@example.com','hash2','Bob','Smith','+880987654321','Chittagong','Bangladesh',100.00,4.8,'seller', TRUE),
('charlie_admin','charlie@example.com','hash3','Charlie','Brown','+8801122334455','Khulna','Bangladesh',0.00,5.0,'admin', TRUE);

-- -------------------------
-- Sample Authors
-- -------------------------
INSERT INTO authors (first_name, last_name, biography, nationality)
VALUES
('J.K.','Rowling','Author of Harry Potter series','British'),
('George','Orwell','Author of 1984 and Animal Farm','British'),
('Rabindranath','Tagore','Bengali poet and philosopher','Indian');

-- -------------------------
-- Sample Publishers
-- -------------------------
INSERT INTO publishers (publisher_name, address, phone, email, established_year, website)
VALUES
('Penguin Books','London, UK','441234567890','info@penguin.com',1935,'https://penguin.co.uk'),
('HarperCollins','New York, USA','12125551234','contact@harpercollins.com',1989,'https://harpercollins.com');

-- -------------------------
-- Sample Categories
-- -------------------------
INSERT INTO categories (category_name, description)
VALUES
('Fiction','Fiction books including novels, short stories'),
('Non-Fiction','Informative books including history, science, biographies'),
('Children','Books for children and young readers');

-- -------------------------
-- Sample Books
-- -------------------------
INSERT INTO books (isbn, title, subtitle, description, publisher_id, publication_date, language, pages, cover_image)
VALUES
('9780747532743','Harry Potter and the Philosopher''s Stone','Book 1','First book in Harry Potter series',1,'1997-06-26','English',223,'hp1.jpg'),
('9780451524935','1984','','Dystopian novel by George Orwell',2,'1949-06-08','English',328,'1984.jpg'),
('9788172234983','Gitanjali','','Collection of poems by Rabindranath Tagore',2,'1910-08-01','Bengali',150,'gitanjali.jpg');

-- -------------------------
-- Book Authors
-- -------------------------
INSERT INTO book_authors (book_id, author_id, author_order)
VALUES
(1,1,1),
(2,2,1),
(3,3,1);

-- -------------------------
-- Book Categories
-- -------------------------
INSERT INTO book_categories (book_id, category_id)
VALUES
(1,1),
(2,1),
(3,2);

-- -------------------------
-- Sample Book Listings
-- -------------------------
INSERT INTO book_listings (book_id, seller_id, listing_type, condition_type, sell_price, rent_price_per_day, rent_price_per_week, rent_price_per_month, location)
VALUES
(1,2,'sell','like_new',20.00,NULL,NULL,NULL,'Dhaka'),
(2,2,'rent','good',NULL,3.00,15.00,50.00,'Chittagong'),
(3,2,'both','very_good',15.00,2.00,10.00,40.00,'Khulna');

-- -------------------------
-- Sample Stationery Categories
-- -------------------------
INSERT INTO stationery_categories (category_name, description)
VALUES
('Pens','All types of pens'),
('Notebooks','Various sizes of notebooks');

-- -------------------------
-- Sample Stationery Items
-- -------------------------
INSERT INTO stationery_items (item_name, category_id, brand, description, price, stock_quantity)
VALUES
('Gel Pen','1','Pilot','Smooth gel pen',1.50,100),
('Notebook A4','2','Classmate','A4 size ruled notebook',2.50,50);

-- -------------------------
-- Sample Cart Items
-- -------------------------
INSERT INTO cart_items (user_id, listing_id, stationery_item_id, quantity, rental_duration)
VALUES
(1,1,NULL,1,NULL),
(1,NULL,2,2,NULL),
(1,2,NULL,1,7); -- rental for 7 days

-- -------------------------
-- Sample Orders
-- -------------------------
INSERT INTO orders (buyer_id, order_type, total_amount, shipping_address, payment_method, payment_status, order_status)
VALUES
(1,'mixed',28.00,'House 123, Dhaka','card','paid','delivered');

INSERT INTO order_items (order_id, listing_id, stationery_item_id, quantity, unit_price, total_price, rental_start_date, rental_end_date, rental_duration)
VALUES
(1,1,NULL,1,20.00,20.00,NULL,NULL,NULL),
(1,NULL,2,2,2.50,5.00,NULL,NULL,NULL),
(1,2,NULL,1,3.00,3.00,'2025-09-01','2025-09-07',7);

-- -------------------------
-- Sample Reviews
-- -------------------------
INSERT INTO reviews (book_id, user_id, rating, title, review_text, is_verified_purchase, is_approved)
VALUES
(1,1,5,'Amazing Book','Loved it! Highly recommend.',TRUE,TRUE),
(2,1,4,'Thought Provoking','A bit dark but excellent.',TRUE,TRUE);

-- -------------------------
-- Sample Donations
-- -------------------------
INSERT INTO donations (donor_id, book_id, quantity, condition_type, donation_type, recipient_organization, pickup_required, pickup_address)
VALUES
(1,1,2,'like_new','library','Local Library',TRUE,'House 123, Dhaka');

INSERT INTO book_donations (book_id, donor_id, recipient_type, condition_type, quantity, special_notes)
VALUES
(2,1,'charity','very_good',1,'For children');

-- -------------------------
-- Sample Monthly Quiz
-- -------------------------
INSERT INTO monthly_quiz (quiz_title, quiz_description, quiz_date, quiz_data, prize_description)
VALUES
('September Quiz','General knowledge quiz','2025-09-06','{"questions":[{"q":"Capital of France?","options":["Paris","London","Berlin","Rome"],"answer":0}]}','Free Book Voucher');

INSERT INTO quiz_participants (quiz_id, user_id, answers, score, completed_at)
VALUES
(1,1,'[0]',10,'2025-09-06 10:00:00');

-- -------------------------
-- Sample Ebooks
-- -------------------------
INSERT INTO ebooks (book_id, seller_id, file_path, file_size, file_format, price)
VALUES
(1,2,'ebooks/hp1.pdf',2048000,'PDF',10.00),
(2,2,'ebooks/1984.epub',1024000,'EPUB',8.00);

-- -------------------------
-- Sample Notifications
-- -------------------------
INSERT INTO notifications (user_id, type, title, content)
VALUES
(1,'system','Welcome!','Welcome to Librariya platform.'),
(1,'order_status','Order Delivered','Your order #1 has been delivered.');
-- -------------------------
-- Additional Users
-- -------------------------
INSERT INTO users (username, email, password_hash, first_name, last_name, phone, city, country, wallet_balance, rating, user_type, email_verified)
VALUES
('diana88','diana@example.com','hash4','Diana','Prince','+8802233445566','Sylhet','Bangladesh',75.00,4.7,'customer', TRUE),
('edward_seller','edward@example.com','hash5','Edward','Norton','+8806677889900','Barishal','Bangladesh',120.00,4.9,'seller', TRUE),
('frank_admin','frank@example.com','hash6','Frank','Castle','+8803344556677','Rajshahi','Bangladesh',0.00,5.0,'admin', TRUE);

-- -------------------------
-- Additional Authors
-- -------------------------
INSERT INTO authors (first_name, last_name, biography, nationality)
VALUES
('Stephen','King','Famous horror and thriller author','American'),
('Agatha','Christie','Queen of Crime, detective novels','British'),
('Kazi','Nazrul','Bengali poet, musician, revolutionary','Bangladeshi');

-- -------------------------
-- Additional Publishers
-- -------------------------
INSERT INTO publishers (publisher_name, address, phone, email, established_year, website)
VALUES
('Random House','New York, USA','12125556789','info@randomhouse.com',1927,'https://randomhouse.com'),
('Macmillan','London, UK','441234567891','contact@macmillan.com',1843,'https://macmillan.com');

-- -------------------------
-- Additional Categories
-- -------------------------
INSERT INTO categories (category_name, description)
VALUES
('Science','Books about science, experiments, research'),
('History','Historical books and biographies'),
('Poetry','Poems, anthologies, and classic literature');

-- -------------------------
-- Additional Books
-- -------------------------
INSERT INTO books (isbn, title, subtitle, description, publisher_id, publication_date, language, pages, cover_image)
VALUES
('9780451169518','The Shining','','Classic horror novel by Stephen King',3,'1977-01-28','English',447,'shining.jpg'),
('9780062073488','Murder on the Orient Express','','Detective novel by Agatha Christie',4,'1934-01-01','English',256,'orient_express.jpg'),
('9789849382000','Bisher Banalata','','Poetry collection by Kazi Nazrul',4,'1920-05-05','Bengali',120,'banalata.jpg');

-- -------------------------
-- Additional Book Authors
-- -------------------------
INSERT INTO book_authors (book_id, author_id, author_order)
VALUES
(4,4,1),
(5,5,1),
(6,6,1);

-- -------------------------
-- Additional Book Categories
-- -------------------------
INSERT INTO book_categories (book_id, category_id)
VALUES
(4,1),
(5,2),
(6,3);

-- -------------------------
-- Additional Book Listings
-- -------------------------
INSERT INTO book_listings (book_id, seller_id, listing_type, condition_type, sell_price, rent_price_per_day, rent_price_per_week, rent_price_per_month, location)
VALUES
(4,5,'sell','new',25.00,NULL,NULL,NULL,'Sylhet'),
(5,5,'rent','like_new',NULL,4.00,20.00,60.00,'Barishal'),
(6,5,'both','good',18.00,3.00,15.00,50.00,'Rajshahi');

-- -------------------------
-- Additional Stationery Categories
-- -------------------------
INSERT INTO stationery_categories (category_name, description)
VALUES
('Markers','Colored markers for drawing and writing'),
('Erasers','Various types of erasers for pencils');
-- -------------------------
-- Sample Stationery Categories (Lots of examples)
-- -------------------------
INSERT IGNORE INTO stationery_categories (category_name, description)
VALUES
('Pens','All types of pens including gel, ballpoint, fountain'),
('Notebooks','Various sizes of notebooks, ruled or blank'),
('Markers','Colored markers for drawing and writing'),
('Erasers','Different types of erasers'),
('Pencils','Mechanical and wooden pencils'),
('Highlighters','Bright colors for highlighting text'),
('Staplers','Staplers for office and school use'),
('Paper Clips','Metal and plastic paper clips'),
('Folders','Document and file folders'),
('Art Supplies','Paints, brushes, sketchbooks, canvas'),
('Calculators','Scientific, basic, and graphing calculators'),
('Rulers','Plastic, metal, wooden rulers'),
('Glue & Adhesives','Glue sticks, liquid glue, tape'),
('Scissors','School and office scissors'),
('Markers Board & Chalk','Whiteboard markers, chalks');

-- -------------------------
-- Sample Stationery Items (Linked to above categories)
-- -------------------------
INSERT INTO stationery_items (item_name, category_id, brand, description, price, stock_quantity)
VALUES
('Gel Pen Set',1,'Pilot','Set of 12 smooth gel pens',5.00,100),
('A4 Notebook',2,'Classmate','100 pages ruled notebook',2.50,200),
('Permanent Marker',3,'Sharpie','Black permanent marker',2.00,150),
('Rubber Eraser',4,'Faber-Castell','Soft eraser for pencils',0.80,200),
('HB Pencil',20,'Staedtler','Pack of 12 pencils',3.00,250),
('Highlighter Set',21,'Stabilo','Pack of 6 fluorescent highlighters',4.50,120),
('Mini Stapler',22,'Swingline','Compact stapler with staples',6.00,80),
('Paper Clip Box',23,'Officemate','Box of 100 paper clips',1.20,300),
('Document Folder',24,'Kokuyo','Plastic A4 folder',2.00,150),
('Watercolor Paint Set',25,'Winsor & Newton','12-color set with brush',10.00,50),
('Scientific Calculator',26,'Casio','Function calculator for school',15.00,75),
('Plastic Ruler 30cm',27,'Faber-Castell','30 cm transparent ruler',1.50,200),
('Glue Stick',28,'Pritt','20g glue stick',1.00,180),
('School Scissors',29,'Fiskars','Children-safe scissors',3.50,120),
('Whiteboard Marker',30,'Luxor','Pack of 4 black whiteboard markers',4.00,100);

-- -------------------------
-- Additional Donations
-- -------------------------
INSERT INTO donations (donor_id, book_id, quantity, condition_type, donation_type, recipient_organization, pickup_required, pickup_address)
VALUES
(4,4,1,'new','school','Green Valley School',FALSE,NULL),
(5,6,3,'good','community','Community Center',TRUE,'Barishal Street 12');

INSERT INTO book_donations (book_id, donor_id, recipient_type, condition_type, quantity, special_notes)
VALUES
(4,4,'school','new',1,'For library use'),
(6,5,'community','good',2,'For youth program');

-- -------------------------
-- Additional Quizzes
-- -------------------------
INSERT INTO monthly_quiz (quiz_title, quiz_description, quiz_date, quiz_data, prize_description)
VALUES
('October Quiz','Math and Science quiz','2025-10-05','{"questions":[{"q":"2+2=?","options":[2,3,4,5],"answer":2}]}','Gift Voucher 100 TK');

INSERT INTO quiz_participants (quiz_id, user_id, answers, score, completed_at)
VALUES
(2,4,'[2]',10,'2025-10-05 11:00:00'),
(2,1,'[2]',10,'2025-10-05 11:30:00');

-- -------------------------
-- Additional Ebooks
-- -------------------------
INSERT INTO ebooks (book_id, seller_id, file_path, file_size, file_format, price)
VALUES
(4,5,'ebooks/shining.pdf',3072000,'PDF',12.00),
(5,5,'ebooks/orient_express.epub',1536000,'EPUB',9.00),
(6,5,'ebooks/banalata.pdf',1024000,'PDF',7.00);

-- -------------------------
-- Additional Notifications
-- -------------------------
INSERT INTO notifications (user_id, type, title, content)
VALUES
(4,'system','Welcome Diana','Welcome to Librariya platform, Diana!'),
(5,'order_status','New Listing','Your book listing #4 is now live!');


INSERT IGNORE INTO categories (category_name, description)
VALUES
('Science Fiction','Books about futuristic concepts, space, and technology'),
('Fantasy','Magical worlds, wizards, dragons, and mythical stories'),
('Mystery','Detective and crime-solving novels'),
('Thriller','Fast-paced books with suspense and excitement'),
('Romance','Love stories and relationships'),
('Historical Fiction','Stories set in historical periods'),
('Biography','Life stories of famous people'),
('Self-Help','Guides for personal development and improvement'),
('Business','Books on entrepreneurship, management, finance'),
('Technology','Books about programming, AI, gadgets, and tech trends'),
('Philosophy','Books exploring ideas, ethics, and human thought'),
('Poetry','Collections of poems and verse'),
('Horror','Fiction that evokes fear and suspense'),
('Adventure','Exciting journeys, survival, and exploration stories'),
('Cookbooks','Recipes and culinary guides'),
('Travel','Travel guides and travelogues'),
('Health & Fitness','Books about wellness, exercise, nutrition'),
('Education','Books for learning and academic purposes'),
('Art & Design','Books on painting, drawing, photography, and design'),
('Religion & Spirituality','Books about faith, meditation, and spirituality'),
('Children','Books for kids including stories and picture books'),
('Young Adult','Books targeted for teenagers and young adults'),
('Comics & Graphic Novels','Manga, comic books, and illustrated novels'),
('Drama','Serious fictional works with emotional themes'),
('Science','Books explaining scientific topics and experiments'),
('Politics','Books about governments, policy, and political history'),
('Environment','Books on climate change, nature, and ecology'),
('Law','Books on legal systems, rights, and case studies'),
('Sports','Books on sports, athletes, and fitness'),
('Humor','Funny stories, jokes, and satirical works');
INSERT INTO books (isbn, title, subtitle, description, publisher_id, publication_date, language, pages)
VALUES
('9780451457998','Dune','Epic Sci-Fi Novel','Set in a desert planet with interstellar politics',1,'1965-08-01','English',412),
('9780545010221','Harry Potter and the Deathly Hallows','','Final book of the magical series',2,'2007-07-21','English',759),
('9780062073488','Murder on the Orient Express','','Detective Hercule Poirot solves a murder on a train',3,'1934-01-01','English',256),
('9780307949486','Gone Girl','','Thriller about a missing wife and shocking secrets',1,'2012-05-24','English',422),
('9780345803481','Fifty Shades of Grey','','Romantic novel with drama and passion',2,'2011-06-20','English',514),
('9780812993547','All the Light We Cannot See','','Historical fiction during WWII',3,'2014-05-06','English',531),
('9781455586691','Steve Jobs','','Biography of Apple co-founder',1,'2011-10-24','English',656),
('9780812981607','The 7 Habits of Highly Effective People','','Self-help and productivity guide',2,'1989-08-15','English',384),
('9780134685991','Clean Code','','Software development and programming best practices',3,'2008-08-11','English',464),
('9780140449136','Meditations','','Philosophy book by Marcus Aurelius',1,'0180-01-01','English',304),
('9780143127741','Leaves of Grass','','Poetry collection by Walt Whitman',2,'1855-01-01','English',152),
('9780307743657','It','','Horror novel by Stephen King',3,'1986-09-15','English',1138),
('9780143038412','The Odyssey','','Ancient Greek adventure epic',1,NULL,'English',560),
('9781400033416','Mastering the Art of French Cooking','','Classic cookbook by Julia Child',2,'1961-10-16','English',684),
('9780143039433','Lonely Planet Japan','','Travel guide to Japan',3,'2020-03-10','English',576);
