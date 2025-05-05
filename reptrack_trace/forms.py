from django import forms
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Row, Column, Submit, HTML, Field
from django.utils.translation import gettext_lazy as _
from .models import Report, Shop, Product, User
from django.core.exceptions import ValidationError
from django.db.models import Q
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, HTML



class ShopForm(forms.ModelForm):
    """Form for creating/editing shops"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes and other attributes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'id': f'id_shop_{field_name}',
                'name': field_name
            })
    class Meta:
        model = Shop
        fields = [
            'name',
            'address',
            'manager_name',
            'manager_phone',
            'manager_email',
            'store_manager_name',
            'store_manager_phone',
            'store_manager_email'
        ]
        exclude = ['created_at', 'updated_at']

    def clean_manager_phone(self):
        phone = self.cleaned_data.get('manager_phone')
        if phone and not phone.isdigit():
            raise ValidationError('Phone number must contain only digits')
        return phone

    def clean_store_manager_phone(self):
        phone = self.cleaned_data.get('store_manager_phone')
        if phone and not phone.isdigit():
            raise ValidationError('Phone number must contain only digits')
        return phone





class ProductForm(forms.ModelForm):
    """Form for creating/editing products"""
    class Meta:
        model = Product
        fields = '__all__'


class ReportForm(forms.ModelForm):
    """
    Form for the Report model that matches exactly with the model fields.
    """
    class Meta:
        model = Report
        fields = [
            # Shop Section
            'shop', 'product', 'shop_current_quantity',
             'stock_file_quantity', 'stock_file_photo', 'po_photo', 'shop_comments',
            
            # Merchandising Section - Before Photos
            'before_merch_photo_1', 'before_merch_photo_2', 'before_merch_photo_3',
            'before_merch_photo_4', 'before_merch_photo_5',
            
            # Merchandising Section - After Photos
            'after_merch_photo_1', 'after_merch_photo_2', 'after_merch_photo_3',
            'after_merch_photo_4', 'after_merch_photo_5',
            
            # Merchandising Comment
            'merchandising_comment',
            
            # Status
            'status',
        ]
        widgets = {
            'shop': forms.Select(attrs={
                'class': 'form-select',
                'onchange': 'this.form.submit()'
            }),
            'product': forms.Select(attrs={'class': 'form-select'}),
            'shop_current_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_file_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'shop_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'merchandising_comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            
            
            # Before merch photos
            'before_merch_photo_1': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'data-preview': 'before-merch-photo-1-preview'
            }),

            'before_merch_photo_2': forms.FileInput(attrs={'class': 'form-control'}),
            'before_merch_photo_3': forms.FileInput(attrs={'class': 'form-control'}),
            'before_merch_photo_4': forms.FileInput(attrs={'class': 'form-control'}),
            'before_merch_photo_5': forms.FileInput(attrs={'class': 'form-control'}),
            
            # After merch photo widgets
            'after_merch_photo_1': forms.FileInput(attrs={'class': 'form-control'}),
            'after_merch_photo_2': forms.FileInput(attrs={'class': 'form-control'}),
            'after_merch_photo_3': forms.FileInput(attrs={'class': 'form-control'}),
            'after_merch_photo_4': forms.FileInput(attrs={'class': 'form-control'}),
            'after_merch_photo_5': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.image_helper = FormHelper()
        self.image_helper.form_tag = False
        
        # Define templates for each image field separately
        stock_file_template = """
        <div class="col-md-6 mb-3">
            <label for="id_stock_file_photo" class="form-label">Stock File Photo</label>
            <div class="custom-file-input-container">
                {{ form.stock_file_photo }}
                <div class="image-preview mt-2">
                    {% if form.instance.stock_file_photo %}
                        <img src="{{ form.instance.stock_file_photo.url }}" 
                             class="img-fluid rounded preview-image" 
                             alt="Stock File Photo">
                    {% endif %}
                </div>
            </div>
            <small class="form-text text-muted">{{ form.stock_file_photo.help_text }}</small>
        </div>
        """

        po_photo_template = """
        <div class="col-md-6 mb-3">
            <label for="id_po_photo" class="form-label">PO Photo</label>
            <div class="custom-file-input-container">
                {{ form.po_photo }}
                <div class="image-preview mt-2">
                    {% if form.instance.po_photo %}
                        <img src="{{ form.instance.po_photo.url }}" 
                             class="img-fluid rounded preview-image" 
                             alt="PO Photo">
                    {% endif %}
                </div>
            </div>
            <small class="form-text text-muted">{{ form.po_photo.help_text }}</small>
        </div>
        """

        # Create layout for image fields
        self.image_helper.layout = Layout(
            HTML(stock_file_template),
            HTML(po_photo_template)
        )

        # Update image field widgets
        self.fields['stock_file_photo'].widget.attrs.update({
            'class': 'form-control image-input',
            'accept': 'image/*',
            'data-preview': 'stock-file-preview'
        })
        self.fields['po_photo'].widget.attrs.update({
            'class': 'form-control image-input',
            'accept': 'image/*',
            'data-preview': 'po-photo-preview'
        })
    
    def clean(self):
        """Add custom validation and calculate discrepancy."""
        cleaned_data = super().clean()
        stock_file_quantity = cleaned_data.get('stock_file_quantity')
        shop_current_quantity = cleaned_data.get('shop_current_quantity')
        
        # You can't directly save to the discrepancy property, but you can calculate and 
        # display it in the template or add it to a context variable
        
        return cleaned_data
        
    def clean_photo_field(self, photo):
        """Helper method to validate photo fields"""
        if photo:
            # Validate file size
            if photo.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError('Image file too large ( > 5mb )')

            # Validate file type
            valid_extensions = ['.jpg', '.jpeg', '.png']
            import os
            ext = os.path.splitext(photo.name)[1]
            if ext.lower() not in valid_extensions:
                raise ValidationError('Unsupported file extension. Use jpg, jpeg or png')
        return photo

    def clean_shop_photo(self):
        return self.clean_photo_field(self.cleaned_data.get('shop_photo'))

    def clean(self):
        cleaned_data = super().clean()
        # Add any additional form-wide validation here
        return cleaned_data

class ReportSearchForm(forms.Form):
    """Enhanced Report Search Form with Crispy Forms"""
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label=_('From Date')
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label=_('To Date')
    )
    shop = forms.ModelChoiceField(
        queryset=Shop.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'data-live-search': 'true'}),
        label=_('Shop')
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'data-live-search': 'true'}),
        label=_('Product')
    )
    status = forms.ChoiceField(
        choices=[('', _('All'))] + Report.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('Status')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('date_from', css_class='form-group col-md-6'),
                Column('date_to', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('shop', css_class='form-group col-md-6'),
                Column('product', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Column('status', css_class='form-group'),
            Submit('search', _('Search Reports'), css_class='btn btn-primary')
        )


# Additional form validation mixins
class PhoneValidationMixin:
    """Mixin for phone number validation"""
    def clean_manager_phone(self):
        phone = self.cleaned_data.get('manager_phone')
        if not phone.isdigit():
            raise ValidationError(_('Phone number must contain only digits'))
        return phone

class ShopForm(PhoneValidationMixin, forms.ModelForm):
    """Enhanced Shop Form with Phone Validation"""
    class Meta:
        model = Shop
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            # Add more specific widgets as needed
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6'),
                Column('address', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('manager_name', css_class='form-group col-md-4'),
                Column('manager_phone', css_class='form-group col-md-4'),
                Column('manager_email', css_class='form-group col-md-4'),
                css_class='form-row'
            ),
            Submit('submit', _('Save Shop'), css_class='btn btn-primary')
        )
