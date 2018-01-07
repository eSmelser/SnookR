from collections import OrderedDict

from django.views.generic import FormView, TemplateView
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
        context['messages'] = self.get_messages(me, myfriend)
        context['recent_messages'] = self.get_recent_messages()
        context['friend'] = myfriend
        return context

    def get_messages(self, me, myfriend):
        messages = Message.objects.filter(Q(sender=me, receiver=myfriend) | Q(sender=myfriend, receiver=me)).order_by('timestamp')
        for message in messages:
            if message.receiver == me:
                message.receiver_has_seen = True
                message.save()
            elif message.sender == me:
                message.sender_has_seen = True
                message.save()

        return messages

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


class MessageNewView(TemplateView):
    template_name = 'messaging/message_list_elements.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = CustomUser.objects.get(id=self.request.user.id)
        friend = self.request.GET.get('username')
        messages = Message.objects.filter(Q(sender=user, receiver__username=friend) | Q(sender__username=friend, receiver=user)).order_by('timestamp')
        temp = []
        for message in messages:
            if message.receiver == user and not message.receiver_has_seen:
                message.receiver_has_seen = True
                message.save()
                temp.append(message)
            elif message.sender == user and not message.sender_has_seen:
                message.sender_has_seen = True
                message.save()
                temp.append(message)

        context['messages'] = temp
        return context

class MessageCreateView(FormView):
    template_name = 'messaging/message_list_elements.html'
    form_class = MessageForm

    def post(self, request, *args, **kwargs):
        ret = super().post(request, *args, **kwargs)
        form = self.get_form()
        form_kwargs = self.get_form_kwargs()
        import json
        data = json.loads(self.request.body.decode('utf8'))
        sender = int(data['sender'])
        sender = CustomUser.objects.get(id=sender)
        receiver = int(data['receiver'])
        receiver = CustomUser.objects.get(id=receiver)
        message = Message.objects.create(sender=sender, receiver=receiver, text=data['text'], sender_has_seen=True)
        context = super().get_context_data(**kwargs)
        context['messages'] = [message]
        return self.render_to_response(context, **kwargs)

    def form_valid(self, form):
        context = super().get_context_data(**self.kwargs)
        instance = form.save()
        context['messages'] = [instance]
        print('form_valid()')
        return self.render_to_response(context, **self.kwargs)
