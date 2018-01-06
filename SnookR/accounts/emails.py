from django.core.mail import send_mail

def send_confirmation_email(user):
    activation_key = user.profile.activation_key
    key_expires = user.profile.key_expires
    dummy_message = '{} {} {} {}'.format(user.first_name, user.username, activation_key, key_expires)
    send_mail(
        'Subject here',
        dummy_message,
        'from@example.com',
        [user.email],
        fail_silently=False,
    )
