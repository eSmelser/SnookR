from collections import OrderedDict

from django.views.generic import FormView
from django.shortcuts import get_object_or_404, reverse
from django.db.models import Q, OuterRef, Subquery
from messaging.forms import MessageForm
from messaging.models import Message
from accounts.models import CustomUser


class MessagingView(FormView):
    template_name = 'messaging/messaging.html'
    form_class = MessageForm

    def get_success_url(self):
        return reverse('messaging:messaging', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        me, myfriend = self.get_users()
        context['messages'] = Message.objects.filter(Q(sender=me, receiver=myfriend) | Q(sender=myfriend, receiver=me)).order_by('timestamp')
        context['recent_messages'] = self.get_recent_messages()
        return context

    def get_initial(self):
        sender, receiver = self.get_users()
        return dict(sender=sender.id, receiver=receiver.id)

    def get_users(self):
        sender = CustomUser.objects.get(id=self.request.user.id)
        receiver = get_object_or_404(CustomUser, username=self.kwargs.get('username', None))
        return sender, receiver

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_recent_messages(self):
        messages = Message.objects.last_message_per_user(self.request.user)
        for message in messages:
            message.friend = message.receiver if message.receiver != self.request.user else message.sender

        return messages
