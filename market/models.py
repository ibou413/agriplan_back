# market/models.py
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

from users.models import CustomUser

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True,null=True)
    Category_image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        related_name='subcategories', 
        blank=True, 
        null=True
    )

    def __str__(self):
        return self.name
    

class Shop(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='shops')  # Vendeur propriétaire
    name = models.CharField(max_length=255, unique=True)  # Nom de la boutique
    description = models.TextField(blank=True, null=True)  # Description de la boutique
    address = models.TextField(blank=True, null=True)  # Adresse physique ou URL
    contact_email = models.EmailField(blank=True, null=True)  # Email de contact
    contact_phone = models.CharField(max_length=15, blank=True, null=True)  # Numéro de téléphone
    shop_image = models.ImageField(upload_to='shop_images/', blank=True, null=True)  # Image de la boutique
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    updated_at = models.DateTimeField(auto_now=True)  # Dernière mise à jour

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    product_image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    product_demo = models.FileField(upload_to='product_videos/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField()
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='shop')

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente de confirmation'),
        ('confirmed', 'Confirmée'),
        ('shipped', 'Expédiée'),
        ('delivered', 'Livrée'),
        ('canceled', 'Annulée'),
        ('failed', 'Échec du paiement'),
        ('paid', 'Payée')
    ]

    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)  # Boutique associée
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Commande {self.id} par {self.author.username} (Boutique: {self.shop.name if self.shop else 'Multiple'})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Review(models.Model):
    # Référence au produit évalué
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # Référence à l'auteur de l'avis
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    # Note attribuée au produit
    rating = models.PositiveIntegerField()
    # Commentaire sur le produit
    comment = models.TextField()
    # Date de l'avis
    review_date = models.DateTimeField(auto_now_add=True)
    # Autres champs pertinents

    def __str__(self):
        return f"Avis de {self.reviewer} sur le produit {self.product}"

class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="likes")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Empêche les doublons

    def __str__(self):
        return f"{self.user} aime {self.product.name}"




class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Empêche les doublons

    def __str__(self):
        return f"{self.quantity} x {self.product.name} dans le panier de {self.user}"



#########################################################################################"
# ######################################################################################
###############   MODELS POUR LES DASHBOARDS    #######################################



from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Report(models.Model):
    REPORT_TYPES = [
        ('global_statistics', 'Statistiques Globales'),
        ('shop_report', 'Rapport des Boutiques'),
        ('popular_product', 'Produits Populaires'),
        ('customer_activity', 'Activité Client'),
        ('product_review_summary', 'Résumé des Avis Produits'),
    ]

    report_type = models.CharField(
        max_length=50,
        choices=REPORT_TYPES,
        help_text="Type de rapport"
    )
    related_object_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Type de l'objet lié (Shop, Product, User, etc.)",
        null=True,
        blank=True
    )
    related_object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="ID de l'objet lié"
    )
    related_object = GenericForeignKey(
        'related_object_type',
        'related_object_id'
    )

    data = models.JSONField(
        default=dict,
        help_text="Données dynamiques du rapport (statistiques, activité, etc.)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.related_object or 'Général'}"

