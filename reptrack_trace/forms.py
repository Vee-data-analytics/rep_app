from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import Report, Shop, Product, User
from django.core.exceptions import ValidationError
from django.db.models import Q


class ShopForm(forms.ModelForm):
    """Form for creating/editing shops"""
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
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'manager_name': forms.TextInput(attrs={'class': 'form-control'}),
            'manager_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'manager_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'store_manager_name': forms.TextInput(attrs={'class': 'form-control'}),
            'store_manager_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'store_manager_email': forms.EmailInput(attrs={'class': 'form-control'})
        }

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
        widgets = {
            # Add Bootstrap classes to all fields
            field: forms.TextInput(attrs={'class': 'form-control'})
            for field in Product._meta.get_fields() if field.name != 'id'
        }


class ReportForm(forms.ModelForm):
    """
    Form for the Report model that matches exactly with the model fields.
    """
    class Meta:
        model = Report
        fields = [
            # Shop Section
            'shop', 'product', 'shop_current_quantity',
            'stock_file_quantity', 'stock_file_photo',  'shop_comments',
            
            # Merchandising Section - Before Photos
            'before_merch_photo_1', 'before_merch_photo_2', 'before_merch_photo_3',
            'before_merch_photo_4', 'before_merch_photo_5',
            
            # Merchandising Section - After Photos
            'after_merch_photo_1', 'after_merch_photo_2', 'after_merch_photo_3',
            'after_merch_photo_4', 'after_merch_photo_5',
            
            # Merchandising Comment
            'merchandising_comment',
            
            # Include discrepancy field
            'discrepancy',
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
            'discrepancy': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',
                'id': 'id_discrepancy'
            }),
            
            # Stock file and PO photos
            'stock_file_photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            
            
            # Before merch photos
            'before_merch_photo_1': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'id_before_merch_photo_1'
            }),
            'before_merch_photo_2': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'id_before_merch_photo_2'
            }),
            'before_merch_photo_3': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'id_before_merch_photo_3'
            }),
            'before_merch_photo_4': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'id_before_merch_photo_4'
            }),
            'before_merch_photo_5': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'id_before_merch_photo_5'
            }),
            
            # After merch photos
            'after_merch_photo_1': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'id_after_merch_photo_1'
            }),
            'after_merch_photo_2': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'id_after_merch_photo_2'
            }),
            'after_merch_photo_3': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'id_after_merch_photo_3'
            }),
            'after_merch_photo_4': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'id_after_merch_photo_4'
            }),
            'after_merch_photo_5': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'id_after_merch_photo_5'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add explicit access properties for template use
        self.before_photos = []
        self.after_photos = []
        
        for i in range(1, 6):
            before_field = f'before_merch_photo_{i}'
            after_field = f'after_merch_photo_{i}'
            


            # Store field references for easier template access
            self.before_photos.append((i, self[before_field], 
                                    getattr(self.instance, before_field, None)))
            self.after_photos.append((i, self[after_field], 
                                   getattr(self.instance, after_field, None)))

        # Make discrepancy field not required
        if 'discrepancy' in self.fields:
            self.fields['discrepancy'].required = False
            
    
    def clean(self):
        cleaned_data = super().clean()
        # Auto-calculate discrepancy if stock_file_quantity and shop_current_quantity are provided
        if 'stock_file_quantity' in cleaned_data and 'shop_current_quantity' in cleaned_data:
            stock_file_qty = cleaned_data.get('stock_file_quantity') or 0
            current_qty = cleaned_data.get('shop_current_quantity') or 0
            cleaned_data['discrepancy'] = stock_file_qty - current_qty
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

    def clean_stock_file_photo(self):
        return self.clean_photo_field(self.cleaned_data.get('stock_file_photo'))
        
    # Clean methods for all photo fields
    def clean_before_merch_photo_1(self):
        return self.clean_photo_field(self.cleaned_data.get('before_merch_photo_1'))
    
    def clean_before_merch_photo_2(self):
        return self.clean_photo_field(self.cleaned_data.get('before_merch_photo_2'))
    
    def clean_before_merch_photo_3(self):
        return self.clean_photo_field(self.cleaned_data.get('before_merch_photo_3'))
    
    def clean_before_merch_photo_4(self):
        return self.clean_photo_field(self.cleaned_data.get('before_merch_photo_4'))
    
    def clean_before_merch_photo_5(self):
        return self.clean_photo_field(self.cleaned_data.get('before_merch_photo_5'))
    
    def clean_after_merch_photo_1(self):
        return self.clean_photo_field(self.cleaned_data.get('after_merch_photo_1'))
    
    def clean_after_merch_photo_2(self):
        return self.clean_photo_field(self.cleaned_data.get('after_merch_photo_2'))
    
    def clean_after_merch_photo_3(self):
        return self.clean_photo_field(self.cleaned_data.get('after_merch_photo_3'))
    
    def clean_after_merch_photo_4(self):
        return self.clean_photo_field(self.cleaned_data.get('after_merch_photo_4'))
    
    def clean_after_merch_photo_5(self):
        return self.clean_photo_field(self.cleaned_data.get('after_merch_photo_5'))


class ReportSearchForm(forms.Form):
    """Report Search Form"""
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
        widget=forms.Select(attrs={'class': 'form-select', 'data-live-search': 'true'}),
        label=_('Shop')
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'data-live-search': 'true'}),
        label=_('Product')
    )
    status = forms.ChoiceField(
        choices=[('', _('All'))] + Report.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Status')
    )