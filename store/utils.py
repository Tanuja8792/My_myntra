from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

def send_order_email(order,subject=None):
    if not order.user.email: return
    lines=[f"Hello {order.user.username},",f"Your order {order.order_id} is now: {order.get_status_display()}.",""]
    for item in order.items.all():
        lines.append(f"{item.product_name} | Qty {item.quantity} | Rs. {item.unit_price}")
    lines += ["",f"Total: Rs. {order.total}",f"Delivery address: {order.address.line1}, {order.address.city} - {order.address.pincode}"]
    send_mail(subject or f"My Myntra order update: {order.order_id}", "\n".join(lines), settings.DEFAULT_FROM_EMAIL,[order.user.email],fail_silently=True)
