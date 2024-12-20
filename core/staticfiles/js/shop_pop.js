document.addEventListener('DOMContentLoaded', function() {
    // Target the shop select element
    const shopSelect = document.getElementById('id_shop');
    
    if (shopSelect) {
        // Add change event listener
        shopSelect.addEventListener('change', function() {
            const shopId = this.value;
            if (shopId) {
                fetchShopDetails(shopId);
            } else {
                clearShopDetails();
            }
        });

        // If there's an initial value, fetch its details
        if (shopSelect.value) {
            fetchShopDetails(shopSelect.value);
        }
    }

    function fetchShopDetails(shopId) {
        // Show loading indicator if you want
        fetch(`/api/get-shop-details/?shop_id=${shopId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Populate the fields
                document.getElementById('shopAddress').value = data.address || '';
                document.getElementById('shopManagerName').value = data.manager_name || '';
                document.getElementById('shopPhone').value = data.manager_phone || '';
            })
            .catch(error => {
                console.error('Error fetching shop details:', error);
                clearShopDetails();
                // Optionally show an error message to the user
                alert('Error fetching shop details. Please try again.');
            });
    }

    function clearShopDetails() {
        document.getElementById('shopAddress').value = '';
        document.getElementById('shopManagerName').value = '';
        document.getElementById('shopPhone').value = '';
    }
});