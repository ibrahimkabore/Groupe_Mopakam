from urllib import request
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from app_mopakam.models import CartItem,ShoppingCart,Order,OrderLine
from django.contrib import messages
from django.templatetags.static import static
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator

 
def envoyer_notification_commande(commande):
    """
    Envoie un email de notification avec les détails de la commande
    """
    # Récupérer les lignes de commande
    order_lines = commande.lines.all()
    
    logo_url = "home/logo.png"
    
    # Préparer le contexte pour le template
    context = {
        'user': commande.user,
        'commande': commande,
        'order_lines': order_lines,
        'total': commande.total,
        'date': commande.created_at.strftime('%d/%m/%Y %H:%M'),
        'logo': logo_url
    }
    
    # Générer le contenu de l'email
    sujet = f'Confirmation de votre commande #{commande.ref}'
    message_text = f"""
    Bonjour {commande.user.get_full_name()},
    
    Votre commande #{commande.ref} a été créée avec succès.
    
    Détails de la commande:
    Date: {commande.created_at.strftime('%d/%m/%Y %H:%M')}
    Mode de paiement: {commande.get_payment_method_display()}
    
    Articles commandés:
    {chr(10).join([f"- {line.product.name} x{line.quantity} : {line.line_total}FCFA" for line in order_lines])}
    
    Total: {commande.total} FCFA
    
    Merci de votre confiance!
    """
    
    # Générer la version HTML
    html_message = render_to_string('commande/confirmation_commande.html', context)
    
    # Envoyer l'email
    send_mail(
        subject=sujet,
        message=message_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[commande.user.email],
        html_message=html_message,
        fail_silently=False,
    )
    
    

def creer_commande(request, user, payment_method):
    try:
        # Récupérer le panier actif de l'utilisateur
        panier = ShoppingCart.objects.get(user=user, is_active=True)
        
        # Récupérer tous les items du panier
        cart_items = CartItem.objects.filter(cart=panier)
        
        if cart_items.exists():
            # Vérifier la disponibilité des stocks avant de créer la commande
            for item in cart_items:
                if item.quantity > item.product.stock_quantity:
                    raise ValueError(
                        f"Stock insuffisant pour le produit {item.product.name}. "
                        f"Quantité disponible: {item.product.stock_quantity}"
                    )
            
            # Calculer le total
            total = sum(item.total_price for item in cart_items)
            
            # Créer la commande dans une transaction
            from django.db import transaction
            
            with transaction.atomic():
                # Créer la commande
                commande = Order.objects.create(
                    user=user,
                    payment_method=payment_method,
                    total=total,
                    status='EA'  # En attente
                )
                
                # Créer les lignes de commande et mettre à jour les stocks
                for item in cart_items:
                    # Créer la ligne de commande
                    OrderLine.objects.create(
                        order=commande,
                        product=item.product,
                        quantity=item.quantity,
                        unit_price=item.product.price,
                        line_total=item.total_price
                    )
                    
                    # Mettre à jour le stock du produit
                    product = item.product
                    product.stock_quantity -= item.quantity
                    
                    # Mettre à jour le statut si le stock atteint zéro
                    if product.stock_quantity == 0:
                        product.status = 'out_of_stock'
                    
                    product.save()
                
                # Envoyer l'email de notification
                envoyer_notification_commande(commande)
                
                # Supprimer tous les items du panier
                cart_items.delete()
                
                # Désactiver le panier
                panier.is_active = False
                panier.save()
                
                # Créer un nouveau panier actif pour l'utilisateur
                ShoppingCart.objects.create(user=user, is_active=True)
                
                return commande
                
    except ShoppingCart.DoesNotExist:
        messages.error(request, "Votre panier est introuvable")
        return None
    except ValueError as e:
        messages.error(request, str(e))
        return None
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erreur lors de la création de la commande: {str(e)}")
        messages.error(request, "Une erreur est survenue lors de la création de la commande")
        return None

@login_required
def passer_commande(request):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        # Vérifier si la méthode de paiement est valide
        valid_methods = ['CB', 'MM','W']  # Cash ou Mobile Money
        if payment_method in valid_methods:
            commande = creer_commande(request, request.user, payment_method)
            if commande:
                messages.success(request, "Votre commande a été créée avec succès!")
                return redirect('payement')
            # Les messages d'erreur sont déjà gérés dans creer_commande
        else:
            data = {
                "apikey": "191723936667c0d7c0d48656.82804730",
                "site_id": "105888863",
                "transaction_id":  str(uuid.uuid4()),
                "amount": commande.total_price,
                "currency": "XOF",
                "alternative_currency": "",
                "description": f"Commande n°{commande.ref}",
                "customer_id": str(request.user.id),
                "customer_name": request.user.first_name,
                "customer_surname": request.user.last_name,
                "customer_email": request.user.email,
                "customer_phone_number": request.user.phone_number,
                "customer_address": request.user.address,
                "customer_city": request.user.city,
                "customer_country": request.user.country,
                "customer_state": request.user.state,
                "customer_zip_code": request.user.zip_code,
                "notify_url": "https://",
                "return_url": request.build_absolute_uri(reverse('order_list')),
                "channels": "ALL",
                "metadata": f"user_{request.user.id}",
                "lang": "FR",
                "invoice_data": {
                    "Donnee1": "",
                    "Donnee2": "",
                    "Donnee3": ""
                }
            };
    
    return redirect('payement', data=data)


