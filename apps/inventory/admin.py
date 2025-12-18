from django.contrib import admin
from .models import LensProduct, StockBatch, StockMovement

admin.site.register(LensProduct)
admin.site.register(StockBatch)
admin.site.register(StockMovement)

