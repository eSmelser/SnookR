from django import forms
from messaging.models import Message
from accounts.models import CustomUser


class MessageForm(forms.Form):
    sender = forms.IntegerField(widget=forms.HiddenInput, required=True)
    receiver = forms.IntegerField(widget=forms.HiddenInput, required=True)
    text = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Type in a message...'}), required=True)

    def save(self):
        import pdb;pdb.set_trace()
        sender = self.cleaned_data['sender']
        receiver = self.cleaned_data['receiver']
        text = self.cleaned_data['text']
        sender = CustomUser.objects.get(id=sender)
        receiver = CustomUser.objects.get(id=receiver)
        print('save called!')
        return Message.objects.create(sender=sender, receiver=receiver, text=text)
