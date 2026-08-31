from django.contrib import admin
from .models import Warehouse, Inventory


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "created_at")
    search_fields = ("name", "location")


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("warehouse", "product", "quantity", "updated_at")
    list_filter = ("warehouse",)
    search_fields = ("product__name",)