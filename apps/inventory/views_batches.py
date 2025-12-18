from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import BatchEntryForm
from .models import StockBatch, StockMovement


@login_required
def batch_list(request):
    today = timezone.localdate()

    batches = (
        StockBatch.objects
        .select_related("product")
        .order_by("expires_at", "created_at")
    )

    rows = []

    for b in batches:
        total_in = (
            StockMovement.objects
            .filter(batch=b, kind="IN")
            .aggregate(t=Sum("qty"))["t"] or 0
        )

        total_out = (
            StockMovement.objects
            .filter(batch=b, kind__in=["OUT", "LOSS"])
            .aggregate(t=Sum("qty"))["t"] or 0
        )

        saldo = total_in - total_out

        status = "ok"
        if saldo <= 0:
            status = "zero"
        elif b.expires_at < today:
            status = "expired"
        elif (b.expires_at - today).days <= 30:
            status = "expiring"

        rows.append({
            "batch": b,
            "saldo": saldo,
            "status": status,
        })

    return render(request, "inventory/batches/list.html", {"rows": rows})


@login_required
def batch_entry(request):
    if request.method == "POST":
        form = BatchEntryForm(request.POST)
        if form.is_valid():
            batch = form.save(user=request.user)
            messages.success(
                request,
                f"Entrada registrada com sucesso (Lote {batch.lot_code})."
            )
            return redirect("inventory:batch_list")
    else:
        form = BatchEntryForm()

    return render(request, "inventory/batches/entry.html", {"form": form})
