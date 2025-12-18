from django import forms
from django.utils import timezone

from .models import LensProduct, StockBatch, StockMovement


# =========================
# FEFO - Saída de produto
# =========================
class FefoIssueForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=LensProduct.objects.filter(active=True),
        label="Produto"
    )
    qty = forms.IntegerField(
        min_value=1,
        label="Quantidade"
    )
    note = forms.CharField(
        required=False,
        label="Observação",
        widget=forms.Textarea(attrs={"rows": 2})
    )


# =========================
# Produto - Cadastro fora do admin
# =========================
class LensProductForm(forms.ModelForm):
    class Meta:
        model = LensProduct
        fields = [
            "brand",
            "model",
            "degree_sph",
            "sale_price",
            "min_stock",
            "active",
        ]
        labels = {
            "brand": "Marca",
            "model": "Modelo",
            "degree_sph": "Grau Esférico (SPH)",
            "sale_price": "Valor de venda",
            "min_stock": "Estoque mínimo",
            "active": "Ativo",
        }


def _kind_value_for_entry():
    """
    Retorna o value correto do kind de 'Entrada' baseado nos choices do model.
    Funciona com IN/OUT/LOSS ou Entrada/Saída/Perda etc.
    """
    field = StockMovement._meta.get_field("kind")
    choices = list(getattr(field, "choices", []) or [])

    # 1) tenta value padrão IN
    for v, label in choices:
        if str(v).upper() == "IN":
            return v

    # 2) tenta pelo label em pt-br
    for v, label in choices:
        if "entr" in str(label).lower():
            return v

    # fallback
    return "IN"


class BatchEntryForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=LensProduct.objects.filter(active=True),
        label="Produto",
    )
    lot_code = forms.CharField(
        label="Código do lote",
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Ex: LOTE-2025-001"}),
    )
    expires_at = forms.DateField(
        label="Validade",
        required=True,
        widget=forms.DateInput(attrs={"type": "date"}),
        help_text="Data de vencimento do lote.",
    )
    qty = forms.IntegerField(
        label="Quantidade",
        min_value=1,
        required=True,
        widget=forms.NumberInput(attrs={"placeholder": "Ex: 10"}),
    )
    unit_price = forms.DecimalField(
        label="Custo unitário",
        min_value=0,
        decimal_places=2,
        max_digits=10,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={"step": "0.01", "placeholder": "Ex: 45.90"}),
        help_text="Opcional (mas recomendado para relatórios).",
    )
    note = forms.CharField(
        label="Observação",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Ex: compra do fornecedor X"}),
    )

    def save(self, user):
        product = self.cleaned_data["product"]
        lot_code = self.cleaned_data["lot_code"]
        expires_at = self.cleaned_data["expires_at"]
        qty = self.cleaned_data["qty"]
        unit_price = self.cleaned_data.get("unit_price") or 0
        note = self.cleaned_data.get("note", "")

        batch = StockBatch.objects.create(
            product=product,
            lot_code=lot_code,
            expires_at=expires_at,
        )

        StockMovement.objects.create(
            batch=batch,
            kind=_kind_value_for_entry(),
            qty=qty,
            unit_price=unit_price,
            note=note,
            created_by=user,
        )

        return batch