from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Shop, MainStore, Report, Product
from django.core.exceptions import ValidationError
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Row, Column, Submit, HTML, Field
from django.utils.translation import gettext_lazy as _
from django import forms
from .models import Report, Shop, Product,ShopStore ,MainStore
from django.core.exceptions import ValidationError
from django import forms
from django.db.models import Q




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
    
    

class MainStoreForm(forms.ModelForm):
    """Form for creating/editing main stores"""
    class Meta:
        model = MainStore
        fields = '__all__'
        
    def clean_manager_phone(self):
        phone = self.cleaned_data.get('manager_phone')
        if not phone.isdigit():
            raise ValidationError('Phone number must contain only digits')
        return phone


class ShopStoreForm(forms.ModelForm):
    class Meta:
        model = ShopStore
        fields = '__all__'
    def clean_manager_phone(self):
        phone = self.cleaned_data.get('manager_phone')
        if not phone.isdigit():
            raise ValidationError('Phone number must contain only digits')
        return phone


class ProductForm(forms.ModelForm):
    """Form for creating/editing products"""
    class Meta:
        model = Product
        fields = '__all__'


class ReportForm(forms.ModelForm):
    topup_quantity = forms.IntegerField(
    widget=forms.NumberInput(attrs={'class': 'form-control'}),
    help_text="This field is auto-calculated on draft",
    required=False  
)
    
    """Form for creating and editing reports"""
    class Meta:
        model = Report
        fields = [
            # Shop Section
            'shop', 'product','shop_current_quantity', 'needs_topup', 
            'desired_quantity', 'topup_quantity', 'shop_photo', 'shop_comments',
            
            # Shop-Stores Section
            'shop_store_manager_confirmed', 'shop_store_current_quantity', 
            'shop_store_has_sufficient_stock', 'quantity_taken_from_shop_store', 'was_shop_updated','shop_store_has_sufficient_stock',
            'remaining_shop_store_quantity', 'shop_store_photo', 'shop_store_comments','shop_photo_update','shop_update_quantity',
            
            
            # Main Store Section
            'main_store', 'main_store_quantity', 'quantity_taken_from_main_store', 'delivered_to_shop_stores','delivered_to_shop',
            'remaining_main_store_quantity','current_shop_photo','quantity_in_shopstores','was_shop_stores_updated','was_shop_m_updated',
            'total_quantity_in_shop' ,'current_shop_store_photo','main_store_photo', 'main_store_comments',
        ]
        widgets = {
            # Shop Section
            'shop': forms.Select(attrs={
                'class': 'form-select',
                'onchange': 'this.form.submit()'
            }),
            'product': forms.Select(attrs={'class': 'form-select'}),
            'shop_current_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'needs_topup': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'desired_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            
            'shop_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'shop_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            
            # Shop-Stores Section
            'shop_store_manager_confirmed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'shop_store_current_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'shop_store_has_sufficient_stock': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'quantity_taken_from_shop_store': forms.NumberInput(attrs={'class': 'form-control'}),
            'was_shop_updated':forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'remaining_shop_store_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'shop_store_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'shop_store_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'shop_photo_update': forms.FileInput(attrs={'class': 'form-control'}),
            'shop_update_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            
            # Main Store Section
            'main_store': forms.Select(attrs={'class': 'form-select'}),
            'main_store_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity_taken_from_main_store': forms.NumberInput(attrs={'class': 'form-control'}),
            'remaining_main_store_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'main_store_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'current_shop_store_photo': forms.FileInput(attrs={'class':'form-control'}),
            'current_shop_photo': forms.FileInput(attrs={'class':'form-control'}),
            'delivered_to_shop_stores':forms.NumberInput(attrs={'class': 'form-control'}),
            'was_shop_m_updated':forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'was_shop_stores_updated' : forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'quantity_in_shopstores': forms.NumberInput(attrs={'class': 'form-control'}),  
            'delivered_to_shop': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_quantity_in_shop': forms.NumberInput(attrs={'class': 'form-control'}),  
            'main_store_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['shop'].widget.attrs.update({
            'class': 'form-select',
            'id': 'id_shop'
        })  # Close the first update() call here
        self.fields['topup_quantity'].widget.attrs.update({
            'readonly': 'readonly',
            'class': 'form-control'
        })  
    

    def clean_shop_store_section(self):
        cleaned_data = self.cleaned_data
        needs_topup = cleaned_data.get('needs_topup')

        # Get Shop-Store section values
        was_shop_updated = cleaned_data.get('was_shop_updated')
        shop_store_current_quantity = cleaned_data.get('shop_store_current_quantity')
        quantity_taken = cleaned_data.get('quantity_taken_from_shop_store')

        if was_shop_updated:
            # Validate required fields when shop is updated
            if shop_store_current_quantity is None:
                self.add_error('shop_store_current_quantity', 'Required when shop is updated')
            if quantity_taken is None:
                self.add_error('quantity_taken_from_shop_store', 'Required when shop is updated')
            
            if shop_store_current_quantity is not None and quantity_taken is not None:
                # Calculate remaining shop store quantity
                remaining = max(0, shop_store_current_quantity - quantity_taken)
                cleaned_data['remaining_shop_store_quantity'] = remaining

                # Calculate shop update quantity
                shop_current = cleaned_data.get('shop_current_quantity', 0)
                cleaned_data['shop_update_quantity'] = shop_current + quantity_taken

                # Validate quantities
                if quantity_taken > shop_store_current_quantity:
                    self.add_error('quantity_taken_from_shop_store', 
                        'Cannot take more quantity than available in shop store')
        cleaned_data = self.clean_shop_store_section()

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make calculated fields readonly
        readonly_fields = [
            'topup_quantity',
            'remaining_main_store_quantity',
            'final_store_quantity',
            'final_shop_quantity',
            'shop_update_quantity',
            'remaining_shop_store_quantity',
            'total_quantity_in_shop',
            'quantity_in_shopstores'
            
            
        ]
        
        for field in readonly_fields:
            if field in self.fields:
                self.fields[field].widget.attrs['readonly'] = True
                self.fields[field].widget.attrs['class'] = 'form-control'
    

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
