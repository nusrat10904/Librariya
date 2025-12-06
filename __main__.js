// LIBRARIYA - Main JavaScript File
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    initializeBootstrapComponents();
    initializeSearch();
    initializeFormValidations();
    initializeImageHandling();
    initializeCartFunctionality();
    initializeFilters();
    initializeAnimations();
    initializeBookCards();
}

// Bootstrap Components
function initializeBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));

    // Auto-dismiss alerts
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert-dismissible:not(.alert-permanent)');
        alerts.forEach(alert => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        });
    }, 5000);
}

// Search Functionality
function initializeSearch() {
    const searchInputs = document.querySelectorAll('input[name="search"]');
    
    searchInputs.forEach(input => {
        // Real-time search suggestions (if needed)
        input.addEventListener('input', debounce(function() {
            if (this.value.length >= 3) {
                // Implement search suggestions here if needed
                console.log('Searching for:', this.value);
            }
        }, 300));
    });

    // Search form submission
    const searchForms = document.querySelectorAll('form[action*="browse"]');
    searchForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const searchInput = this.querySelector('input[name="search"]');
            if (searchInput && searchInput.value.trim() === '') {
                e.preventDefault();
                showAlert('Please enter a search term', 'warning');
            }
        });
    });
}

// Form Validations
function initializeFormValidations() {
    // Registration form validation
    const registerForm = document.querySelector('form[method="POST"]');
    if (registerForm && window.location.pathname.includes('register')) {
        registerForm.addEventListener('submit', validateRegistrationForm);
        
        // Password confirmation validation
        const confirmPassword = document.getElementById('confirm_password');
        if (confirmPassword) {
            confirmPassword.addEventListener('input', validatePasswordMatch);
        }
    }

    // Login form validation
    const loginForm = document.querySelector('form[method="POST"]');
    if (loginForm && window.location.pathname.includes('login')) {
        loginForm.addEventListener('submit', validateLoginForm);
    }

    // Generic form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

function validateRegistrationForm(e) {
    const form = e.target;
    const password = form.querySelector('#password');
    const confirmPassword = form.querySelector('#confirm_password');
    const username = form.querySelector('#username');
    const email = form.querySelector('#email');

    let isValid = true;

    // Username validation
    if (username && username.value.length < 3) {
        showFieldError(username, 'Username must be at least 3 characters long');
        isValid = false;
    }

    // Email validation
    if (email && !isValidEmail(email.value)) {
        showFieldError(email, 'Please enter a valid email address');
        isValid = false;
    }

    // Password validation
    if (password && password.value.length < 6) {
        showFieldError(password, 'Password must be at least 6 characters long');
        isValid = false;
    }

    // Password match validation
    if (password && confirmPassword && password.value !== confirmPassword.value) {
        showFieldError(confirmPassword, 'Passwords do not match');
        isValid = false;
    }

    if (!isValid) {
        e.preventDefault();
        showAlert('Please fix the errors above', 'danger');
    }
}

function validatePasswordMatch() {
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password');
    
    if (password && confirmPassword) {
        if (password.value !== confirmPassword.value) {
            confirmPassword.setCustomValidity("Passwords don't match");
            showFieldError(confirmPassword, "Passwords don't match");
        } else {
            confirmPassword.setCustomValidity('');
            clearFieldError(confirmPassword);
        }
    }
}

function validateLoginForm(e) {
    const form = e.target;
    const username = form.querySelector('#username');
    const password = form.querySelector('#password');
    
    let isValid = true;

    if (!username || username.value.trim() === '') {
        showFieldError(username, 'Username or email is required');
        isValid = false;
    }

    if (!password || password.value.trim() === '') {
        showFieldError(password, 'Password is required');
        isValid = false;
    }

    if (!isValid) {
        e.preventDefault();
        showAlert('Please fill in all required fields', 'danger');
    }
}

// Image Handling
function initializeImageHandling() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    
    imageInputs.forEach(input => {
        input.addEventListener('change', function() {
            handleImagePreview(this);
        });
    });
}

