from dataclasses import fields
from logging import PlaceHolder
from operator import truediv
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UsernameField, UserCreationForm
from vote import models as voteModels
from django.core.exceptions import ValidationError
from django.contrib.auth.validators import ASCIIUsernameValidator
# to over come the dublicate emails. (to be unique)
def validate_email(value):
    if User.objects.filter(email = value).exists():
        raise ValidationError(
            (f"{value} is taken."),
            params = {'value':value}
        )

class ClaimYourSeatForm(UserCreationForm):
    district = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'ENTER YOUR DISTRICT', 
                'style':'text-transform: uppercase',
                'autofocus':True
            }
        ),
        max_length=4,
        label='District'
    )

    username = UsernameField(
        label='UserName',
        widget=forms.HiddenInput(
            attrs={
                'placeholder': 'ENTER YOUR USERNAME',
                'style':'text-transform: uppercase',
                'autofocus':False
            }
        ) #end of widget
    )

    legalName = forms.CharField(
        label='Legal Name',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'ENTER YOUR NAME',
                'style':'text-transform: uppercase',
                'autofocus':False
            }
        )
    )

    is_reg = forms.BooleanField(required=False)
    is_reg1 = forms.BooleanField(required=False)

    email = forms.EmailField(
        validators = [validate_email],
        widget=forms.TextInput(
            attrs={'placeholder': 'ENTER YOUR EMAIL', 'class':'form-control'}
        )
    )

    address = forms.CharField(
        widget=forms.TextInput, 
        label='Address'
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'placeholder':'ENTER YOUR PASSWORD', 'class':'form-control'}
        ), 
        label='Password'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'placeholder':'ENTER YOUR PASSWORD AGAIN', 'class':'form-control'}
        ),
        label='Conform Password'
    )

    class Meta:
        model = User
        fields = ['username','legalName', 'password1','password2']

class UsersForm(forms.ModelForm):
    class Meta:
        model = voteModels.Users
        fields = '__all__'
    


