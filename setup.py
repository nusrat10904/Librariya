#!/usr/bin/env python3
"""
LIBRARIYA - Automated Setup Script
This script helps set up the complete project
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*50)
    print(f" {text}")
    print("="*50)

def print_step(text):
    """Print formatted step"""
    print(f"\n→ {text}")

def print_success(text):
    """Print success message"""
    print(f"✓ {text}")

def print_error(text):
    """Print error message"""
    print(f"✗ {text}")

def check_requirements():
    """Check if Python and pip are available"""
    print_header("CHECKING REQUIREMENTS")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print_error(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}")
        return False
    
    print_success(f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check pip
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print_success("pip is available")
        return True
    except subprocess.CalledProcessError:
        print_error("pip is not available")
        return False

def create_directories():
    """Create necessary directories"""
    print_header("CREATING DIRECTORIES")
    
    directories = [
        "static/css",
        "static/js",
        "static/images",
        "assets/uploads",
        "templates/auth",
        "templates/user", 
        "templates/admin",
        "templates/books",
        "templates/errors"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print_success(f"Created {directory}")
    
    # Set upload directory permissions
    try:
        os.chmod("assets/uploads", 0o755)
        print_success("Set upload directory permissions")
    except OSError:
        print_error("Could not set upload directory permissions")

def create_env_file():
    """Create .env file if it doesn't exist"""
    print_header("ENVIRONMENT SETUP")
    
    if Path(".env").exists():
        print_success(".env file already exists")
        return
    
    if Path(".env.example").exists():
        shutil.copy(".env.example", ".env")
        print_success("Created .env from .env.example")
        print("Please edit .env file with your database credentials")
    else:
        # Create basic .env file
        env_content = """# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=librariya
DB_PORT=3306

# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key_here

# Site Configuration
SITE_NAME=LIBRARIYA
SITE_DESCRIPTION=Simple Book Marketplace
SITE_URL=http://localhost:8000
"""
        with open(".env", "w") as f:
            f.write(env_content)
        print_success("Created basic .env file")

def install_dependencies():
    """Install Python dependencies"""
    print_header("INSTALLING DEPENDENCIES")
    
    if not Path("requirements.txt").exists():
        print_error("requirements.txt not found")
        return False
    
    try:
        print_step("Installing Python packages...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                      check=True)
        print_success("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to install dependencies")
        return False

def check_database():
    """Check database connectivity"""
    print_header("DATABASE CHECK")
    
    try:
        import mysql.connector
        from dotenv import load_dotenv
        
        load_dotenv()
        
        config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'port': int(os.getenv('DB_PORT', 3306))
        }
        
        # Test connection
        conn = mysql.connector.connect(**config)
        conn.close()
        print_success("Database connection successful")
        
        # Check if database exists
        config['database'] = os.getenv('DB_NAME', 'librariya')
        try:
            conn = mysql.connector.connect(**config)
            conn.close()
            print_success("Database exists and accessible")
            return True
        except mysql.connector.Error:
            print_error(f"Database '{config['database']}' not found")
            print("Please create the database first:")
            print(f"CREATE DATABASE {config['database']};")
            return False
            
    except ImportError:
        print_error("mysql-connector-python not installed")
        return False
    except mysql.connector.Error as e:
        print_error(f"Database connection failed: {e}")
        return False

def create_sample_files():
    """Create sample configuration files"""
    print_header("CREATING SAMPLE FILES")
    
    # Create .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Flask
instance/
.webassets-cache

# Database
*.db
*.sqlite3

# Environment variables
.env

# Uploads
assets/uploads/*
!assets/uploads/.gitkeep

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    print_success("Created .gitignore")
    
    # Create upload directory placeholder
    with open("assets/uploads/.gitkeep", "w") as f:
        f.write("")
    print_success("Created upload directory placeholder")

def run_tests():
    """Run basic application tests"""
    print_header("RUNNING TESTS")
    
    try:
        # Test import
        print_step("Testing application import...")
        sys.path.insert(0, os.getcwd())
        import app
        print_success("Application imports successfully")
        
        # Test database initialization
        if hasattr(app, 'init_database'):
            print_step("Testing database initialization...")
            if app.init_database():
                print_success("Database initialization successful")
            else:
                print_error("Database initialization failed")
        
        return True
    except Exception as e:
        print_error(f"Tests failed: {e}")
        return False

def main():
    """Main setup function"""
    print_header("LIBRARIYA PROJECT SETUP")
    print("This script will help you set up the LIBRARIYA project")
    
    # Check requirements
    if not check_requirements():
        print_error("Requirements check failed")
        return False
    
    # Create directories
    create_directories()
    
    # Create environment file
    create_env_file()
    
    # Install dependencies
    if not install_dependencies():
        print_error("Dependency installation failed")
        return False
    
    # Check database
    db_ok = check_database()
    
    # Create sample files
    create_sample_files()
    
    # Run tests
    test_ok = run_tests()
    
    # Final summary
    print_header("SETUP COMPLETE")
    
    if db_ok and test_ok:
        print_success("All checks passed!")
        print("\nNext steps:")
        print("1. Edit .env file with your database credentials")
        print("2. Import database schema: mysql -u root -p librariya < schema.sql")
        print("3. Run the application: python app.py")
        print("4. Open http://localhost:8000 in your browser")
        print("5. Login with admin/admin123 and change the password")
    else:
        print_error("Setup completed with issues")
        if not db_ok:
            print("- Fix database connection")
        if not test_ok:
            print("- Check application configuration")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nSetup failed with error: {e}")
        sys.exit(1)