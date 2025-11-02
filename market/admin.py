from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Review, Shop

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'parent')  # Affiche le nom, la description et le parent
    list_filter = ('parent',)  # Filtrage par parent pour trouver facilement les sous-catégories
    search_fields = ('name',)  # Permet de rechercher par nom
    ordering = ('name',)  # Classe les catégories par ordre alphabétique
    fields = ('name', 'description', 'parent')  # Champs affichés dans le formulaire d’ajout/édition

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'shop')  # Ajout du champ shop
    list_filter = ('category', 'shop')  # Filtrage par catégorie et boutique
    search_fields = ('name', 'category__name', 'shop__name')  # Recherche par nom, catégorie et nom de la boutique

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('author', 'created_at', 'total_amount')  # Corrected to use 'author' instead of 'user'
    list_filter = ('created_at',)
    search_fields = ('author__username',)  # Corrected to use 'author__username'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('order', 'product')
    search_fields = ('order__id', 'product__name')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'reviewer', 'rating', 'review_date')
    list_filter = ('product', 'reviewer', 'rating')
    search_fields = ('product__name', 'reviewer__username', 'comment')

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'contact_email', 'contact_phone', 'created_at')
    search_fields = ('name', 'owner__username', 'contact_email')
    list_filter = ('created_at',)

