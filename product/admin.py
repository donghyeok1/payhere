from django.contrib import admin

from product.models import Product, Category


@admin.register(Product)
class ItemAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "category", "price", "cost"]
    list_display_links = ["name"]
    list_filter = ["category", "created_at"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_displat = "__all__"
    list_displat_links = ["name"]
