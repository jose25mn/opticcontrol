from django.urls import path
from .views_products import (
    product_list,
    product_create,
    product_update,
)

urlpatterns = [
    path("", product_list, name="product_list"),
    path("produtos/", product_list, name="product_list"),
    path("produtos/novo/", product_create, name="product_create"),
    path("produtos/<int:pk>/editar/", product_update, name="product_update"),
]
