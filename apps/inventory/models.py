from datetime import date
from django.db import models
from django.conf import settings
from django.utils import timezone


class LensProduct(models.Model):
    brand = models.CharField(max_length=120)
    model = models.CharField(max_length=120, blank=True)
    degree_sph = models.DecimalField(max_digits=5, decimal_places=2)

    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    min_stock = models.PositiveIntegerField(default=0)

    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.brand} {self.model} | SPH {self.degree_sph}"

    @property
    def total_stock(self):
        return sum(b.balance for b in self.batches.all())


class StockBatch(models.Model):
    product = models.ForeignKey(
        LensProduct,
        related_name="batches",
        on_delete=models.PROTECT
    )
    lot_code = models.CharField(max_length=80, blank=True)
    expires_at = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lote {self.lot_code or self.id} | {self.product}"

    @property
    def balance(self):
        total = 0
        for m in self.movements.all():
            total += m.signed_qty
        return total


class StockMovement(models.Model):
    class Kind(models.TextChoices):
        IN = "IN", "Entrada"
        OUT = "OUT", "Saída"
        LOSS = "LOSS", "Perda"
        ADJUST_IN = "ADJUST_IN", "Ajuste +"
        ADJUST_OUT = "ADJUST_OUT", "Ajuste -"

    batch = models.ForeignKey(
        StockBatch,
        related_name="movements",
        on_delete=models.PROTECT
    )
    kind = models.CharField(max_length=20, choices=Kind.choices)
    qty = models.PositiveIntegerField()

    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    note = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )

    @property
    def signed_qty(self):
        return self.qty if self.kind in [
            self.Kind.IN, self.Kind.ADJUST_IN
        ] else -self.qty

class AuditLog(models.Model):
    action = models.CharField(max_length=20)  # CREATED / UPDATED / DELETED
    model = models.CharField(max_length=120)
    object_id = models.CharField(max_length=64)

    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    at = models.DateTimeField(auto_now_add=True)

    summary = models.TextField(blank=True)  # texto curto do que aconteceu

    def __str__(self):
        return f"[{self.at}] {self.action} {self.model}({self.object_id})"
