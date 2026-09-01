from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from marketplace.models import Product
from warehouse.models import Inventory

from .models import Order, OrderItem


# =========================================================
# ADD TO CART
# =========================================================

def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id,
    )

    cart = request.session.get(
        "cart",
        {},
    )

    product_id = str(product_id)

    current_quantity = cart.get(
        product_id,
        0,
    )

    if current_quantity < product.quantity:

        cart[product_id] = (
            current_quantity + 1
        )

        request.session["cart"] = cart
        request.session.modified = True

    else:

        messages.warning(
            request,
            f"Only {product.quantity} {product.unit} of "
            f"{product.name} are available.",
        )

    return redirect("cart")


# =========================================================
# CART
# =========================================================

def cart(request):

    cart_data = request.session.get(
        "cart",
        {},
    )

    cart_items = []
    total = 0

    for product_id, quantity in cart_data.items():

        try:

            product = Product.objects.get(
                id=product_id,
            )

        except Product.DoesNotExist:

            continue

        if quantity <= 0:
            continue

        if quantity > product.quantity:

            quantity = product.quantity

            cart_data[str(product_id)] = quantity

        subtotal = (
            product.price * quantity
        )

        total += subtotal

        cart_items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

    request.session["cart"] = cart_data
    request.session.modified = True

    return render(
        request,
        "marketplace/cart.html",
        {
            "cart_items": cart_items,
            "total": total,
        },
    )


# =========================================================
# UPDATE CART
# =========================================================

def update_cart(request, product_id):

    if request.method == "POST":

        product = get_object_or_404(
            Product,
            id=product_id,
        )

        try:

            quantity = int(
                request.POST.get(
                    "quantity",
                    1,
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            quantity = 1

        cart = request.session.get(
            "cart",
            {},
        )

        product_id = str(product_id)

        if quantity <= 0:

            cart.pop(
                product_id,
                None,
            )

        elif quantity <= product.quantity:

            cart[product_id] = quantity

        else:

            cart[product_id] = product.quantity

            messages.warning(
                request,
                f"Only {product.quantity} "
                f"{product.unit} of "
                f"{product.name} are available.",
            )

        request.session["cart"] = cart
        request.session.modified = True

    return redirect("cart")


# =========================================================
# REMOVE FROM CART
# =========================================================

def remove_from_cart(
    request,
    product_id,
):

    cart = request.session.get(
        "cart",
        {},
    )

    product_id = str(product_id)

    cart.pop(
        product_id,
        None,
    )

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


# =========================================================
# CHECKOUT
# =========================================================

@login_required
def checkout(request):

    cart_data = request.session.get(
        "cart",
        {},
    )

    cart_items = []
    total = 0

    for product_id, quantity in cart_data.items():

        try:

            product = Product.objects.get(
                id=product_id,
            )

        except Product.DoesNotExist:

            continue

        if quantity <= 0:
            continue

        if quantity > product.quantity:

            messages.error(
                request,
                f"Not enough stock for "
                f"{product.name}.",
            )

            return redirect("cart")

        subtotal = (
            product.price * quantity
        )

        total += subtotal

        cart_items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

    if not cart_items:

        messages.info(
            request,
            "Your cart is empty.",
        )

        return redirect("cart")

    return render(
        request,
        "orders/checkout.html",
        {
            "cart_items": cart_items,
            "total": total,
        },
    )


# =========================================================
# PLACE ORDER
# =========================================================

@login_required
@transaction.atomic
def place_order(request):

    if request.method != "POST":

        return redirect("checkout")

    cart_data = request.session.get(
        "cart",
        {},
    )

    if not cart_data:

        messages.error(
            request,
            "Your cart is empty.",
        )

        return redirect("cart")

    shipping_address = request.POST.get(
        "shipping_address",
        "",
    ).strip()

    if not shipping_address:

        messages.error(
            request,
            "Please enter a delivery address.",
        )

        return redirect("checkout")

    total = 0
    products = []

    # =====================================================
    # VALIDATE PRODUCTS
    # =====================================================

    for product_id, quantity in cart_data.items():

        product = get_object_or_404(
            Product.objects.select_for_update(),
            id=product_id,
        )

        if quantity <= 0:

            messages.error(
                request,
                f"Invalid quantity for {product.name}.",
            )

            return redirect("cart")

        if quantity > product.quantity:

            messages.error(
                request,
                f"Only {product.quantity} "
                f"{product.unit} of "
                f"{product.name} are available.",
            )

            return redirect("cart")

        subtotal = (
            product.price * quantity
        )

        total += subtotal

        products.append(
            {
                "product": product,
                "quantity": quantity,
                "price": product.price,
            }
        )

    # =====================================================
    # CREATE ORDER
    # =====================================================

    order = Order.objects.create(
        customer=request.user,
        total_amount=total,
        shipping_address=shipping_address,
    )

    # =====================================================
    # CREATE ORDER ITEMS + REDUCE STOCK
    # =====================================================

    for item in products:

        product = item["product"]
        quantity = item["quantity"]

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=item["price"],
        )

        # -------------------------------------------------
        # PRODUCT STOCK
        # -------------------------------------------------

        product.quantity -= quantity

        product.save(
            update_fields=[
                "quantity",
                "updated_at",
            ]
        )

        # -------------------------------------------------
        # WAREHOUSE STOCK
        # -------------------------------------------------

        inventory = (
            Inventory.objects
            .select_for_update()
            .filter(
                product=product,
            )
            .first()
        )

        if inventory:

            if quantity > inventory.quantity:

                raise ValueError(
                    f"Warehouse inventory for "
                    f"{product.name} is insufficient."
                )

            inventory.quantity -= quantity

            inventory.save(
                update_fields=[
                    "quantity",
                ]
            )

    # =====================================================
    # CLEAR CART
    # =====================================================

    request.session["cart"] = {}
    request.session.modified = True

    messages.success(
        request,
        f"Order #{order.id} placed successfully.",
    )

    return redirect(
        "order_success",
        order_id=order.id,
    )


# =========================================================
# ORDER SUCCESS
# =========================================================

@login_required
def order_success(
    request,
    order_id,
):

    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user,
    )

    return render(
        request,
        "orders/order_success.html",
        {
            "order": order,
        },
    )


