from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from ..models import Product, ShoppingCart, CartItem
from django.db.models import F, Sum
from decimal import Decimal
from django.contrib import messages
from django.shortcuts import redirect
from django.db import transaction
from django.db import IntegrityError
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from ..models import ShoppingCart, CartItem
 
@login_required
def view_cart(request):
    """
    Affiche le contenu du panier
    """
    if request.user.is_authenticated:
        number = CartItem.objects.filter(cart__user=request.user, cart__is_active=True).count()
    else:
        number = 0

    try:
        cart = ShoppingCart.objects.get(user=request.user, is_active=True)
    except ShoppingCart.DoesNotExist:
        cart = None

    cart_items = cart.cart_items.select_related('product').order_by('created_at') if cart else []

    # Calculer les totaux pour chaque article
    for item in cart_items:
        item.total = item.product.price * item.quantity

    # Calculer le sous-total
    subtotal = sum(item.total for item in cart_items)
    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': Decimal('0.00'),
        'total': subtotal,  # Ajouter les frais d'expédition si nécessaire
        'number': number,  # Correction ici
    })


def add_to_cart(request, product_id, redirect_url):
    """Fonction générique pour ajouter un produit au panier avec gestion du stock"""
    try:
        # Récupération du produit ou 404 si non trouvé
        product = get_object_or_404(Product, id=product_id)
        
        # Vérification du stock
        if product.stock_quantity <= 0:
            messages.error(request, f"Désolé, {product} n'est plus en stock.")
            return redirect(redirect_url)
        
        try:
            # Récupération du panier actif pour l'utilisateur
            cart = ShoppingCart.objects.get(user=request.user, is_active=True)
        except ShoppingCart.DoesNotExist:
            # Si le panier n'existe pas, le créer
            cart = ShoppingCart.objects.create(user=request.user, is_active=True)
            messages.info(request, "Un nouveau panier a été créé pour vous")

        with transaction.atomic():
            # Vérifier si l'élément existe déjà dans le panier
            existing_item = CartItem.objects.filter(product=product, cart=cart).first()
            
            if existing_item:
                # Vérifier si l'augmentation de quantité est possible
                if existing_item.quantity + 1 > product.stock_quantity:
                    messages.warning(request, f"Stock insuffisant pour {product}")
                    return redirect(redirect_url)
                
                # Si l'élément existe, augmenter la quantité
                existing_item.quantity += 1
                existing_item.total_price = existing_item.quantity * product.price
                existing_item.save()
                
            else:
                # Si l'élément n'existe pas, créer un nouvel élément dans le panier
                CartItem.objects.create(
                    product=product,
                    cart=cart,
                    quantity=1,
                    total_price=product.price
                )
 
            messages.success(request, f"{product} ajouté au panier")
            
    except Product.DoesNotExist:
        messages.error(request, "Le produit demandé n'existe pas.")
        return redirect(redirect_url)
        
    except ValueError as e:
        messages.error(request, f"Erreur de validation: {str(e)}")
        return redirect(redirect_url)

    except IntegrityError as e:
        messages.error(request, "Erreur d'intégrité de la base de données.")
        return redirect(redirect_url)
        
    except Exception as e:
        # Log l'erreur pour le débogage
        print(f"Erreur inattendue: {type(e).__name__} - {str(e)}")
        messages.error(request, f"Une erreur est survenue: {type(e).__name__}")
        return redirect(redirect_url)

    return redirect(redirect_url)

@login_required
def add_to_cart_product(request, product_id):
    return add_to_cart(request, product_id, 'produit')


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_http_methods
import uuid

@require_http_methods(["GET"])
def update_cart_item_quantity(request, item_id, quantity):
    """
    Met à jour la quantité d'un article dans le panier via URL
    L'item_id est maintenant un UUID
    """
    try:
        cart_item = get_object_or_404(CartItem, 
                                     id=item_id, 
                                     cart__user=request.user)
        
        quantity = int(quantity)
        if quantity < 1:
            quantity = 1
            messages.warning(request, "La quantité minimum est 1")
            
        # Vérifier le stock disponible
        if quantity > cart_item.product.stock_quantity:
            messages.error(request, 
                         f"Désolé, seulement {cart_item.product.stock_quantity} articles disponibles")
            quantity = cart_item.product.stock_quantity
            
        cart_item.quantity = quantity
        cart_item.calculate_total_price()
        cart_item.save()
        
        messages.success(request, "Quantité mise à jour avec succès")
        
    except ValueError:
        messages.error(request, "Quantité invalide")
    except uuid.uuid4:
        messages.error(request, "Article non trouvé")
    
    return redirect('view_cart')

@require_http_methods(["GET"])
def remove_cart_item(request, item_id):
    """
    Supprime un article spécifique du panier
    L'item_id est maintenant un UUID
    """
    try:
        cart_item = get_object_or_404(CartItem, 
                                     id=item_id, 
                                     cart__user=request.user)
        
        product_name = cart_item.product.name
        cart_item.delete()
        
        messages.error(request, f"{product_name} a été retiré du panier")
    except uuid.uuid4:
        messages.error(request, "Article non trouvé")
    
    return redirect('view_cart')

@require_http_methods(["GET"])
def clear_cart(request):
    """
    Vide complètement le panier
    """
    cart = ShoppingCart.objects.get(user=request.user, is_active=True)
    cart.cart_items.all().delete()
    
    messages.error(request, "Votre panier a été vidé")
    return redirect('view_cart')