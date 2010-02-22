from django import forms
from django.contrib.auth.models import User


class UserForm(forms.Form):
    """
    A form that allows the user to specify a username and email address after
    authenticating with an external service.

    """
    username = forms.RegexField(r'\w+', max_length=255)
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError('This username is already in use.')

