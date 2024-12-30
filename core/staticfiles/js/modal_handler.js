// Function to handle modal form submissions
function handleModalFormSubmit(formId, submitUrl, modalId) {
    const form = document.getElementById(formId);
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        
        fetch(submitUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update the corresponding dropdown
                const dropdown = document.getElementById(data.dropdown_id);
                const newOption = new Option(data.new_option.text, data.new_option.value, true, true);
                dropdown.add(newOption);
                
                // Show success message
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-success alert-dismissible fade show';
                alertDiv.innerHTML = `
                    ${data.message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                `;
                document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.card'));
                
                // Close the modal
                const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
                modal.hide();
                
                // Reset the form
                form.reset();
            } else {
                // Handle validation errors
                Object.keys(data.errors).forEach(field => {
                    const inputField = form.querySelector(`[name=${field}]`);
                    if (inputField) {
                        inputField.classList.add('is-invalid');
                        const feedbackDiv = document.createElement('div');
                        feedbackDiv.className = 'invalid-feedback';
                        feedbackDiv.textContent = data.errors[field].join(' ');
                        inputField.parentNode.appendChild(feedbackDiv);
                    }
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-danger';
            alertDiv.textContent = 'An error occurred. Please try again.';
            form.prepend(alertDiv);
        });
    });
}

// Initialize form handlers for each modal
document.addEventListener('DOMContentLoaded', function() {
    const modalConfigs = [
        {
            formId: 'shopForm',
            submitUrl: '/create-shop/',
            modalId: 'addShopModal'
        },
        {
            formId: 'productForm',
            submitUrl: '/create-product/',
            modalId: 'addProductModal'
        },
        {
            formId: 'storeForm',
            submitUrl: '/create-store/',
            modalId: 'newStoreModal'
        },
        {
            formId: 'mainStoreForm',
            submitUrl: '/create-main-store/',
            modalId: 'addMainStoreModal'
        }
    ];
    
    modalConfigs.forEach(config => {
        handleModalFormSubmit(config.formId, config.submitUrl, config.modalId);
    });
});