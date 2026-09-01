from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import farmer_required
from marketplace.models import Product

from .models import Inventory, Warehouse


# =========================================================
# WAREHOUSE DASHBOARD
# =========================================================

@farmer_required
def warehouse_dashboard(request):

    products = Product.objects.filter(
        farmer=request.user
    ).order_by("-created_at")

    inventory_items = Inventory.objects.filter(
        product__farmer=request.user
    ).select_related(
        "product",
        "warehouse",
    ).order_by(
        "product__name"
    )

    warehouses = Warehouse.objects.all().order_by("name")

    total_products = products.count()

    total_stock = sum(
        item.quantity
        for item in inventory_items
    )

    low_stock_items = [
        item
        for item in inventory_items
        if item.quantity <= 10
    ]

    total_low_stock = len(low_stock_items)

    return render(
        request,
        "warehouse/dashboard.html",
        {
            "products": products,
            "inventory_items": inventory_items,
            "warehouses": warehouses,
            "total_products": total_products,
            "total_stock": total_stock,
            "low_stock_items": low_stock_items,
            "total_low_stock": total_low_stock,
        },
    )


# =========================================================
# CREATE WAREHOUSE
# =========================================================

@farmer_required
def create_warehouse(request):

    if request.method != "POST":
        return redirect("warehouse_dashboard")

    name = request.POST.get("name", "").strip()
    location = request.POST.get("location", "").strip()

    if not name:
        messages.error(
            request,
            "Warehouse name is required."
        )
        return redirect("warehouse_dashboard")

    if not location:
        messages.error(
            request,
            "Warehouse location is required."
        )
        return redirect("warehouse_dashboard")

    Warehouse.objects.create(
        name=name,
        location=location,
    )

    messages.success(
        request,
        f"Warehouse '{name}' created successfully."
    )

    return redirect("warehouse_dashboard")


# =========================================================
# ADD INVENTORY
# =========================================================

@farmer_required
def add_inventory(request):

    if request.method != "POST":
        return redirect("warehouse_dashboard")

    warehouse_id = request.POST.get("warehouse")
    product_id = request.POST.get("product")
    quantity_value = request.POST.get("quantity", "").strip()

    if not warehouse_id:
        messages.error(
            request,
            "Please select a warehouse."
        )
        return redirect("warehouse_dashboard")

    if not product_id:
        messages.error(
            request,
            "Please select a product."
        )
        return redirect("warehouse_dashboard")

    try:
        quantity = int(quantity_value)
    except (TypeError, ValueError):
        messages.error(
            request,
            "Please enter a valid quantity."
        )
        return redirect("warehouse_dashboard")

    if quantity <= 0:
        messages.error(
            request,
            "Quantity must be greater than zero."
        )
        return redirect("warehouse_dashboard")

    warehouse = get_object_or_404(
        Warehouse,
        id=warehouse_id
    )

    product = get_object_or_404(
        Product,
        id=product_id,
        farmer=request.user
    )

    inventory, created = Inventory.objects.get_or_create(
        warehouse=warehouse,
        product=product,
        defaults={
            "quantity": 0
        },
    )

    inventory.quantity += quantity
    inventory.save()

    product.quantity += quantity
    product.save(
        update_fields=[
            "quantity",
            "updated_at",
        ]
    )

    messages.success(
        request,
        f"{quantity} {product.unit} of {product.name} added to inventory."
    )

    return redirect("warehouse_dashboard")


# =========================================================
# REDUCE INVENTORY
# =========================================================

@farmer_required
def reduce_inventory(request, inventory_id):

    inventory = get_object_or_404(
        Inventory.objects.select_related(
            "product",
            "warehouse",
        ),
        id=inventory_id,
        product__farmer=request.user,
    )

    if request.method != "POST":
        return redirect("warehouse_dashboard")

    quantity_value = request.POST.get(
        "quantity",
        ""
    ).strip()

    try:
        quantity = int(quantity_value)
    except (TypeError, ValueError):
        messages.error(
            request,
            "Please enter a valid quantity."
        )
        return redirect("warehouse_dashboard")

    if quantity <= 0:
        messages.error(
            request,
            "Quantity must be greater than zero."
        )
        return redirect("warehouse_dashboard")

    if quantity > inventory.quantity:
        messages.error(
            request,
            "You cannot remove more stock than available."
        )
        return redirect("warehouse_dashboard")

    inventory.quantity -= quantity
    inventory.save()

    product = inventory.product

    product.quantity = max(
        product.quantity - quantity,
        0,
    )

    product.save(
        update_fields=[
            "quantity",
            "updated_at",
        ]
    )

    messages.success(
        request,
        f"{quantity} {product.unit} of {product.name} removed from inventory."
    )

    return redirect("warehouse_dashboard")