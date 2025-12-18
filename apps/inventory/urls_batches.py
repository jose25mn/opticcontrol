from django.urls import path
from .views_batches import batch_list, batch_entry

urlpatterns = [
    path("lotes/", batch_list, name="batch_list"),
    path("lotes/entrada/", batch_entry, name="batch_entry"),
]
