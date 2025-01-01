$(document).ready(function() {
    // Function to handle modal form submissions
    function handleModalForm(formId, formKey) {
        $(`#${formId}`).submit(function(e) {
            e.preventDefault();
            let $form = $(this);
            $.ajax({
                type: "POST",
                url: "{% url 'reptrack_trace:report-create' %}",
                data: {
                    form_key: formKey,
                    ...$form.serialize()
                },
                dataType: "json",
                headers: {'X-Requested-With': 'XMLHttpRequest'},
                success: function(response) {
                    if (response.success) {
                        let dropdownId = response.dropdown_data.dropdown_id;
                        let newOption = response.dropdown_data.new_option;
                        let $dropdown = $("#" + dropdownId);
                        $dropdown.append($("<option>", {value: newOption.value, text: newOption.text}));
                        $dropdown.val(newOption.value);
                        $form.closest('.modal').modal('hide');
                        $form[0].reset(); // Clear the form
                        $form.find(".alert-danger").hide(); //hide errors
                    } else {
                        let errorHtml = "<ul>";
                        for (const [key, errors] of Object.entries(response.errors)) {
                            errorHtml += `<li><strong>${key}:</strong><ul>`;
                            for (const error of errors) {
                                errorHtml += `<li>${error}</li>`;
                            }
                            errorHtml += `</ul></li>`;
                        }
                        errorHtml += "</ul>";
                        $form.find(".alert-danger").html(errorHtml).show();
                    }
                },
                error: function(xhr, textStatus, errorThrown) {
                    console.error("AJAX Error:", textStatus, errorThrown);
                    $form.find(".alert-danger").html("<p>An error occurred. Please try again later.</p>").show();
                }
            });
        });
    }

    // Initialize handlers for each modal form
    handleModalForm("shopForm", "shop_form");
    handleModalForm("storeForm", "store_form");
    handleModalForm("mainStoreForm", "main_store_form");
    handleModalForm("shopStoreForm", "shop_store_form");
    handleModalForm("productForm", "product_form");
});
