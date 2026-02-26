from django import forms
from .models import QuickOrder, FullOrder, Review

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
    """Форма полной заявки"""
    class Meta:
        model = FullOrder
        fields = ['full_name', 'phone', 'children_count', 'age_of_children', 'notes']
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
            'children_count': forms.NumberInput(attrs={
                'placeholder': 'Количество детей',
                'class': 'form-input',
                'min': 1,
                'required': True
            }),
            'age_of_children': forms.TextInput(attrs={
                'placeholder': 'Например: 5, 7, 10 лет',
                'class': 'form-input',
                'required': True
            }),
            'notes': forms.Textarea(attrs={
                'placeholder': 'Дополнительные пожелания',
                'class': 'form-input',
                'rows': 3
            }),
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