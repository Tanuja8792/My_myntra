from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Order, Notification
from .utils import send_order_email

@receiver(pre_save,sender=Order)
def remember_order_status(sender,instance,**kwargs):
    if instance.pk:
        try: instance._previous_status=Order.objects.get(pk=instance.pk).status
        except Order.DoesNotExist: instance._previous_status=None
    else: instance._previous_status=None

@receiver(post_save,sender=Order)
def notify_status_change(sender,instance,created,**kwargs):
    old=getattr(instance,"_previous_status",None)
    if not created and old and old!=instance.status:
        Notification.objects.create(user=instance.user,title="Order update",message=f"Order {instance.order_id}: {instance.get_status_display()}.")
        send_order_email(instance,f"My Myntra order update: {instance.get_status_display()}")
