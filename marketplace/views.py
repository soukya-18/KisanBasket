from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import farmer_required

from .models import Category, Product


# =========================================================
# HOME
# =========================================================

def home(request):

    search_query = request.GET.get(
        "q",
        ""
    ).strip()

    category_id = request.GET.get(
        "category",
        ""
    ).strip()

    products = Product.objects.select_related(
        "category",
        "farmer",
    ).all().order_by(
        "-created_at"
    )

    categories = Category.objects.all().order_by(
        "name"
    )

    # =====================================================
    # SEARCH
    # =====================================================

    if search_query:

        products = products.filter(
            name__icontains=search_query
        ) | products.filter(
            description__icontains=search_query
        )

        products = products.distinct()


    # =====================================================
    # CATEGORY FILTER
    # =====================================================

    if category_id:

        products = products.filter(
            category_id=category_id
        )


    return render(
        request,
        "marketplace/home.html",
        {
            "products": products,
            "categories": categories,
            "search_query": search_query,
            "selected_category": category_id,
        },
    )


# =========================================================
# PRODUCT DETAIL
# =========================================================

def product_detail(
    request,
    product_id,
):

    product = get_object_or_404(
        Product.objects.select_related(
            "category",
            "farmer",
        ),
        id=product_id,
    )

    return render(
        request,
        "marketplace/product_detail.html",
        {
            "product": product,
        },
    )


# =========================================================
# ADD TO CART
# =========================================================

def add_to_cart(
    request,
    product_id,
):

    product = get_object_or_404(
        Product,
        id=product_id,
    )

    cart = request.session.get(
        "cart",
        {},
    )

    product_id_str = str(
        product_id
    )

    current_quantity = cart.get(
        product_id_str,
        0,
    )


    if product.quantity <= 0:

        messages.error(
            request,
            f"{product.name} is currently out of stock.",
        )

        return redirect("home")


    if current_quantity < product.quantity:

        cart[product_id_str] = (
            current_quantity + 1
        )

        messages.success(
            request,
            f"{product.name} added to your cart.",
        )

    else:

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
# CART
# =========================================================

def cart(request):

    cart_data = request.session.get(
        "cart",
        {},
    )

    cart_items = []

    total = 0

    cleaned_cart = {}


    for product_id, quantity in cart_data.items():

        try:

            product = Product.objects.get(
                id=product_id,
            )

        except Product.DoesNotExist:

            continue


        if quantity <= 0:

            continue


        if product.quantity <= 0:

            continue


        if quantity > product.quantity:

            quantity = product.quantity


        if quantity <= 0:

            continue


        subtotal = (
            product.price * quantity
        )

        total += subtotal


        cleaned_cart[
            str(product_id)
        ] = quantity


        cart_items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )


    request.session["cart"] = cleaned_cart

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

def update_cart(
    request,
    product_id,
):

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


        product_id_str = str(
            product_id
        )


        if quantity <= 0:

            cart.pop(
                product_id_str,
                None,
            )


        elif product.quantity <= 0:

            cart.pop(
                product_id_str,
                None,
            )

            messages.warning(
                request,
                f"{product.name} is out of stock.",
            )


        elif quantity <= product.quantity:

            cart[product_id_str] = quantity


        else:

            cart[product_id_str] = (
                product.quantity
            )

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


    product_id_str = str(
        product_id
    )


    cart.pop(
        product_id_str,
        None,
    )


    request.session["cart"] = cart

    request.session.modified = True


    return redirect("cart")


# =========================================================
# FARMER DASHBOARD
# =========================================================

@farmer_required
def farmer_dashboard(request):

    products = Product.objects.filter(
        farmer=request.user
    ).order_by(
        "-created_at"
    )


    total_products = products.count()


    total_stock = sum(
        product.quantity
        for product in products
    )


    return render(
        request,
        "marketplace/farmer_dashboard.html",
        {
            "products": products,
            "total_products": total_products,
            "total_stock": total_stock,
        },
    )


# =========================================================
# FARMER PRODUCTS
# =========================================================

@farmer_required
def farmer_products(request):

    products = Product.objects.filter(
        farmer=request.user
    ).order_by(
        "-created_at"
    )


    return render(
        request,
        "marketplace/farmer_products.html",
        {
            "products": products,
        },
    )


# =========================================================
# ADD PRODUCT
# =========================================================

