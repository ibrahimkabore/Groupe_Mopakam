from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app_mopakam.forms import ContactForm
from django.core.mail import EmailMessage, get_connection
from django.templatetags.static import static
from django.template.loader import render_to_string
def accueil (request):
    
    
    return render(request,'pages/accueil.html')

def apropos (request):
    
    
    return render(request,'pages/apropos.html')

def entreprise (request):
    
    
    return render(request,'pages/entreprise.html')
 

def produit (request):
    
    
    return render(request,'pages/produit.html')

def contact (request):
    
     # URL absolue du logo
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data.get('phone')
            message = form.cleaned_data['message']
            logo_url = request.build_absolute_uri(static('images/oil_of_africa.png'))  # Utiliser une URL absolue

            email_subject = f"Réception de mail d'un visiteur : {name}"
            email_body_html = render_to_string('pages/contact_email.html', {
                'name': name,
                'email': email,
                'phone': phone,
                'message': message,
                'logo_url': logo_url,
            })

            try:
                connection = get_connection()
                connection.open()
                email_message = EmailMessage(
                    email_subject,
                    email_body_html,
                    email,
                    ['ibrahim.kabore.hsg@gmail.com', ],
                    connection=connection,
                )
                email_message.content_subtype = 'html'
                email_message.send(fail_silently=False)
                messages.success(request, f"Merci pour votre message {name}. Nous vous contacterons bientôt.")
            except Exception as e:
                messages.error(request, f"Une erreur est survenue lors de l'envoi du message : {e}")
            finally:
                connection.close()
    else:
        form = ContactForm()
    
    
    return render(request,'pages/contact.html',{'form': form})

def connexion (request):
    
    
    return render(request,'pages/connexion.html')