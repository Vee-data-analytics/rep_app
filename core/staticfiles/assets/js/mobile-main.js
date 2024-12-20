// Theme switching functionality
document.addEventListener('DOMContentLoaded', function() {
    const themeSwitch = document.getElementById('themeSwitch');
    const html = document.documentElement;
    const body = document.body;
    const header = document.querySelector('header');
    const main = document.querySelector('main');
    
    // Check for saved theme preference or default to light
    const savedTheme = localStorage.getItem('theme') || 'light';
    
    // Apply theme to all elements
    function applyTheme(theme) {
        html.setAttribute('data-bs-theme', theme);
        body.setAttribute('data-bs-theme', theme);
        header.setAttribute('data-bs-theme', theme);
        main.setAttribute('data-bs-theme', theme);
    }
    
    // Initial theme application
    applyTheme(savedTheme);
    themeSwitch.checked = savedTheme === 'dark';
    
    // Theme switch event listener
    themeSwitch.addEventListener('change', function() {
        const theme = this.checked ? 'dark' : 'light';
        applyTheme(theme);
        localStorage.setItem('theme', theme);
    });
});

// Date/Time update functionality
function updateDateTime() {
    const now = new Date();
    document.getElementById('currentTime').textContent = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
    document.getElementById('currentDate').textContent = now.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

updateDateTime();
setInterval(updateDateTime, 60000);