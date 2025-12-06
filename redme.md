# 📚 LIBRARIYA - Simple Book Marketplace

A comprehensive web application for buying, selling, and renting books with additional stationery items, built with Flask and MySQL.

## 🚀 Features

- **User Management**: Registration, login, user dashboard
- **Book Management**: Add, browse, search, and filter books
- **Multiple Transaction Types**: Buy, sell, and rent books
- **Admin Panel**: Complete administrative interface
- **Reviews & Ratings**: User feedback system
- **Book Donations**: Charity and community support
- **Stationery Items**: School and office supplies
- **Monthly Quizzes**: Interactive book-related contests
- **Responsive Design**: Mobile-friendly interface

## 🛠 Tech Stack

- **Backend**: Python Flask
- **Database**: MySQL
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Authentication**: bcrypt password hashing
- **File Upload**: Werkzeug secure filename handling

## 📋 Prerequisites

Before you begin, ensure you have:

- Python 3.8 or higher
- MySQL 5.7 or higher
- pip (Python package installer)
- Git (optional, for cloning)

## ⚙️ Installation & Setup

### 1. Clone or Download the Project

```bash
git clone <repository-url>
cd librariya
```

Or download and extract the ZIP file.

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

1. **Create MySQL Database**:
   ```sql
   CREATE DATABASE librariya;
   ```

2. **Import Database Schema**:
   ```bash
   mysql -u root -p librariya < schema.sql
   ```

3. **Update Database Configuration**:
   - Copy `.env.example` to `.env`
   - Update database credentials in `.env` file:
   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=librariya
   ```

### 5. Configure Application

1. **Set up Environment Variables**:
   ```bash
   cp .env.example .env
   ```

2. **Update `.env` file** with your settings:
   ```env
   SECRET_KEY=your_secret_key_here
   DB_PASSWORD=your_mysql_password
   SITE_NAME=LIBRARIYA
   SITE_URL=http://localhost:8000
   ```

### 6. Create Upload Directory

```bash
mkdir -p assets/uploads
chmod 755 assets/uploads
```

## 🏃‍♂️ Running the Application

### Development Mode

```bash
python app.py
```

### Production Mode

```bash
python run.py
```

The application will be available at: `http://localhost:8000`

## 👤 Default Admin Account

- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@librariya.com`

⚠️ **Important**: Change the default admin password after first login!

## 📁 Project Structure

```
librariya/
├── 📄 app.py                 # Main Flask application
├── 📄 run.py                 # Production runner
├── 📄 requirements.txt       # Python dependencies
├── 📄 .env.example          # Environment variables template
├── 📄 schema.sql            # Database schema
├── 📄 README.md             # This file
├── 📁 templates/            # HTML templates
│   ├── 📄 index.html        # Homepage
│   ├── 📄 book_details.html # Book details page
│   ├── 📄 add_book.html     # Add book form
│   ├── 📁 auth/             # Authentication pages
│   ├── 📁 user/             # User dashboard pages
│   └── 📁 admin/            # Admin panel pages
├── 📁 static/               # Static files
│   ├── 📁 css/
│   │   └── 📄 style.css     # Main stylesheet
│   ├── 📁 js/
│   │   └── 📄 main.js       # Main JavaScript
│   └── 📁 images/           # Static images
└── 📁 assets/
    └── 📁 uploads/          # User uploaded files
```

## 🔧 Configuration Options

### Database Settings
- `DB_HOST`: MySQL server host
- `DB_USER`: MySQL username
- `DB_PASSWORD`: MySQL password
- `DB_NAME`: Database name

### Application Settings
- `FLASK_ENV`: Environment (development/production)
- `SECRET_KEY`: Flask secret key for sessions
- `DEBUG_MODE`: Enable/disable debug mode

### Upload Settings
- `UPLOAD_FOLDER`: Directory for uploaded files
- `MAX_FILE_SIZE`: Maximum file size (default: 5MB)
- `ALLOWED_EXTENSIONS`: Allowed file extensions

## 🎯 Core Features Usage

### For Users
1. **Registration**: Create account with username, email, password
2. **Browse Books**: Search and filter books by category, price, condition
3. **Add Books**: List books for sale or rent
4. **View Details**: See complete book information and reviews
5. **Dashboard**: Manage your books, orders, and profile

### For Admins
1. **Admin Panel**: Access via `/admin/dashboard`
2. **Manage Books**: Add, edit, delete book listings
3. **User Management**: View and manage user accounts
4. **Orders**: Track and manage all transactions
5. **Donations**: Handle book donation requests
6. **Stationery**: Manage stationery inventory

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Verify MySQL is running
   - Check database credentials in `.env`
   - Ensure database exists

2. **Import Error**:
   - Activate virtual environment
   - Install requirements: `pip install -r requirements.txt`

3. **Upload Issues**:
   - Check `assets/uploads` directory exists
   - Verify directory permissions (755)

4. **Static Files Not Loading**:
   - Ensure `static/` directory structure is correct
   - Check file paths in templates

### Debug Mode

Enable debug mode for development:
```python
# In app.py
app.run(debug=True, host='0.0.0.0', port=8000)
```

## 🔒 Security Considerations

- Change default admin credentials
- Use strong secret key in production
- Enable HTTPS in production
- Regular database backups
- Keep dependencies updated

## 📝 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/logout` - User logout

### Books
- `GET /` - Homepage with featured books
- `GET /books/browse` - Browse all books
- `GET /books/details/<id>` - Book details
- `POST /books/add` - Add new book (authenticated)

### User Dashboard
- `GET /user/dashboard` - User dashboard
- `GET /admin/dashboard` - Admin dashboard (admin only)

## 🤝 Contributing

1. Fork the project
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push branch: `git push origin feature/new-feature`
5. Submit pull request

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue in the repository
- Email: admin@librariya.com

---

**Made with ❤️ for the book-loving community**