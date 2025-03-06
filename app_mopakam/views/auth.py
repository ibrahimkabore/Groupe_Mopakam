from django.shortcuts import render, redirect
from django.contrib.auth import login,logout,get_backends
from app_mopakam.forms import *
from django.shortcuts import redirect
from app_mopakam.models import VerificationCode
from django.contrib.auth.decorators import login_required
# view de creation de compte 
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import views as auth_views
 
from uuid import UUID
import random
from django.core.mail import send_mail
import pyotp
import qrcode
import io
import base64

class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # On utilise CustomUser au lieu de User
            user = CustomUser.objects.get(
                Q(username=username) | Q(email=username)
            )
            # Vérifie si le mot de passe est correct et si l'utilisateur peut s'authentifier
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
            return None
        except CustomUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None     
    
       
def register(request):
    
    GENDER_CHOICES = [
        ('H', _('Homme')),
        ('F', _('Femme')),
        ('A', _('Autre'))
    ]
    if request.method == 'POST':
        form = CustomUserForm(request.POST , request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('verify')  # Rediriger vers la page de vérification
    else:
        form = CustomUserForm()
    return render(request, 'registration/register.html', {'form': form, 'GENDER_CHOICES': GENDER_CHOICES})

# view de verification de creation de compte 

def verify(request):
    if request.method == 'POST':
        form = VerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                verification_code = VerificationCode.objects.get(code=code)
                user = verification_code.user
                user.is_active = True
                user.is_verified = True
                user.save()
                verification_code.delete()  # Supprimer le code de vérification après validation
                
                # Obtenir le backend d'authentification utilisé
                backend = get_backends()[0]
                login(request, user, backend='accounts.auth_backends.EmailOrUsernameModelBackend')
                return redirect('login')
            except VerificationCode.DoesNotExist:
                form.add_error('code', 'Code invalide')
    else:
        form = VerificationForm()
    return render(request, 'registration/verify.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Ajouter un print de débug
            print("User ID being stored:", str(user.id))
            request.session['pre_2fa_user_id'] = str(user.id)
            # Vérifier que la session est sauvegardée
            print("Session after storage:", request.session.get('pre_2fa_user_id'))
            return redirect('two_factor_method')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

def two_factor_method(request):
    print("Session at start:", request.session.get('pre_2fa_user_id'))
    if 'pre_2fa_user_id' not in request.session:
        print("No pre_2fa_user_id in session")
        return redirect('login')
    
    try:
        user_id = request.session['pre_2fa_user_id']
        user = CustomUser.objects.get(id=user_id)
        print("User found:", user.username)
    except (ValueError, CustomUser.DoesNotExist) as e:
        print("Error:", str(e))
        del request.session['pre_2fa_user_id']
        return redirect('login')
   
    if request.method == 'POST':
        form = TwoFactorMethodForm(request.POST)
        if form.is_valid():
            method = form.cleaned_data['two_factor_method']
            user.two_factor_method = method
            user.save()
           
            if method == 'email':
                code = str(random.randint(100000, 999999))
                request.session['2fa_email_code'] = code
                send_mail(
                    'Code de Vérification - Authentification à Deux Facteurs',
                    f'''
                    Bonjour,

                    Nous vous avons envoyé ce message pour vous fournir votre code de vérification à deux facteurs pour votre compte chez Ghislaine Cosmetic.

                    Votre code de vérification est : {code}

                    Veuillez entrer ce code dans l'application pour terminer votre vérification.

                    Si vous n'avez pas demandé cette vérification, veuillez ignorer ce message.

                    Merci de faire confiance au GROUPE MOPAKAM.

                    Cordialement,
                    L'équipe GROUPE MOPAKAM
                    ''',
                    'no-reply@GROUPEMOPAKAM.com',
                    [user.email],
                    fail_silently=False,
                )
                return redirect('email_verification')
           
            elif method == 'google_auth':
                # Check if user already has Google Auth set up
                if user.google_auth_secret:  # Assuming you store the secret in this field
                    return redirect('google_auth_verification')
                    
                # If not set up, continue with new setup
                secret = user.generate_google_auth_secret()
                totp = pyotp.TOTP(secret)
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(totp.provisioning_uri(name=user.username, issuer_name='Groupe Mopakam'))
                qr.make(fit=True)
               
                img = qr.make_image(fill_color="black", back_color="green")
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                qr_code = base64.b64encode(buffered.getvalue()).decode()
               
                return render(request, 'registration/google_auth_setup.html', {
                    'qr_code': qr_code,
                    'secret': secret
                })
    else:
        form = TwoFactorMethodForm()
   
    return render(request, 'registration/two_factor_method.html', {'form': form})

def email_verification(request):
    if 'pre_2fa_user_id' not in request.session or '2fa_email_code' not in request.session:
        return redirect('login')
    
    user = CustomUser.objects.get(id=request.session['pre_2fa_user_id'])
    
    if request.method == 'POST':
        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            if code == request.session['2fa_email_code']:
                # Specify the backend explicitly
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                del request.session['pre_2fa_user_id']
                del request.session['2fa_email_code']
                return redirect('produit')
            else:
                messages.error(request, 'Invalid verification code')
    else:
        form = EmailVerificationForm()
    
    return render(request, 'registration/email_verification.html', {'form': form})

def google_auth_verification(request):
    if 'pre_2fa_user_id' not in request.session:
        return redirect('login')
    
    user = CustomUser.objects.get(id=request.session['pre_2fa_user_id'])
    
    if request.method == 'POST':
        form = GoogleAuthVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            if user.verify_google_auth_code(code):
                # Specify the backend explicitly
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                del request.session['pre_2fa_user_id']
                return redirect('produit')
            else:
                messages.error(request, 'Invalid authentication code')
    else:
        form = GoogleAuthVerificationForm()
    
    return render(request, 'registration/google_auth_verification.html', {'form': form})

@login_required
def deconnection(request):
    logout(request)
    # Redirige l'utilisateur vers une page après la déconnexion (par exemple la page d'accueil)
    messages.add_message(request, messages.SUCCESS, " A bientot  " )

    return redirect('accueil')

#view reste password


class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'registration/rest/password_reset.html'

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        if not CustomUser.objects.filter(email=email).exists():
            messages.error(self.request, "Cet email n'est associé à aucun compte utilisateur.")
            return self.form_invalid(form)
        return super().form_valid(form)

from django.shortcuts import render

