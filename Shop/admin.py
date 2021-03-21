from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(Category)
admin.site.register(AvailableSizes)
admin.site.register(ProductMaterial)
admin.site.register(ProductImages)
admin.site.register(Cart)
admin.site.register(ProduсtContry)
admin.site.register(CartProduct)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(ProduсtBrand)


class ImageAdmin(admin.TabularInline):
    model = ProductImages


class ProductAdmin(admin.ModelAdmin):
    inlines = [ImageAdmin]


admin.site.register(Product, ProductAdmin)
