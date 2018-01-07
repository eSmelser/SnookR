import time
import json

from django.views.generic import FormView, TemplateView, RedirectView
from django.shortcuts import get_object_or_404, reverse
from django.db.models import Q, OuterRef, Subquery
from messaging.forms import MessageForm
from messaging.models import Message
from accounts.models import CustomUser


class MessagingRootView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        most_recent = Message.objects.all_related(self.request.user).order_by('-timestamp')
        if most_recent.exists():
            most_recent = most_recent[0]
            friend = most_recent.get_not_user(self.request.user)
            return reverse('messaging:messaging', kwargs={'username': friend.username})
        else:
            return


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
        messages = Message.objects.select_related('sender', 'receiver').filter(Q(sender=me, receiver=myfriend) | Q(sender=myfriend, receiver=me)).order_by('timestamp')
        before = time.time()
        messages.filter(receiver=me).update(receiver_has_seen=True)
        messages.filter(sender=me).update(sender_has_seen=True)
        elapsed = time.time() - before
        print('elapsed', elapsed)
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
        messages = Message.objects.select_related('sender', 'receiver').filter(Q(sender=user, receiver__username=friend) | Q(sender__username=friend, receiver=user)).order_by('timestamp')
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
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = [self.get_message()]
        return context

    def get_message(self, data, receiver, sender):
        data = self.get_data()
        sender = self.get_sender(data)
        receiver = self.get_receiver(data)
        message = Message.objects.create(sender=sender, receiver=receiver, text=data['text'], sender_has_seen=True)
        return message

    def get_receiver(self, data):
        receiver = int(data['receiver'])
        receiver = CustomUser.objects.get(id=receiver)
        return receiver

    def get_sender(self, data):
        sender = int(data['sender'])
        sender = CustomUser.objects.get(id=sender)
        return sender

    def get_data(self):
        return json.loads(self.request.body.decode('utf8'))

    def form_valid(self, form):
        context = super().get_context_data(**self.kwargs)
        instance = form.save()
        context['messages'] = [instance]
        return self.render_to_response(context, **self.kwargs)