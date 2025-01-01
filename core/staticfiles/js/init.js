import { handleModalFormSubmit } from './modal-handler.js';

document.addEventListener('DOMContentLoaded', () => {
    // Initialize all your modal forms here
    handleModalFormSubmit('shopForm', 'addShopModal');
    
    // If you have other modals, you can initialize them here too
    // handleModalFormSubmit('productForm', 'addProductModal');
    // handleModalFormSubmit('customerForm', 'addCustomerModal');
});