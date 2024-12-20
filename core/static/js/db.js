// static/js/db.js
const dbName = 'ShopRepDB';
const dbVersion = 1;

const initDB = () => {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(dbName, dbVersion);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            
            // Create object stores
            if (!db.objectStoreNames.contains('reports')) {
                const reportStore = db.createObjectStore('reports', { keyPath: 'id' });
                reportStore.createIndex('status', 'status');
                reportStore.createIndex('created_at', 'created_at');
            }
            
            if (!db.objectStoreNames.contains('shops')) {
                db.createObjectStore('shops', { keyPath: 'id' });
            }
            
            if (!db.objectStoreNames.contains('products')) {
                db.createObjectStore('products', { keyPath: 'id' });
            }
        };
    });
};
