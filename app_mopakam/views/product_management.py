from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from ..models import Product, Category
from ..forms import ProductForm
import os
from django.core.files.storage import FileSystemStorage
def is_admin(user):
    """Vérifie si l'utilisateur est un administrateur"""
    return user.is_superuser or user.type_user == 'A'

@login_required
@user_passes_test(is_admin)
def product_list(request):
    """Vue pour lister tous les produits avec recherche et filtrage"""
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    
    products = Product.objects.all()
    
    if query:
        products = products.filter(name__icontains=query)
    
    if category:
        products = products.filter(category__name=category)
    
    products = products.order_by('-created_at')
    categories = Category.objects.all().order_by('name')
    
    return render(request, 'product_management/list.html', {
        'products': products,
        'categories': categories,
        'current_category': category,
        'search_query': query
    })

@login_required
@user_passes_test(is_admin)
def product_create(request):
    """Vue pour créer un nouveau produit"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock_quantity = request.POST.get('stock_quantity')
        image = request.FILES.get('image')
        category_name = request.POST.get('category')
        
        try:
            # Récupérer ou créer la catégorie
            category, created = Category.objects.get_or_create(name=category_name)
            
            product = Product.objects.create(
                name=name,
                description=description,
                price=price,
                stock_quantity=stock_quantity,
                category=category,
            )
            
            if image:
                fs = FileSystemStorage()
                filename = fs.save(f'products/{image.name}', image)
                product.image = filename
                product.save()
            
            messages.success(request, 'Produit créé avec succès!')
            return redirect('product_list')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création du produit: {str(e)}')
    
    # Récupérer toutes les catégories pour le formulaire
    categories = Category.objects.all().order_by('name')
    return render(request, 'product_management/create.html', {'categories': categories})

@login_required
@user_passes_test(is_admin)
def product_edit(request, product_id):
    """Vue pour modifier un produit existant"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.stock_quantity = request.POST.get('stock_quantity')
        category_name = request.POST.get('category')
        
        # Mettre à jour la catégorie
        try:
            category, created = Category.objects.get_or_create(name=category_name)
            product.category = category
        except Exception as e:
            messages.error(request, f'Erreur lors de la mise à jour de la catégorie: {str(e)}')
            return render(request, 'product_management/edit.html', {
                'product': product,
                'categories': Category.objects.all().order_by('name')
            })
        
        image = request.FILES.get('image')
        if image:
            # Supprimer l'ancienne image si elle existe
            if product.image:
                if os.path.isfile(product.image.path):
                    os.remove(product.image.path)
            
            fs = FileSystemStorage()
            filename = fs.save(f'products/{image.name}', image)
            product.image = filename
        
        try:
            product.save()
            messages.success(request, 'Produit modifié avec succès!')
            return redirect('product_list')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification du produit: {str(e)}')
    
    # Récupérer toutes les catégories pour le formulaire
    categories = Category.objects.all().order_by('name')
    return render(request, 'product_management/edit.html', {
        'product': product,
        'categories': categories
    })

@login_required
@user_passes_test(is_admin)
def product_delete(request, product_id):
    """Vue pour supprimer un produit"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        try:
            # Supprimer l'image si elle existe
            if product.image:
                if os.path.isfile(product.image.path):
                    os.remove(product.image.path)
            
            product.delete()
            messages.success(request, 'Produit supprimé avec succès!')
            return JsonResponse({'success': True})
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression du produit: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

@login_required
@user_passes_test(is_admin)
def product_search(request):
    """Vue pour rechercher et filtrer les produits"""
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    
    products = Product.objects.all()
    
    if query:
        products = products.filter(name__icontains=query)
    
    if category:
        products = products.filter(category__name=category)
    
    products = products.order_by('-created_at')
    
    # Récupérer toutes les catégories pour le filtre
    categories = Category.objects.all().order_by('name')
    
    return render(request, 'product_management/list.html', {
        'products': products,
        'categories': categories,
        'current_category': category,
        'search_query': query
    })
