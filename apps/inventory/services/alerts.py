from datetime import date, timedelta
from django.db.models import Prefetch
from apps.inventory.models import LensProduct, StockBatch, StockMovement

def get_dashboard_context(expire_days: int = 30, last_moves: int = 15):
    today = date.today()
    limit = today + timedelta(days=expire_days)

    # Lotes vencidos / vencendo
    expired_batches = StockBatch.objects.filter(expires_at__lt=today).order_by("expires_at")
    expiring_batches = StockBatch.objects.filter(expires_at__gte=today, expires_at__lte=limit).order_by("expires_at")

    # Baixo estoque (MVP: calcula via property total_stock)
    products = (
        LensProduct.objects.filter(active=True)
        .prefetch_related("batches__movements")
        .order_by("brand", "model", "degree_sph")
    )
    low_stock_products = [p for p in products if p.total_stock <= p.min_stock]

    # Últimas movimentações
    last_movements = (
        StockMovement.objects.select_related("batch", "batch__product", "created_by")
        .order_by("-created_at")[:last_moves]
    )

    return {
        "expired_batches": expired_batches,
        "expiring_batches": expiring_batches,
        "low_stock_products": low_stock_products,
        "last_movements": last_movements,
        "expire_days": expire_days,
    }
