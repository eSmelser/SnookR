from django import forms
from messaging.models import Message


class MessageForm(forms.Form):
    sender = forms.IntegerField()
    receiver = forms.IntegerField()
    text = forms.CharField()
    class Meta:
        model = Message
        fields = ['text', 'sender', 'receiver']
        widgets = {
            'sender': forms.HiddenInput,
            'receiver':forms.HiddenInput,
        }
