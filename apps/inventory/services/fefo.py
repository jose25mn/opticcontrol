from django.db import transaction
from django.core.exceptions import ValidationError
from apps.inventory.models import StockBatch, StockMovement, LensProduct

@transaction.atomic
def fefo_issue_product(*, product: LensProduct, qty: int, user=None, note: str = ""):
    if qty <= 0:
        raise ValidationError("Quantidade deve ser > 0.")

    remaining = qty

    # Pega lotes do produto, ordenado por validade, e trava pra evitar corrida
    batches = (
        StockBatch.objects.select_for_update()
        .filter(product=product)
        .order_by("expires_at", "id")
    )

    for batch in batches:
        balance = batch.balance
        if balance <= 0:
            continue

        take = min(balance, remaining)
        if take > 0:
            StockMovement.objects.create(
                batch=batch,
                kind=StockMovement.Kind.OUT,
                qty=take,
                created_by=user,
                note=note or f"Saída FEFO (produto {product.id})",
                unit_price=product.sale_price,  # opcional: registra preço do dia
            )
            remaining -= take

        if remaining == 0:
            break

    if remaining > 0:
        raise ValidationError(f"Estoque insuficiente. Faltou {remaining} unidade(s).")

    return True
