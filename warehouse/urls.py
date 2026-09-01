from django.urls import path

from .views import (
    add_inventory,
    create_warehouse,
    reduce_inventory,
    warehouse_dashboard,
)


urlpatterns = [

    path(
        "",
        warehouse_dashboard,
        name="warehouse_dashboard",
    ),

    path(
        "create/",
        create_warehouse,
        name="create_warehouse",
    ),

    path(
        "inventory/add/",
        add_inventory,
        name="add_inventory",
    ),

    path(
        "inventory/<int:inventory_id>/reduce/",
        reduce_inventory,
        name="reduce_inventory",
    ),

]