import random
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row,Column
from django.core.mail import send_mail
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import modelformset_factory
from django import forms

from .models import *
from django.forms import  DateTimeInput



#formulaire de connexion
class LoginForm(AuthenticationForm): 
    
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur ou e-mail', 'id': 'username'})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe', 'id': 'password'})
    )

#formualire de verification
class VerificationForm(forms.Form):
 
    code = forms.CharField(max_length=6)
    


#formualire de creation de compte 
class  CustomUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('first_name','last_name', 'email','phone','username','password1', 'password2','gender')
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Un compte avec cet e-mail existe déjà.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False  # Désactiver le compte jusqu'à la vérification
        if commit:
            user.save()
            code = str(random.randint(100000, 999999))
            VerificationCode.objects.create(user=user, code=code)
            send_mail(
                'Votre code de vérification',
                f'Votre code de vérification est {code}',
                'kaboremessi@gmail.com',
                [user.email],
                fail_silently=False,
            )
        return user
 
# 2ath

class TwoFactorMethodForm(forms.Form):
    two_factor_method = forms.ChoiceField(
        choices=[
            ('email', 'Receive Code by Email'),
            ('google_auth', 'Use Google Authenticator')
        ],
        widget=forms.RadioSelect,
        label="Choisissez la méthode de deux facteurs"
    )

class EmailVerificationForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={'placeholder': 'Entrez le code'})
    )

class GoogleAuthVerificationForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={'placeholder': 'Entrez le code Google Authenticator'})
    )
    


# # forms.py
# from django import forms
# from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 
            'description', 
            'category', 
            'price', 
            'stock_quantity', 
            'status',
            'image',
            'bestseller',
            'recommended',
            'star_product'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'bestseller': forms.Select(attrs={'class': 'form-select'}),
            'recommended': forms.Select(attrs={'class': 'form-select'}),
            'star_product': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'name': 'Nom du produit',
            'description': 'Description',
            'category': 'Catégorie',
            'price': 'Prix (FCFA)',
            'stock_quantity': 'Quantité en stock',
            'status': 'Statut',
            'image': 'Image',
            'bestseller': 'Meilleure vente',
            'recommended': 'Recommandé',
            'star_product': 'Produit vedette'
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Le prix doit être supérieur à 0")
        return price

    def clean_stock_quantity(self):
        quantity = self.cleaned_data.get('stock_quantity')
        if quantity < 0:
            raise forms.ValidationError("La quantité ne peut pas être négative")
        return quantity


from django.core.mail import send_mail


class ContactForm(forms.Form):
    name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=10, required=False)
    message = forms.CharField(widget=forms.Textarea, required=True)
