// Components.js - Utility functions for loading components

// Function to load HTML components into the page
async function loadComponent(elementId, componentPath) {
    try {
        const response = await fetch(componentPath);
        if (!response.ok) {
            throw new Error(`Failed to load component: ${response.status}`);
        }
        const html = await response.text();
        document.getElementById(elementId).innerHTML = html;
    } catch (error) {
        console.error('Error loading component:', error);
    }
}

// Function to include the loading overlay and error message components
function includeCommonComponents() {
    // Create a container for the components if it doesn't exist
    let componentsContainer = document.getElementById('components-container');
    if (!componentsContainer) {
        componentsContainer = document.createElement('div');
        componentsContainer.id = 'components-container';
        document.body.appendChild(componentsContainer);
    }
    
    // Load the loading overlay component
    fetch('components/loading-overlay.html')
        .then(response => response.text())
        .then(html => {
            componentsContainer.innerHTML = html;
        })
        .catch(error => {
            console.error('Error loading components:', error);
        });
}

// Initialize components when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    includeCommonComponents();
});
