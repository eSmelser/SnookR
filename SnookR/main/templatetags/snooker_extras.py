from django import template
from main.models import Session, Sub

register = template.Library()


@register.simple_tag
def get_unregister_url(session: Session, sub: Sub):
    return session.get_unregister_url(sub)