@login_required
def order_list(request):
    orders = request.user.orders.all().order_by('-created_at')
    if request.user.is_authenticated:
        number = CartItem.objects.filter(cart__user=request.user, cart__is_active=True).count()
    else:
        number = 0
    return render(request, 'commande/historique_commandes.html', {
        'orders': orders,
        'number': number
    })


@login_required
def checkout_view(request):
    cart = ShoppingCart.objects.get(user=request.user, is_active=True)
    cart_items = CartItem.objects.filter(cart=cart)
    
    # Calculer les totaux
    subtotal = sum(item.total_price for item in cart_items)
    print(subtotal)
    total = subtotal  # Ajoutez les frais de livraison si nécessaire
    
    if request.user.is_authenticated:
        number = CartItem.objects.filter(cart__user=request.user, cart__is_active=True).count()
    else:
        number = 0
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': total,
        'number': number
    }
    return render(request, 'commande/valider_commande.html', context)


@login_required
def cancel_order(request, order_ref):
    if request.method == 'POST':
        try:
            order = Order.objects.get(ref=order_ref, user=request.user)
            if order.status == 'EA':  # Seulement si la commande est en attente
                order.status = 'AN'
                order.save()
                
                # Remettre les produits en stock
                for line in order.lines.all():
                    product = line.product
                    product.stock_quantity += line.quantity
                    if product.status == 'out_of_stock' and product.stock_quantity > 0:
                        product.status = 'available'
                    product.save()
                
                return JsonResponse({'success': True})
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Cette commande ne peut plus être annulée'
                })
        except Order.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Commande introuvable'
            })
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

@staff_member_required
def admin_order_list(request):
    """
    Vue pour afficher toutes les commandes (réservée aux administrateurs)
    """
    # Récupérer les paramètres de filtrage
    status = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search = request.GET.get('search', '')

    # Requête de base
    orders = Order.objects.all().order_by('-created_at')

    # Appliquer les filtres
    if status:
        orders = orders.filter(status=status)
    if date_from:
        orders = orders.filter(created_at__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__lte=date_to)
    if search:
        orders = orders.filter(
            ref__icontains=search
        ) | orders.filter(
            user__email__icontains=search
        ) | orders.filter(
            user__first_name__icontains=search
        ) | orders.filter(
            user__last_name__icontains=search
        )

    # Pagination - 20 commandes par page
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Statistiques
    total_orders = orders.count()
    total_revenue = sum(order.total for order in orders)
    pending_orders = orders.filter(status='EA').count()
    completed_orders = orders.filter(status='TE').count()

    context = {
        'page_obj': page_obj,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'status_choices': Order.STATUS_CHOICES,
        'current_status': status,
        'search': search,
        'date_from': date_from,
        'date_to': date_to,
    }

    return render(request, 'commande/admin_order_list.html', context)

@staff_member_required
def get_order_details(request, order_ref):
    """Vue pour récupérer les détails d'une commande au format JSON"""
    try:
        order = Order.objects.get(ref=order_ref)
        order_lines = order.lines.all()
        
        # Préparer les données de la commande
        data = {
            'ref': order.ref,
            'created_at': order.created_at.strftime('%d/%m/%Y %H:%M'),
            'status_display': order.get_status_display(),
            'payment_method_display': order.get_payment_method_display(),
            'total': order.total,
            'user': {
                'full_name': order.user.get_full_name(),
                'email': order.user.email,
                'phone': order.user.phone
            },
            'lines': []
        }
        
        # Ajouter les lignes de commande
        for line in order_lines:
            data['lines'].append({
                'product_name': line.product.name if line.product else 'Produit supprimé',
                'unit_price': line.unit_price,
                'quantity': line.quantity,
                'line_total': line.line_total
            })
        
        return JsonResponse(data)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Commande introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@staff_member_required
def validate_order(request, order_ref):
    """Vue pour valider une commande"""
    if request.method == 'POST':
        try:
            order = Order.objects.get(ref=order_ref, status='EA')
            order.status = 'TE'
            order.save()
            return JsonResponse({'success': True})
        except Order.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Commande introuvable ou ne peut pas être validée'
            })
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})
