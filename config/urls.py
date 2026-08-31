"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),

    # Marketplace
    path("", include("marketplace.urls")),

    # Accounts
    path("accounts/", include("accounts.urls")),

    # Cart and Orders
    path("", include("orders.urls")),
]


# Serve uploaded media files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )