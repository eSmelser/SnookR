from django.core.mail import send_mail

def send_confirmation_email(user):
    send_mail(
        'Subject here',
        'Here is the message.',
        'from@example.com',
        [user.email],
        fail_silently=False,
    )
