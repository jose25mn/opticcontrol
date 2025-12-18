from django.db.models import Sum, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import LensProduct, StockMovement
from .forms import LensProductForm


@login_required
def product_list(request):
    # ---------- filtros ----------
    q = request.GET.get("q", "").strip()
    sph = request.GET.get("sph", "").strip()
    status = request.GET.get("status", "").strip()

    products_qs = LensProduct.objects.all()

    if q:
        products_qs = products_qs.filter(
            Q(brand__icontains=q) | Q(model__icontains=q)
        )

    if sph:
        products_qs = products_qs.filter(degree_sph=sph)

    if status == "active":
        products_qs = products_qs.filter(active=True)
    elif status == "inactive":
        products_qs = products_qs.filter(active=False)

    # ---------- saldo por produto (SEM Case / SEM bug ORM) ----------
    product_data = []
    critical_count = 0

    for p in products_qs:
        total_in = (
            StockMovement.objects
            .filter(batch__product=p, kind="IN")
            .aggregate(total=Sum("qty"))["total"] or 0
        )

        total_out = (
            StockMovement.objects
            .filter(batch__product=p, kind__in=["OUT", "LOSS"])
            .aggregate(total=Sum("qty"))["total"] or 0
        )

        total_stock = total_in - total_out

        is_critical = total_stock < p.min_stock
        if is_critical:
            critical_count += 1

        product_data.append({
            "product": p,
            "total_stock": total_stock,
            "is_critical": is_critical,
        })

    context = {
        "products": product_data,
        "total_products": products_qs.count(),
        "active_products": products_qs.filter(active=True).count(),
        "critical_products": critical_count,
        "sph_choices": (
            LensProduct.objects
            .values_list("degree_sph", flat=True)
            .distinct()
            .order_by("degree_sph")
        ),
        "filters": {
            "q": q,
            "sph": sph,
            "status": status,
        }
    }

    return render(request, "inventory/products/list.html", context)


@login_required
def product_create(request):
    if request.method == "POST":
        form = LensProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Produto cadastrado com sucesso.")
            return redirect("inventory:product_list")
    else:
        form = LensProductForm()

    return render(request, "inventory/products/form.html", {
        "form": form,
        "title": "Novo produto",
    })


@login_required
def product_update(request, pk):
    product = get_object_or_404(LensProduct, pk=pk)

    if request.method == "POST":
        form = LensProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Produto atualizado com sucesso.")
            return redirect("inventory:product_list")
    else:
        form = LensProductForm(instance=product)

    return render(request, "inventory/products/form.html", {
        "form": form,
        "title": "Editar produto",
    })
