from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.inventory.middleware import get_current_user
from .models import AuditLog, LensProduct, StockBatch, StockMovement

def _log(action, instance, summary=""):
    user = get_current_user()
    AuditLog.objects.create(
        action=action,
        model=instance.__class__.__name__,
        object_id=str(instance.pk),
        actor=user if getattr(user, "is_authenticated", False) else None,
        summary=summary or str(instance),
    )

@receiver(post_save, sender=LensProduct)
def log_product_save(sender, instance, created, **kwargs):
    _log("CREATED" if created else "UPDATED", instance)

@receiver(post_save, sender=StockBatch)
def log_batch_save(sender, instance, created, **kwargs):
    _log("CREATED" if created else "UPDATED", instance)

@receiver(post_save, sender=StockMovement)
def log_move_save(sender, instance, created, **kwargs):
    _log("CREATED" if created else "UPDATED", instance)

@receiver(post_delete, sender=LensProduct)
def log_product_delete(sender, instance, **kwargs):
    _log("DELETED", instance)

@receiver(post_delete, sender=StockBatch)
def log_batch_delete(sender, instance, **kwargs):
    _log("DELETED", instance)

@receiver(post_delete, sender=StockMovement)
def log_move_delete(sender, instance, **kwargs):
    _log("DELETED", instance)
