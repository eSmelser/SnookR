import random
from django.contrib.auth import get_user_model


def unique_username(first_name, last_name):
    """Returns a unique username string generated from a first and last name.
    
    If the user's first and last name is unique, the result is the first and last names concatenated.
    Otherwise, the return string is the first and last name followed by four integers.
    """
    username = first_name + last_name
    while get_user_model().objects.filter(username=username).exists():
        username = first_name + last_name + ''.join(random.randint(0, 9) for _ in range(4))

    return username