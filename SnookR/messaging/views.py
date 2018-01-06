from django.views.generic import FormView
from django.shortcuts import get_object_or_404, reverse
from django.db.models import Q
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
        return context

    def get_initial(self):
        sender, receiver = self.get_users()
        return dict(sender=sender.id, receiver=receiver.id)

    def get_users(self):
        sender = self.request.user
        receiver = get_object_or_404(CustomUser, username=self.kwargs.get('username', None))
        return sender, receiver

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
