"""
URL configuration for config project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [

    # =====================================================
    # ADMIN
    # =====================================================

    path(
        "admin/",
        admin.site.urls,
    ),


    # =====================================================
    # MARKETPLACE
    # =====================================================

    path(
        "",
        include("marketplace.urls"),
    ),


    # =====================================================
    # ACCOUNTS
    # =====================================================

    path(
        "accounts/",
        include("accounts.urls"),
    ),


    # =====================================================
    # CART + ORDERS
    # =====================================================

    path(
        "",
        include("orders.urls"),
    ),


    # =====================================================
    # WAREHOUSE
    # =====================================================

    path(
        "warehouse/",
        include("warehouse.urls"),
    ),

]


# =========================================================
# MEDIA FILES - DEVELOPMENT
# =========================================================

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )