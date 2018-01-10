"""Defines custom steps in the social """
from accounts.models import UserProfile


def save_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'google-oauth2':
        profile = UserProfile(user=user)
        image_url = response.get('image', {}).get('url', '')
        if image_url:
            profile.image_url = image_url

        profile.save()
        profile.send_confirmation_email()
        return {'profile': profile}
