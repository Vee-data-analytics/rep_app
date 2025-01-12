from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
import json

from django.views.decorators.csrf import csrf_exempt
from .forms import  (
    ProductForm,ShopForm,
    MainStoreForm,
    ShopStoreForm,)

import logging

logger = logging.getLogger(__name__)

from django.http import JsonResponse
from django.shortcuts import render
from .models import Product, MainStore, Shop

def get_shop_details(request):
    shop_id = request.GET.get('shop')
    try:
        shop = Shop.objects.get(id=shop_id)
        return render(request, 'partials/shop_details.html', {'shop': shop})
    except Shop.DoesNotExist:
        return HttpResponse('')

def get_mainstore_details(request):
    mainstore_id = request.GET.get('main_store')
    try:
        mainstore = MainStore.objects.get(id=mainstore_id)
        return render(request, 'partials/mainstore_details.html', {'mainstore': mainstore})
    except MainStore.DoesNotExist:
        return HttpResponse('')

def get_product_details(request):
    product_id = request.GET.get('product')
    try:
        product = Product.objects.get(id=product_id)
        return render(request, 'partials/product_details.html', {'product': product})
    except Product.DoesNotExist:
        return HttpResponse('')


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

def dynamic_fetch(request):
    shop_id = request.GET.get('shop')
    main_store_id = request.GET.get('main_store')
    product_id = request.GET.get('product')

    logger.debug(f"Received request: shop_id={shop_id}, main_store_id={main_store_id}, product_id={product_id}")

    data = {}

    if shop_id:
        try:
            shop = Shop.objects.get(id=shop_id)
            data['selected_shop'] = {
                'address': shop.address,
                'manager_name': shop.manager_name,
                'manager_phone': shop.manager_phone,
            }
            logger.debug(f"Shop data fetched: {data['selected_shop']}")
        except Shop.DoesNotExist:
            logger.warning(f"Shop with ID {shop_id} does not exist.")
            data['selected_shop'] = None

    if main_store_id:
        try:
            main_store = MainStore.objects.get(id=main_store_id)
            data['selected_mainstore'] = {
                'location': main_store.address,
                'manager_name': main_store.manager_name,
                'manager_phone': main_store.manager_phone,
                'manager_email': main_store.manager_email,
            }
            logger.debug(f"Main store data fetched: {data['selected_mainstore']}")
        except MainStore.DoesNotExist:
            logger.warning(f"Main store with ID {main_store_id} does not exist.")
            data['selected_mainstore'] = None

    if product_id:
        try:
            product = Product.objects.get(id=product_id)
            data['selected_product'] = {
                'name': product.name,
            }
            logger.debug(f"Product data fetched: {data['selected_product']}")
        except Product.DoesNotExist:
            logger.warning(f"Product with ID {product_id} does not exist.")
            data['selected_product'] = None

    return JsonResponse(data)