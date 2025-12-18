from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Sum

from .forms import FefoIssueForm
from .services.alerts import get_dashboard_context
from .services.fefo import fefo_issue_product
from .models import StockMovement


@login_required
def dashboard(request):
    ctx = get_dashboard_context(expire_days=30, last_moves=15)
    return render(request, "inventory/dashboard.html", ctx)


@login_required
def fefo_issue(request):
    if request.method == "POST":
        form = FefoIssueForm(request.POST)
        if form.is_valid():
            try:
                fefo_issue_product(
                    product=form.cleaned_data["product"],
                    qty=form.cleaned_data["qty"],
                    user=request.user,
                    note=form.cleaned_data.get("note", ""),
                )
                messages.success(request, "Saída FEFO registrada com sucesso.")
                return redirect("inventory:dashboard")
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = FefoIssueForm()

    return render(request, "inventory/fefo_issue.html", {"form": form})

def loss_report(request):
    qs = (
        StockMovement.objects
        .filter(kind=StockMovement.Kind.LOSS)
        .select_related("batch", "batch__product", "created_by")
        .order_by("-created_at")
    )
    total_qty = qs.aggregate(total=Sum("qty"))["total"] or 0

    return render(request, "inventory/loss_report.html", {
        "losses": qs[:200],
        "total_qty": total_qty
    })

def loss_report(request):
    today = now().date()

    batches = (
        StockBatch.objects
        .filter(expires_at__lt=today)
        .annotate(
            saldo=Sum(
                "movements__qty",
                filter=None
            )
        )
    )

    rows = []

    for b in batches:
        saldo = b.movements.aggregate(
            total=Sum("qty")
        )["total"] or 0

        if saldo > 0:
            rows.append({
                "batch": b,
                "saldo": saldo,
                "loss_value": saldo * b.movements.filter(kind="IN").first().unit_price,
            })

    return render(
        request,
        "inventory/losses/list.html",
        {
            "rows": rows,
        }
    )
