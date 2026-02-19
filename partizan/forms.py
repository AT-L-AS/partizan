from django import forms
from .models import QuickOrder, FullOrder, Review

class QuickOrderForm(forms.ModelForm):
    class Meta:
        model = QuickOrder
        fields = ['phone']
        widgets = {
            'phone': forms.TextInput(attrs={
                'placeholder': 'Ваш телефон',
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
                'placeholder': 'ФИО',
                'class': 'form-input',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Телефон',
                'class': 'form-input',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email',
                'class': 'form-input'
            }),
            'children_count': forms.NumberInput(attrs={
                'placeholder': 'Количество детей',
                'class': 'form-input',
                'min': 1,
                'required': True
            }),
            'age_of_children': forms.TextInput(attrs={
                'placeholder': 'Возраст детей',
                'class': 'form-input',
                'required': True
            }),
            'notes': forms.Textarea(attrs={
                'placeholder': 'Примечания',
                'class': 'form-input',
                'rows': 4
            }),
        }

class ReviewForm(forms.ModelForm):
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