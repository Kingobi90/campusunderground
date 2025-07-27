// Common functionality for all pages
document.addEventListener('DOMContentLoaded', function() {
    // Initialize navigation
    initNavigation();
    
    // Initialize any interactive elements
    initInteractiveElements();
});

// Initialize navigation elements
function initNavigation() {
    // Add click event to the home icon (first nav item after logo)
    const navItems = document.querySelectorAll('.nav-item');
    
    // Home icon (first nav item)
    if (navItems[0]) {
        navItems[0].addEventListener('click', function() {
            window.location.href = '../index.html';
        });
    }
    
    // Second nav item - Study Tools
    if (navItems[1]) {
        navItems[1].addEventListener('click', function() {
            window.location.href = 'main page.html';
        });
    }
    
    // Third nav item - Refresh current page
    if (navItems[2]) {
        navItems[2].addEventListener('click', function() {
            window.location.reload();
        });
    }
    
    // Add back button functionality if it exists
    const backButtons = document.querySelectorAll('.back-button');
    backButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = 'main page.html';
        });
    });
}

// Initialize interactive elements that might be common across pages
function initInteractiveElements() {
    // Add hover effects to cards
    const cards = document.querySelectorAll('.tool-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 30px rgba(255, 255, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
}

// Function to show loading state
function showLoading(message = 'Loading...') {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        const loadingMessage = loadingOverlay.querySelector('p');
        if (loadingMessage) {
            loadingMessage.textContent = message;
        }
        loadingOverlay.style.display = 'flex';
    }
}

// Function to hide loading state
function hideLoading() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
}

// Function to show error messages
function showError(message) {
    const errorMessage = document.getElementById('error-message');
    if (errorMessage) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 5000);
    }
}

// Function to format time (for timers, etc.)
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
}
