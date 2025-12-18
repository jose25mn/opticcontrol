from django.contrib import admin
from django.urls import path, include
from apps.inventory import views as inventory_views

urlpatterns = [
    path("admin/", admin.site.urls),

    # ROTA RAIZ (IMPORTANTE PRO RENDER)
    path("", inventory_views.dashboard, name="home"),

    # INVENTORY
    path("", include("apps.inventory.urls")),
]
