from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from .models import FarmerProfile, CustomerProfile


def register(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        user_type = request.POST.get("user_type", "customer")

        if not username or not email or not password:
            messages.error(request, "Please fill in all required fields.")
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        if user_type == "farmer":
            FarmerProfile.objects.create(
                user=user,
                phone="",
                farm_name="",
                farm_address="",
            )
        else:
            CustomerProfile.objects.create(
                user=user,
                phone="",
                address="",
            )

        login(request, user)

        messages.success(
            request,
            "Account created successfully. Welcome to KisanBasket!"
        )

        return redirect("profile")

    return render(
        request,
        "accounts/register.html"
    )


def login_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            login(request, user)

            messages.success(
                request,
                f"Welcome back, {user.username}!"
            )

            next_url = request.GET.get("next")

            if next_url:
                return redirect(next_url)

            return redirect("home")

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "accounts/login.html"
    )


def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("home")


@login_required
def profile(request):

    user = request.user

    farmer_profile = None
    customer_profile = None

    try:
        farmer_profile = FarmerProfile.objects.get(user=user)
    except FarmerProfile.DoesNotExist:
        pass

    try:
        customer_profile = CustomerProfile.objects.get(user=user)
    except CustomerProfile.DoesNotExist:
        pass

    return render(
        request,
        "accounts/profile.html",
        {
            "user": user,
            "farmer_profile": farmer_profile,
            "customer_profile": customer_profile,
        },
    )


# ==========================================
# EDIT PROFILE
# ==========================================

@login_required
def edit_profile(request):

    user = request.user

    farmer_profile = None
    customer_profile = None

    try:
        farmer_profile = FarmerProfile.objects.get(user=user)
    except FarmerProfile.DoesNotExist:
        pass

    try:
        customer_profile = CustomerProfile.objects.get(user=user)
    except CustomerProfile.DoesNotExist:
        pass


    if request.method == "POST":

        # ==============================
        # COMMON USER INFORMATION
        # ==============================

        email = request.POST.get("email", "").strip()

        if not email:

            messages.error(
                request,
                "Email address cannot be empty."
            )

            return redirect("edit_profile")


        # Check whether another user already has this email

        if User.objects.filter(
            email=email
        ).exclude(
            id=user.id
        ).exists():

            messages.error(
                request,
                "This email address is already in use."
            )

            return redirect("edit_profile")


        user.email = email
        user.save()


        # ==============================
        # FARMER PROFILE
        # ==============================

        if farmer_profile:

            phone = request.POST.get(
                "phone",
                ""
            ).strip()

            farm_name = request.POST.get(
                "farm_name",
                ""
            ).strip()

            farm_address = request.POST.get(
                "farm_address",
                ""
            ).strip()


            farmer_profile.phone = phone
            farmer_profile.farm_name = farm_name
            farmer_profile.farm_address = farm_address

            farmer_profile.save()


        # ==============================
        # CUSTOMER PROFILE
        # ==============================

        elif customer_profile:

            phone = request.POST.get(
                "phone",
                ""
            ).strip()

            address = request.POST.get(
                "address",
                ""
            ).strip()


            customer_profile.phone = phone
            customer_profile.address = address

            customer_profile.save()


        messages.success(
            request,
            "Your profile has been updated successfully."
        )

        return redirect("profile")


    return render(
        request,
        "accounts/edit_profile.html",
        {
            "user": user,
            "farmer_profile": farmer_profile,
            "customer_profile": customer_profile,
        },
    )