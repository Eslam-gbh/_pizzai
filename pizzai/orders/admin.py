from django.contrib import admin
from pizzai.orders.models import Order, OrderedItem, ProductVariant, Product, Size, Category

# Register your models here.
admin.site.register(Order)
admin.site.register(OrderedItem)
admin.site.register(ProductVariant)
admin.site.register(Product)
admin.site.register(Size)
admin.site.register(Category)
