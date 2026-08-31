from django.contrib import messages
from django.shortcuts import redirect


def farmer_required(view_func):

    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if not hasattr(request.user, "farmer_profile"):
            messages.error(
                request,
                "Access denied. Farmer account required."
            )
            return redirect("home")

        return view_func(request, *args, **kwargs)

    return wrapper


def customer_required(view_func):

    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if not hasattr(request.user, "customer_profile"):
            messages.error(
                request,
                "Access denied. Customer account required."
            )
            return redirect("home")

        return view_func(request, *args, **kwargs)

    return wrapper