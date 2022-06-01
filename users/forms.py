from users.models import *
from django import forms
from django.contrib.auth.forms import UserCreationForm


class UserUpdateForm(forms.ModelForm):
    # username = forms.CharField(widget=forms.TextInput(attrs={
    #     "class": "form-control",
    #     'name': "username"
    # }))
    # email = forms.EmailField(widget=forms.EmailInput(attrs={
    #     "class": "form-control",
    #     'email': "email"
    # }))

    class Meta:
        model = User
        fields = ["display_name", "username", "email", "about", "image", "background_image"]


class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["display_name", "username", "email",]

