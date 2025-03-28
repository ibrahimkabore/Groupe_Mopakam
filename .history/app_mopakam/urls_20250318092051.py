from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView, TemplateView
from django.views.i18n import set_language

from app_mopakam.views import *

urlpatterns = [
    path('', RedirectView.as_view(url='accueil/', permanent=False)),
    path('accueil/',accueil,name='accueil'),
    path('apropos/',apropos,name='apropos'),
    path('entreprise/',entreprise,name='entreprise'),
    path('produit/',produit,name='produit'),
    path('contact/',contact,name='contact'),
    path('connexion/',connexion,name='connexion'),
    path(r'^set_language/$', set_language, name='set_language'),
    
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('two-factor-method/', two_factor_method, name='two_factor_method'),
    path('email-verification/', email_verification, name='email_verification'),
    path('google-auth-verification/', google_auth_verification, name='google_auth_verification'),
    path('deconnexion',deconnection,name='deconnexion'),
    path('verify/', verify, name='verify'),
    
    ####################### view de recuperation de compte #######################
    path('reset-password/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/rest/password_reset_done.html'), name='password_reset_done'),
    path('reset-password/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/rest/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset-password/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/rest/password_reset_complete.html'), name='password_reset_complete'),
    
    ####################### URLs du panier #######################
    path('cart/', view_cart, name='view_cart'),
    path('cart/add/<uuid:product_id>/',add_to_cart_product,name='add_to_cart_product'),
    path('cart/update/<uuid:item_id>/<int:quantity>/',update_cart_item_quantity,name='update_cart_item'),
    path('cart/remove/<uuid:item_id>/',remove_cart_item,name='remove_cart_item'),
    path('cart/clear/',clear_cart, name='clear_cart'),

    ####################### URLs des commandes #######################
    path('orders/', order_list, name='order_list'),
    path('order/create/', passer_commande, name='create_order'),
    path('checkout/', checkout_view, name='checkout'),
    path('order/confirmation/<uuid:commande_id>/',  TemplateView.as_view(template_name='commande/confirmation_commande.html'), name='confirmation_commande'),
    path('order/<str:order_ref>/cancel/', cancel_order, name='cancel_order'),
    path('cinetpay/', cinetpay, name='cinetpay'),

    ####################### URLs de gestion des produits #######################
    # Product Management URLs
    path('products/', product_list, name='product_list'),
    path('products/create/', product_create, name='product_create'),
    path('products/edit/<uuid:product_id>/', product_edit, name='product_edit'),
    path('products/delete/<uuid:product_id>/', product_delete, name='product_delete'),
    path('products/search/', product_search, name='product_search'),
    
    path('i18n/setlang/', set_language, name='set_language'),
    
    path('commande/admin/', admin_order_list, name='admin_order_list'),
    path('commande/details/<str:order_ref>/', get_order_details, name='order_details'),
    path('commande/validate/<str:order_ref>/', validate_order, name='validate_order'),
     
    
    ]