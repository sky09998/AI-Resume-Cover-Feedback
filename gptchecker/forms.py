# forms.py
from django import forms
from .models import Document
from .models import Order
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

        
class DocumentForm(forms.ModelForm):
    DOCUMENT_CHOICES = (
        ('resume', 'Resume'),
        ('cover_letter', 'Cover Letter'),
    )
    document_type = forms.ChoiceField(choices=DOCUMENT_CHOICES)

    class Meta:
        model = Document
        fields = ('uploaded_file', 'document_type')

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)