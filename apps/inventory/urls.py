from django.urls import path, include
from . import views  # se tu tem dashboard/fefo/perdas aqui

app_name = "inventory"

urlpatterns = [
    # (opcional) dashboard do inventory
    path("dashboard/", views.dashboard, name="dashboard"),
    path("fefo/saida/", views.fefo_issue, name="fefo_issue"),
    path("relatorios/perdas/", views.loss_report, name="loss_report"),

    # separação clara:
    path("produtos/", include("apps.inventory.urls_products")),
    path("lotes/", include("apps.inventory.urls_batches")),
]
