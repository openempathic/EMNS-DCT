from email.policy import default
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserResisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(choices=(('Other', 'Other'),('Male', 'Male'), ('Female', 'Female')), required=False)
    age = forms.IntegerField(required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(choices=(('Other', 'Other'),('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')))
    age = forms.IntegerField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'age', 'gender', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']
