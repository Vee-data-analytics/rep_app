// Dynamic Form Behavior
document.addEventListener('DOMContentLoaded', function() {
    // Progressive disclosure for top-up fields
    const needsTopupCheckbox = document.querySelector('input[name="needs_topup"]');
    const topupSection = document.getElementById('topup-fields');

    if (needsTopupCheckbox && topupSection) {
        // Initial state
        topupSection.style.display = needsTopupCheckbox.checked ? 'block' : 'none';

        // Toggle visibility based on checkbox
        needsTopupCheckbox.addEventListener('change', function() {
            topupSection.style.display = this.checked ? 'block' : 'none';
        });
    }

    // Form validation enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            let isValid = true;
            const requiredFields = form.querySelectorAll('[required]');

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });

            // Specific validations
            const desiredQuantityField = form.querySelector('input[name="desired_quantity"]');
            const currentQuantityField = form.querySelector('input[name="shop_current_quantity"]');
            const needsTopupCheckbox = form.querySelector('input[name="needs_topup"]');

            if (needsTopupCheckbox && needsTopupCheckbox.checked && desiredQuantityField) {
                const currentQuantity = parseInt(currentQuantityField.value);
                const desiredQuantity = parseInt(desiredQuantityField.value);

                if (desiredQuantity <= currentQuantity) {
                    desiredQuantityField.classList.add('is-invalid');
                    isValid = false;
                }
            }

            if (!isValid) {
                event.preventDefault();
                // Optional: Show a global error message
                const errorSummary = document.createElement('div');
                errorSummary.classList.add('alert', 'alert-danger');
                errorSummary.textContent = 'Please correct the highlighted fields before submitting.';
                form.insertBefore(errorSummary, form.firstChild);
            }
        });
    });

    // Live search and autocomplete for select fields
    const selectFields = document.querySelectorAll('select[data-live-search="true"]');
    selectFields.forEach(select => {
        // Assuming you're using Bootstrap Select or a similar library
        $(select).selectpicker({
            liveSearch: true,
            style: 'btn-outline-primary',
            size: 4
        });
    });
});