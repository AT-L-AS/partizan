from django import forms
from .models import QuickOrder, FullOrder, Review
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class QuickOrderForm(forms.ModelForm):
    """Форма быстрой заявки"""
    class Meta:
        model = QuickOrder
        fields = ['phone']
        widgets = {
            'phone': forms.TextInput(attrs={
                'placeholder': 'Ваш номер телефона',
                'class': 'form-input',
                'required': True
            }),
        }

class FullOrderForm(forms.ModelForm):
    class Meta:
        model = FullOrder
        fields = ['full_name', 'phone', 'email', 'children_count', 'age_of_children', 'notes']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'placeholder': 'Иванов Иван Иванович',
                'class': 'form-input',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': '+7 (999) 123-45-67',
                'class': 'form-input',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'your@email.com',
                'class': 'form-input'
            }),
            # ... остальные поля
        }
class ReviewForm(forms.ModelForm):
    """Форма отзыва"""
    class Meta:
        model = Review
        fields = ['name', 'text', 'rating']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Ваше имя',
                'class': 'form-input',
                'required': True
            }),
            'text': forms.Textarea(attrs={
                'placeholder': 'Ваш отзыв',
                'class': 'form-input',
                'rows': 4,
                'required': True
            }),
            'rating': forms.Select(attrs={
                'class': 'form-input',
                'required': True
            }),
        }

class CustomUserCreationForm(UserCreationForm):
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'auth-input',
            'placeholder': '+7 (999) 123-45-67',
            'id': 'id_phone'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'auth-input',
                'placeholder': 'Введите логин',
                'id': 'id_username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'auth-input',
                'placeholder': 'Ваш email',
                'id': 'id_email',
                'required': True
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'auth-input',
                'placeholder': 'Введите пароль',
                'id': 'id_password1'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'auth-input',
                'placeholder': 'Подтвердите пароль',
                'id': 'id_password2'
            })
        }

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'auth-input',
            'placeholder': 'Введите логин'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'auth-input',
            'placeholder': 'Введите пароль'
        })
    )