# =========================================================
# MY ORDERS
# =========================================================

@login_required
def my_orders(request):

    orders = (
        Order.objects
        .filter(
            customer=request.user,
        )
        .prefetch_related(
            "items__product",
        )
        .order_by(
            "-created_at",
        )
    )

    return render(
        request,
        "orders/my_orders.html",
        {
            "orders": orders,
        },
    )


# =========================================================
# CANCEL ORDER
# =========================================================

@login_required
@transaction.atomic
def cancel_order(request, order_id):

    if request.method != "POST":

        return redirect("my_orders")

    order = get_object_or_404(
        Order.objects.select_for_update(),
        id=order_id,
        customer=request.user,
    )

    # -----------------------------------------------------
    # CHECK CURRENT STATUS
    # -----------------------------------------------------

    if order.status not in {
        "pending",
        "confirmed",
    }:

        messages.error(
            request,
            "This order can no longer be cancelled.",
        )

        return redirect("my_orders")

    # -----------------------------------------------------
    # PREVENT DOUBLE CANCELLATION
    # -----------------------------------------------------

    if order.status == "cancelled":

        messages.info(
            request,
            "This order is already cancelled.",
        )

        return redirect("my_orders")

    # -----------------------------------------------------
    # RESTORE STOCK
    # -----------------------------------------------------

    order_items = (
        order.items
        .select_related("product")
        .all()
    )

    for item in order_items:

        product = (
            Product.objects
            .select_for_update()
            .get(
                id=item.product_id,
            )
        )

        # -------------------------------------------------
        # RESTORE PRODUCT STOCK
        # -------------------------------------------------

        product.quantity += item.quantity

        product.save(
            update_fields=[
                "quantity",
                "updated_at",
            ]
        )

        # -------------------------------------------------
        # RESTORE WAREHOUSE INVENTORY
        # -------------------------------------------------

        inventory = (
            Inventory.objects
            .select_for_update()
            .filter(
                product=product,
            )
            .first()
        )

        if inventory:

            inventory.quantity += item.quantity

            inventory.save(
                update_fields=[
                    "quantity",
                ]
            )

    # -----------------------------------------------------
    # UPDATE ORDER
    # -----------------------------------------------------

    order.status = "cancelled"

    order.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    messages.success(
        request,
        f"Order #{order.id} has been cancelled "
        f"and the stock has been restored.",
    )

    return redirect("my_orders")


# =========================================================
# FARMER ORDERS
# =========================================================

@login_required
def farmer_orders(request):

    orders = (
        Order.objects
        .filter(
            items__product__farmer=request.user,
        )
        .prefetch_related(
            "items__product",
        )
        .distinct()
        .order_by(
            "-created_at",
        )
    )

    return render(
        request,
        "orders/farmer_orders.html",
        {
            "orders": orders,
        },
    )


# =========================================================
# UPDATE ORDER STATUS
# =========================================================

@login_required
@transaction.atomic
def update_order_status(
    request,
    order_id,
):

    if request.method != "POST":

        return redirect("farmer_orders")

    order = get_object_or_404(
        Order,
        id=order_id,
    )

    # -----------------------------------------------------
    # VERIFY FARMER OWNS A PRODUCT IN THIS ORDER
    # -----------------------------------------------------

    owns_product = order.items.filter(
        product__farmer=request.user,
    ).exists()

    if not owns_product:

        messages.error(
            request,
            "You are not allowed to update this order.",
        )

        return redirect("farmer_orders")

    status = request.POST.get(
        "status",
        "",
    ).strip()

    valid_statuses = {
        "pending",
        "confirmed",
        "shipped",
        "delivered",
        "cancelled",
    }

    if status not in valid_statuses:

        messages.error(
            request,
            "Invalid order status.",
        )

        return redirect("farmer_orders")

    # -----------------------------------------------------
    # DON'T RESTORE STOCK TWICE
    # -----------------------------------------------------

    if (
        status == "cancelled"
        and order.status != "cancelled"
    ):

        order_items = (
            order.items
            .select_related("product")
            .all()
        )

        for item in order_items:

            product = (
                Product.objects
                .select_for_update()
                .get(
                    id=item.product_id,
                )
            )

            product.quantity += item.quantity

            product.save(
                update_fields=[
                    "quantity",
                    "updated_at",
                ]
            )

            inventory = (
                Inventory.objects
                .select_for_update()
                .filter(
                    product=product,
                )
                .first()
            )

            if inventory:

                inventory.quantity += item.quantity

                inventory.save(
                    update_fields=[
                        "quantity",
                    ]
                )

    # -----------------------------------------------------
    # UPDATE STATUS
    # -----------------------------------------------------

    order.status = status

    order.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    messages.success(
        request,
        f"Order #{order.id} status updated to "
        f"{order.get_status_display()}.",
    )

    return redirect("farmer_orders")