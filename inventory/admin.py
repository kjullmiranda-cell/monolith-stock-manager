from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'description')
    list_filter = ('company',)
    search_fields = ('name', 'company__name')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'sku',
        'name',
        'company',
        'category',
        'quantity',
        'min_stock',
        'cost_price',
        'selling_price',
    )
    list_filter = ('company', 'category', 'unit')
    search_fields = ('name', 'sku', 'company__name')