@farmer_required
def add_product(request):

    categories = Category.objects.all().order_by(
        "name"
    )


    if request.method == "POST":

        name = request.POST.get(
            "name",
            "",
        ).strip()

        description = request.POST.get(
            "description",
            "",
        ).strip()

        price = request.POST.get(
            "price",
            "",
        ).strip()

        quantity = request.POST.get(
            "quantity",
            "",
        ).strip()

        unit = request.POST.get(
            "unit",
            "kg",
        ).strip()

        category_id = request.POST.get(
            "category"
        )

        image = request.FILES.get(
            "image"
        )


        if not name:

            messages.error(
                request,
                "Product name is required.",
            )

            return redirect(
                "add_product"
            )


        if not description:

            messages.error(
                request,
                "Product description is required.",
            )

            return redirect(
                "add_product"
            )


        if not price:

            messages.error(
                request,
                "Product price is required.",
            )

            return redirect(
                "add_product"
            )


        if not quantity:

            messages.error(
                request,
                "Product quantity is required.",
            )

            return redirect(
                "add_product"
            )


        if not category_id:

            messages.error(
                request,
                "Please select a category.",
            )

            return redirect(
                "add_product"
            )


        try:

            price = float(price)

        except (
            TypeError,
            ValueError,
        ):

            messages.error(
                request,
                "Please enter a valid price.",
            )

            return redirect(
                "add_product"
            )


        try:

            quantity = int(quantity)

        except (
            TypeError,
            ValueError,
        ):

            messages.error(
                request,
                "Please enter a valid quantity.",
            )

            return redirect(
                "add_product"
            )


        if price <= 0:

            messages.error(
                request,
                "Price must be greater than zero.",
            )

            return redirect(
                "add_product"
            )


        if quantity < 0:

            messages.error(
                request,
                "Quantity cannot be negative.",
            )

            return redirect(
                "add_product"
            )


        category = get_object_or_404(
            Category,
            id=category_id,
        )


        product = Product.objects.create(

            farmer=request.user,

            name=name,

            description=description,

            price=price,

            quantity=quantity,

            unit=unit or "kg",

            category=category,

            image=image,
        )


        messages.success(
            request,
            f"{product.name} was added successfully.",
        )


        return redirect(
            "farmer_dashboard"
        )


    return render(
        request,
        "marketplace/add_product.html",
        {
            "categories": categories,
        },
    )


# =========================================================
# EDIT PRODUCT
# =========================================================

@farmer_required
def edit_product(
    request,
    product_id,
):

    product = get_object_or_404(
        Product,
        id=product_id,
        farmer=request.user,
    )


    categories = Category.objects.all().order_by(
        "name"
    )


    if request.method == "POST":

        name = request.POST.get(
            "name",
            "",
        ).strip()

        description = request.POST.get(
            "description",
            "",
        ).strip()

        price = request.POST.get(
            "price",
            "",
        ).strip()

        quantity = request.POST.get(
            "quantity",
            "",
        ).strip()

        unit = request.POST.get(
            "unit",
            "kg",
        ).strip()

        category_id = request.POST.get(
            "category"
        )

        image = request.FILES.get(
            "image"
        )


        if not name:

            messages.error(
                request,
                "Product name is required.",
            )

            return redirect(
                "edit_product",
                product_id=product.id,
            )


        if not description:

            messages.error(
                request,
                "Product description is required.",
            )

            return redirect(
                "edit_product",
                product_id=product.id,
            )


        if not price:

            messages.error(
                request,
                "Product price is required.",
            )

            return redirect(
                "edit_product",
                product_id=product.id,
            )


        if not quantity:

            messages.error(
                request,
                "Product quantity is required.",
            )

            return redirect(
                "edit_product",
                product_id=product.id,
            )


        if not category_id:

            messages.error(
                request,
                "Please select a category.",
            )

            return redirect(
                "edit_product",
                product_id=product.id,
            )


        try:

            price = float(price)

        except (
            TypeError,
            ValueError,
        ):

            messages.error(
                request,
                "Please enter a valid price.",
            )

            return redirect(
                "edit_product",
                product_id=product.id,
            )


        try:

            quantity = int(quantity)

        except (
            TypeError,
            ValueError,
        ):

            messages.error(
                request,
                "Please enter a valid quantity.",
            )

            return redirect(
                "edit_product",
                product_id=product.id,
            )


        if price <= 0:

            messages.error(
                request,
                "Price must be greater than zero.",
            )

            return redirect(
                "edit_product",
                product_id=product.id,
            )


        if quantity < 0:

            messages.error(
                request,
                "Quantity cannot be negative.",
            )

            return redirect(
                "edit_product",
                product_id=product.id,
            )


        category = get_object_or_404(
            Category,
            id=category_id,
        )


        product.name = name

        product.description = description

        product.price = price

        product.quantity = quantity

        product.unit = unit or "kg"

        product.category = category


        if image:

            product.image = image


        product.save()


        messages.success(
            request,
            f"{product.name} was updated successfully.",
        )


        return redirect(
            "farmer_dashboard"
        )


    return render(
        request,
        "marketplace/edit_product.html",
        {
            "product": product,
            "categories": categories,
        },
    )


# =========================================================
# DELETE PRODUCT
# =========================================================

@farmer_required
def delete_product(
    request,
    product_id,
):

    product = get_object_or_404(
        Product,
        id=product_id,
        farmer=request.user,
    )


    if request.method == "POST":

        product_name = product.name

        product.delete()


        messages.success(
            request,
            f"{product_name} was deleted successfully.",
        )


        return redirect(
            "farmer_dashboard"
        )


    return render(
        request,
        "marketplace/delete_product.html",
        {
            "product": product,
        },
    )