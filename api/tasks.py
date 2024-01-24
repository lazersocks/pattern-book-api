from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_purchase_email(user_email, cart_items):
    subject = "Your Purchase Details"
    message = "Thank you for your purchase. Here are the details:\n"
    message += "\n".join(
        [f"- {item.book.title} (Quantity: {item.quantity}) \n" for item in cart_items]
    )

    send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email])
