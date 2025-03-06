from .models import ShoppingCart, CartItem

def cart_count(request):
    """
    Context processor pour obtenir le nombre d'articles différents dans le panier
    """
    count = 0
    if request.user.is_authenticated:
        try:
            cart = ShoppingCart.objects.get(user=request.user, is_active=True)
            # Compte le nombre de CartItems dans le panier
            count = CartItem.objects.filter(cart=cart).count()
        except ShoppingCart.DoesNotExist:
            count = 0
    return {'cart_count': count}
