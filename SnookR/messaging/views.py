import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, TemplateView, RedirectView
from django.shortcuts import get_object_or_404, reverse, redirect
from django.db.models import Q

from messaging.forms import MessageForm
from messaging.models import Message
from accounts.models import User


class MessagingView(LoginRequiredMixin, FormView):
    template_name = 'messaging/messaging.html'
    form_class = MessageForm

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.request.GET.get('username', False)
        if username:
            context['form'] = self.get_form()
            user, friend = self.get_users(username)
            context['messages'] = self.get_messages(user, friend)
            context['friend'] = friend
        elif self.has_previous_messages():
            return self.redirect_to_most_recent_conversation()
        else:
            context['has_previous_messages'] = False

        context['recent_messages'] = self.get_recent_messages()

        return self.render_to_response(context, **kwargs)

    def has_previous_messages(self):
        return Message.objects.select_related('sender', 'receiver').filter(Q(sender=self.request.user) | Q(receiver=self.request.user)).order_by('timestamp').exists()

    def redirect_to_most_recent_conversation(self):
        url = self.recent_conversation_url()
        return redirect(url)

    def recent_conversation_url(self):
        return reverse('messaging:messaging') + '?username=' + Message.objects.most_recent_friend_of(self.request.user).username

    def get_success_url(self):
        return reverse('messaging:messaging')

    def get_messages(self, user, friend):
        messages = Message.objects\
            .select_related('sender', 'receiver')\
            .filter(Q(sender=user, receiver=friend) | Q(sender=friend, receiver=user))\
            .order_by('-timestamp')
        messages.filter(receiver=user).update(receiver_has_seen=True)
        messages.filter(sender=user).update(sender_has_seen=True)
        return reversed(messages[:20])

    def get_initial(self):
        username = self.request.GET.get('username', False)
        if username:
            sender, receiver = self.get_users(username)
            return dict(sender=sender.id, receiver=receiver.id)
        else:
            return dict()

    def get_users(self, username):
        sender = User.objects.get(id=self.request.user.id)
        receiver = get_object_or_404(User, username=username)
        return sender, receiver

    def get_recent_messages(self):
        messages = Message.objects.last_message_per_user(self.request.user)
        for message in messages:
            message.friend = message.receiver if message.receiver != self.request.user else message.sender

        return messages


class MessageNewView(TemplateView):
    template_name = 'messaging/message_list_elements.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(id=self.request.user.id)
        friend = self.request.GET.get('username')
        messages = Message.objects\
            .select_related('sender', 'receiver')\
            .filter(Q(sender=user, receiver__username=friend) | Q(sender__username=friend, receiver=user))\
            .order_by('timestamp')
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

    def get_message(self):
        data = self.get_data()
        sender = self.get_sender(data)
        receiver = self.get_receiver(data)
        message = Message.objects.create(sender=sender, receiver=receiver, text=data['text'], sender_has_seen=True)
        return message

    def get_receiver(self, data):
        receiver = int(data['receiver'])
        receiver = User.objects.get(id=receiver)
        return receiver

    def get_sender(self, data):
        sender = int(data['sender'])
        sender = User.objects.get(id=sender)
        return sender

    def get_data(self):
        return json.loads(self.request.body.decode('utf8'))

    def form_valid(self, form):
        context = super().get_context_data(**self.kwargs)
        instance = form.save()
        context['messages'] = [instance]
        return self.render_to_response(context, **self.kwargs)