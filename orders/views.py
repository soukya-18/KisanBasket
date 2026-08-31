from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from marketplace.models import Product
from .models import Order, OrderItem


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get("cart", {})

    product_id = str(product_id)

    current_quantity = cart.get(product_id, 0)

    if current_quantity < product.quantity:
        cart[product_id] = current_quantity + 1

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


def cart(request):
    cart_data = request.session.get("cart", {})

    cart_items = []
    total = 0

    for product_id, quantity in cart_data.items():

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue

        subtotal = product.price * quantity
        total += subtotal

        cart_items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

    return render(
        request,
        "marketplace/cart.html",
        {
            "cart_items": cart_items,
            "total": total,
        },
    )


def update_cart(request, product_id):
    if request.method == "POST":

        product = get_object_or_404(Product, id=product_id)

        try:
            quantity = int(request.POST.get("quantity", 1))
        except (TypeError, ValueError):
            quantity = 1

        cart = request.session.get("cart", {})

        product_id = str(product_id)

        if quantity <= 0:
            cart.pop(product_id, None)

        elif quantity <= product.quantity:
            cart[product_id] = quantity

        else:
            cart[product_id] = product.quantity

        request.session["cart"] = cart
        request.session.modified = True

    return redirect("cart")


def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})

    product_id = str(product_id)

    cart.pop(product_id, None)

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


@login_required
def checkout(request):
    cart_data = request.session.get("cart", {})

    cart_items = []
    total = 0

    for product_id, quantity in cart_data.items():

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue

        subtotal = product.price * quantity
        total += subtotal

        cart_items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

    return render(
        request,
        "orders/checkout.html",
        {
            "cart_items": cart_items,
            "total": total,
        },
    )


@login_required
def place_order(request):

    if request.method != "POST":
        return redirect("checkout")

    cart_data = request.session.get("cart", {})

    if not cart_data:
        return redirect("cart")

    shipping_address = request.POST.get("shipping_address", "").strip()

    if not shipping_address:
        return redirect("checkout")

    total = 0
    products = []

    for product_id, quantity in cart_data.items():

        product = get_object_or_404(Product, id=product_id)

        if quantity <= 0 or quantity > product.quantity:
            return redirect("cart")

        subtotal = product.price * quantity
        total += subtotal

        products.append(
            {
                "product": product,
                "quantity": quantity,
                "price": product.price,
            }
        )

    order = Order.objects.create(
        customer=request.user,
        total_amount=total,
        shipping_address=shipping_address,
    )

    for item in products:

        OrderItem.objects.create(
            order=order,
            product=item["product"],
            quantity=item["quantity"],
            price=item["price"],
        )

        item["product"].quantity -= item["quantity"]
        item["product"].save()

    request.session["cart"] = {}
    request.session.modified = True

    return redirect("order_success", order_id=order.id)


@login_required
def order_success(request, order_id):

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


@login_required
def my_orders(request):

    orders = Order.objects.filter(
        customer=request.user
    ).prefetch_related(
        "items__product"
    )

    return render(
        request,
        "orders/my_orders.html",
        {
            "orders": orders,
        },
    )
@login_required
def farmer_orders(request):
    orders = Order.objects.filter(
        items__product__farmer=request.user
    ).distinct().prefetch_related(
        "items__product"
    ).order_by("-created_at")

    return render(
        request,
        "orders/farmer_orders.html",
        {
            "orders": orders,
        },
    )

@login_required
def update_order_status(request, order_id):

    if request.method != "POST":
        return redirect("farmer_orders")

    order = get_object_or_404(
        Order,
        id=order_id,
        items__product__farmer=request.user,
    )

    new_status = request.POST.get("status")

    valid_statuses = {
        "pending",
        "confirmed",
        "shipped",
        "delivered",
        "cancelled",
    }

    if new_status in valid_statuses:
        order.status = new_status
        order.save(update_fields=["status", "updated_at"])

    return redirect("farmer_orders")