from django.contrib import admin
from .models import  Product, Shop,ShopStore,Store ,MainStore, Report,Inventory


admin.site.register(Product)
admin.site.register(ShopStore)
admin.site.register(Shop)
admin.site.register(Store)
admin.site.register(MainStore)
admin.site.register(Report)
admin.site.register(Inventory)