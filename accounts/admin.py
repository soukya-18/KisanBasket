from django.contrib import admin
from .models import FarmerProfile, CustomerProfile


@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ("farm_name", "user", "phone")
    search_fields = ("farm_name", "user__username", "phone")


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone")
    search_fields = ("user__username", "phone")