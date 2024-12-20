// static/js/sync.js
const syncData = async () => {
    if (!navigator.onLine) {
        return;
    }
    
    const db = await initDB();
    const transaction = db.transaction(['reports'], 'readwrite');
    const store = transaction.objectStore('reports');
    
    // Get all unsychronized reports
    const reports = await store.index('status').getAll('draft');
    
    for (const report of reports) {
        try {
            const response = await fetch('/api/reports/sync/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(report)
            });
            
            if (response.ok) {
                // Remove synchronized report from IndexedDB
                await store.delete(report.id);
            }
        } catch (error) {
            console.error('Error syncing report:', error);
        }
    }
};

// Add event listeners for online/offline status
window.addEventListener('online', syncData);
window.addEventListener('offline', () => {
    console.log('Application is offline');
});