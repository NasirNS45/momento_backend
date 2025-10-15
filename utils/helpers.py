from django.conf import settings
from django.core.mail import send_mail as django_send_mail


def send_mail(email: str, subject: str, message: str):
    django_send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )


def get_media_type(file):
    extension = file.name.split(".")[-1]
    if extension in ["jpg", "jpeg", "png"]:
        return "image"
    elif extension in ["mp4", "mov"]:
        return "video"
    return None
