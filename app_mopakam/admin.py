from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Country, City, CustomUser, Category, Product,
    Favorite, ShoppingCart, CartItem, Order, Review,
    OrderLine, VerificationCode
)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at', 'updated_at')
    search_fields = ('name', 'code')
    list_filter = ('created_at',)
    ordering = ('name',)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'created_at', 'updated_at')
    list_filter = ('country', 'created_at')
    search_fields = ('name', 'country__name')
    ordering = ('country', 'name')

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone', 'type_user', 'is_active', 'is_staff', 'is_verified', 'is_online')
    list_filter = ('type_user', 'is_active', 'is_staff', 'is_verified', 'is_online', 'gender')
    search_fields = ('username', 'email', 'phone')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'gender')}),
        (_('Location'), {'fields': ('country', 'city')}),
        (_('User type'), {'fields': ('type_user',)}),
        (_('Status'), {'fields': ('is_active', 'is_staff', 'is_verified', 'is_online')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock_quantity', 'status', 'bestseller', 'recommended', 'star_product')
    list_filter = ('category', 'status', 'bestseller', 'recommended', 'star_product')
    search_fields = ('name', 'description')
    ordering = ('name',)
    list_editable = ('status', 'bestseller', 'recommended', 'star_product')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'category')
        }),
        (_('Pricing and Stock'), {
            'fields': ('price', 'discount_percentage', 'stock_quantity')
        }),
        (_('Status and Features'), {
            'fields': ('status', 'bestseller', 'recommended', 'star_product')
        }),
        (_('Image'), {
            'fields': ('image',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product__name')
    ordering = ('-created_at',)

@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username',)
    ordering = ('-created_at',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'total_price')
    list_filter = ('cart__is_active',)
    search_fields = ('cart__user__username', 'product__name')
    ordering = ('-cart__created_at',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['ref', 'user', 'total', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['ref', 'user__email']
    ordering = ['-created_at']
    readonly_fields = ['ref', 'created_at', 'updated_at']

@admin.register(OrderLine)
class OrderLineAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'unit_price', 'line_total')
    list_filter = ('order__status',)
    search_fields = ('order__ref', 'product__name')
    ordering = ('-order__payment_date',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'recommended', 'review_date')
    list_filter = ('rating', 'recommended', 'review_date')
    search_fields = ('product__name', 'user__username', 'comment')
    ordering = ('-review_date',)

@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at')
    search_fields = ('user__username', 'code')
    ordering = ('-created_at',)
