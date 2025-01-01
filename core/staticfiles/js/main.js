if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/service-worker.js', {
            scope: '/'
        })
        .then(function(registration) {
            console.log('ServiceWorker registration successful with scope: ', registration.scope);
        })
        .catch(function(err) {
            console.log('ServiceWorker registration failed: ', err);
        });
    });
}
// App Install Prompt
let deferredPrompt;
const addBtn = document.querySelector('.add-button');
if (addBtn) addBtn.style.display = 'none';

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    if (addBtn) addBtn.style.display = 'block';

    addBtn.addEventListener('click', async () => {
        if (addBtn) addBtn.style.display = 'none';
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        console.log(`User response to install prompt: ${outcome}`);
        deferredPrompt = null;
    });
});

// Offline Status Detection
window.addEventListener('online', function() {
    document.body.classList.remove('offline');
    showNotification('You are back online!', 'success');
});

window.addEventListener('offline', function() {
    document.body.classList.add('offline');
    showNotification('You are offline. Some features may be limited.', 'warning');
});

// Utility Functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Form Handling
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            if (!navigator.onLine) {
                e.preventDefault();
                showNotification('Cannot submit form while offline', 'error');
                return;
            }
            
            // Add loading state if needed
            const submitButton = form.querySelector('[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = 'Processing...';
            }
        });
    });
});

// Data Sync for Offline Mode
class DataSync {
    static async syncOfflineData() {
        if (!navigator.onLine) return;
        
        try {
            const offlineData = JSON.parse(localStorage.getItem('offlineData') || '[]');
            
            for (const item of offlineData) {
                await fetch(item.url, {
                    method: item.method,
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify(item.data)
                });
            }
            
            localStorage.removeItem('offlineData');
            showNotification('Offline data synchronized successfully', 'success');
        } catch (error) {
            console.error('Error syncing offline data:', error);
            showNotification('Error syncing offline data', 'error');
        }
    }
    
    static getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }
    
    static saveForOffline(url, method, data) {
        const offlineData = JSON.parse(localStorage.getItem('offlineData') || '[]');
        offlineData.push({ url, method, data });
        localStorage.setItem('offlineData', JSON.stringify(offlineData));
        showNotification('Data saved for offline sync', 'info');
    }
}

// Automatic Data Sync When Coming Online
window.addEventListener('online', () => {
    DataSync.syncOfflineData();
});

// Dynamic Image Loading with Fallback
function loadImage(img) {
    const src = img.dataset.src;
    if (!src) return;
    
    img.src = src;
    img.removeAttribute('data-src');
}

// Lazy Loading Images
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                loadImage(entry.target);
                observer.unobserve(entry.target);
            }
        });
    });

    document.querySelectorAll('img[data-src]').forEach(img => imageObserver.observe(img));
}

// Error Handling
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    showNotification('An error occurred', 'error');
});

// Cache Management
async function clearAppCache() {
    try {
        const cacheNames = await caches.keys();
        await Promise.all(
            cacheNames.map(cacheName => {
                if (cacheName.startsWith('shop-rep-')) {
                    return caches.delete(cacheName);
                }
            })
        );
        showNotification('Cache cleared successfully', 'success');
    } catch (error) {
        console.error('Error clearing cache:', error);
        showNotification('Error clearing cache', 'error');
    }
}