function handleImagePreview(input) {
    if (input.files && input.files[0]) {
        const file = input.files[0];
        
        // Validate file size (5MB max)
        if (file.size > 5 * 1024 * 1024) {
            showAlert('Image size must be less than 5MB', 'danger');
            input.value = '';
            return;
        }

        // Validate file type
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
        if (!allowedTypes.includes(file.type)) {
            showAlert('Please upload a valid image file (JPG, PNG, GIF, WebP)', 'danger');
            input.value = '';
            return;
        }

        // Create preview
        const reader = new FileReader();
        reader.onload = function(e) {
            let preview = document.querySelector('#image-preview');
            if (!preview) {
                preview = document.createElement('img');
                preview.id = 'image-preview';
                preview.className = 'img-thumbnail mt-2';
                preview.style.maxWidth = '200px';
                preview.style.maxHeight = '200px';
                input.parentNode.appendChild(preview);
            }
            preview.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
}

// Cart Functionality
function initializeCartFunctionality() {
    const cartButtons = document.querySelectorAll('.btn-add-to-cart');
    const cartCount = document.querySelector('#cart-count');
    
    cartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const bookId = this.dataset.bookId;
            const bookTitle = this.dataset.bookTitle;
            addToCart(bookId, bookTitle);
        });
    });
}

function addToCart(bookId, bookTitle) {
    // Get current cart from storage (using variables since localStorage isn't available)
    let cart = window.cartItems || [];
    
    // Check if item already in cart
    const existingItem = cart.find(item => item.id === bookId);
    
    if (existingItem) {
        existingItem.quantity += 1;
        showAlert(`Increased quantity of "${bookTitle}" in cart`, 'success');
    } else {
        cart.push({
            id: bookId,
            title: bookTitle,
            quantity: 1,
            addedAt: new Date().toISOString()
        });
        showAlert(`"${bookTitle}" added to cart`, 'success');
    }
    
    // Save cart
    window.cartItems = cart;
    updateCartCount();
}

function updateCartCount() {
    const cartCount = document.querySelector('#cart-count');
    const cart = window.cartItems || [];
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    
    if (cartCount) {
        cartCount.textContent = totalItems;
        cartCount.style.display = totalItems > 0 ? 'inline' : 'none';
    }
}

// Filter Functionality
function initializeFilters() {
    const filterForm = document.querySelector('.card form');
    const sortSelect = document.querySelector('select[onchange]');
    
    if (filterForm) {
        const inputs = filterForm.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('change', debounce(function() {
                // Auto-submit form when filters change
                if (this.type !== 'submit') {
                    // Could auto-submit here if desired
                    console.log('Filter changed:', this.name, this.value);
                }
            }, 500));
        });
    }

    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const url = new URL(window.location);
            url.searchParams.set('sort', this.value);
            window.location.href = url.toString();
        });
    }
}

// Animations
function initializeAnimations() {
    // Fade in elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);

    // Observe elements that should animate
    const animateElements = document.querySelectorAll('.book-card, .category-card, .card');
    animateElements.forEach(el => {
        observer.observe(el);
    });
}

// Book Cards
function initializeBookCards() {
    const bookCards = document.querySelectorAll('.book-card');
    
    bookCards.forEach(card => {
        // Add hover effects
        card.addEventListener('mouseenter', function() {
            this.classList.add('hover-lift');
        });
        
        card.addEventListener('mouseleave', function() {
            this.classList.remove('hover-lift');
        });
        
        // Handle view button clicks
        const viewBtn = card.querySelector('.btn-primary');
        if (viewBtn && !viewBtn.href) {
            viewBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const bookId = this.dataset.bookId || '1';
                window.location.href = `/books/details/${bookId}`;
            });
        }
    });
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.alert-container') || document.body;
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.insertBefore(alert, alertContainer.firstChild);
    
    setTimeout(() => {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        if (bsAlert) bsAlert.close();
    }, 5000);
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('is-invalid');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Price formatting
function formatPrice(amount, currency = 'BDT') {
    if (typeof amount !== 'number') {
        amount = parseFloat(amount) || 0;
    }
    return `৳${amount.toLocaleString('en-BD', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

// Loading states
function showLoading(element) {
    const originalHTML = element.innerHTML;
    element.dataset.originalHtml = originalHTML;
    element.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    element.disabled = true;
}

function hideLoading(element) {
    if (element.dataset.originalHtml) {
        element.innerHTML = element.dataset.originalHtml;
        delete element.dataset.originalHtml;
    }
    element.disabled = false;
}

// Initialize cart count on page load
document.addEventListener('DOMContentLoaded', function() {
    updateCartCount();
});

// Export functions for global use
window.LibrariyaApp = {
    showAlert,
    formatPrice,
    addToCart,
    showLoading,
    hideLoading
};