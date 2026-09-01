from django.urls import path

from .views import (
    add_product,
    add_to_cart,
    cart,
    delete_product,
    edit_product,
    farmer_dashboard,
    farmer_products,
    home,
    product_detail,
    remove_from_cart,
)


urlpatterns = [

    # =====================================================
    # HOME
    # =====================================================

    path(
        "",
        home,
        name="home",
    ),


    # =====================================================
    # PRODUCTS
    # =====================================================

    path(
        "products/<int:product_id>/",
        product_detail,
        name="product_detail",
    ),


    # =====================================================
    # CART
    # =====================================================

    path(
        "cart/",
        cart,
        name="cart",
    ),

    path(
        "cart/add/<int:product_id>/",
        add_to_cart,
        name="add_to_cart",
    ),

    path(
        "cart/remove/<int:product_id>/",
        remove_from_cart,
        name="remove_from_cart",
    ),


    # =====================================================
    # FARMER DASHBOARD
    # =====================================================

    path(
        "farmer/dashboard/",
        farmer_dashboard,
        name="farmer_dashboard",
    ),

    path(
        "farmer/products/",
        farmer_products,
        name="farmer_products",
    ),

    path(
        "farmer/products/add/",
        add_product,
        name="add_product",
    ),

    path(
        "farmer/products/<int:product_id>/edit/",
        edit_product,
        name="edit_product",
    ),

    path(
        "farmer/products/<int:product_id>/delete/",
        delete_product,
        name="delete_product",
    ),
]