from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.http import HttpResponse
from django.template.loader import render_to_string
import json

from django.views.decorators.csrf import csrf_exempt
from .forms import  (
    ProductForm,ShopForm,
    MainStoreForm,
    ShopStoreForm,)

from django.http import JsonResponse
from django.shortcuts import render


def handle_modal_form(request, form_class, modal_id, success_message=None, dropdown_id=None):
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()
            return render(request, 'reports/partials/modal_form.html', {
                'form': form,
                'form_submitted': True,
                'success_message': success_message.format(name=instance.name),
                'modal_id': modal_id,
                'dropdown_id': dropdown_id,
                'new_option': {'value': instance.id, 'text': instance.name}
            })
        return render(request, 'reports/partials/modal_form.html', {
            'form': form,
            'modal_id': modal_id
        })
    return HttpResponse("Invalid request", status=400)

def create_shop(request):
    return handle_modal_form(
        request,
        ShopForm,
        'addShopModal',
        'Shop "{name}" created successfully!',
        'id_shop'
    )

def create_store(request):
    return handle_modal_form(
        request,
        StoreForm,
        'newStoreModal',
        'Store "{name}" created successfully!',
        'id_store'
    )

def create_main_store(request):
    return handle_modal_form(
        request,
        MainStoreForm,
        'addMainStoreModal',
        'Main Store "{name}" created successfully!',
        'id_main_store'
    )

def create_shop_store(request):
    return handle_modal_form(
        request,
        ShopStoreForm,
        'newShopStoreModal',
        'Shop Store "{name}" created successfully!',
        'id_shop_store'
    )

def create_product(request):
    return handle_modal_form(
        request,
        ProductForm,
        'addProductModal',
        'Product "{name}" created successfully!',
        'id_product'
    )



def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            # Render the form again as a blank form after saving
            return render(request, 'reports/partials/product_form.html', {
                'product_form': ProductForm(),  # Reset form
                'form_submitted': True,
                'new_product': product
            })
        else:
            # Render the form with errors
            return render(request, 'reports/partials/product_form.html', {
                'product_form': form,
                'form_submitted': False,
            })
    return HttpResponse("Invalid request", status=400)

