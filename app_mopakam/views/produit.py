from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from app_mopakam.models import Product, Favorite

def produit(request):
    """
    Vue pour afficher la liste des produits.
    """
    # Récupérer tous les produits actifs
    products = Product.objects.all().order_by('-created_at')
    
    # Si l'utilisateur est connecté, récupérer ses favoris
    if request.user.is_authenticated:
        favorite_products = Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
    else:
        favorite_products = []
    
    context = {
        'products': products,
        'favorite_products': favorite_products
    }
    
    return render(request, 'pages/produit.html', context)

 