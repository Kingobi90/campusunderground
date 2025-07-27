// Redirect.js - Handles redirections between study tool pages

document.addEventListener('DOMContentLoaded', function() {
    // Get the current page filename
    const currentPage = window.location.pathname.split('/').pop();
    
    // Set up tool card redirections on the main page
    setupToolCardRedirects();
    
    // Set active state for the current navigation item
    highlightCurrentNavItem(currentPage);
});

// Function to set up the tool card redirects on the main page
function setupToolCardRedirects() {
    // Only run this on the main page
    if (window.location.pathname.includes('main page.html') || window.location.pathname.includes('study-tools.html')) {
        // Find all tool cards and add click events
        const toolCards = document.querySelectorAll('.tool-card');
        
        toolCards.forEach(card => {
            const toolTitle = card.querySelector('.tool-title')?.textContent.trim();
            const button = card.querySelector('.tool-button');
            
            if (button) {
                button.addEventListener('click', function(e) {
                    e.stopPropagation(); // Prevent the card click from also triggering
                    redirectToTool(toolTitle);
                });
            }
            
            // Make the entire card clickable
            card.addEventListener('click', function() {
                redirectToTool(toolTitle);
            });
        });
    }
}

// Function to redirect to the appropriate tool page based on the tool title
function redirectToTool(toolTitle) {
    if (!toolTitle) return;
    
    switch(toolTitle) {
        case 'Flashcards':
            window.location.href = 'flashcards.html';
            break;
        case 'Pomodoro Timer':
            window.location.href = 'pomodoro_timer_component.html';
            break;
        case 'Smart Notes':
            window.location.href = 'smart notes.html';
            break;
        case 'Moodle Integration':
            window.location.href = 'moodle_integration_ui.html';
            break;
        case 'Study Groups':
            showComingSoonMessage('Study Groups feature');
            break;
        case 'Practice Quizzes':
            showComingSoonMessage('Practice Quizzes feature');
            break;
        default:
            showComingSoonMessage('This tool');
            break;
    }
}

// Function to highlight the current navigation item
function highlightCurrentNavItem(currentPage) {
    const navItems = document.querySelectorAll('.nav-item');
    
    // Remove active class from all nav items
    navItems.forEach(item => {
        item.classList.remove('active');
    });
    
    // Set active class based on current page
    if ((currentPage.includes('main page.html') || currentPage.includes('study-tools.html')) && navItems[1]) {
        navItems[1].classList.add('active');
    } else if (currentPage.includes('index.html') && navItems[0]) {
        navItems[0].classList.add('active');
    }
}

// Function to show a coming soon message for features not yet implemented
function showComingSoonMessage(featureName) {
    alert(`${featureName} is coming soon! Check back later for updates.`);
}
