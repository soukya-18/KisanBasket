from django.urls import path

from .views import (
    add_to_cart,
    cart,
    checkout,
    my_orders,
    order_success,
    place_order,
    remove_from_cart,
    update_cart,
    farmer_orders,
    update_order_status
)


urlpatterns = [
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
        "cart/update/<int:product_id>/",
        update_cart,
        name="update_cart",
    ),

    path(
        "cart/remove/<int:product_id>/",
        remove_from_cart,
        name="remove_from_cart",
    ),

    path(
        "checkout/",
        checkout,
        name="checkout",
    ),

    path(
        "checkout/place-order/",
        place_order,
        name="place_order",
    ),

    path(
        "order-success/<int:order_id>/",
        order_success,
        name="order_success",
    ),

    path(
        "orders/",
        my_orders,
        name="my_orders",
    ),
    path(
    "farmer/orders/",
    farmer_orders,
    name="farmer_orders",
),
path(
    "farmer/orders/<int:order_id>/status/",
    update_order_status,
    name="update_order_status",
),
]