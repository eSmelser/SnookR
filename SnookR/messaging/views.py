from django.views.generic.base import TemplateView

class MessagingView(TemplateView):
    template_name = 'messaging/messaging.html'
