from rest_framework import serializers
from .models import Category, Product, Order, OrderItem, Review, Shop


from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'subcategories', ]

    def get_subcategories(self, obj):
        # Retourner les sous-catégories associées à cette catégorie
        subcategories = obj.subcategories.all()
        return CategorySerializer(subcategories, many=True).data

    def create(self, validated_data):
        # Créer une catégorie
        subcategories_data = validated_data.pop('subcategories', [])
        category = Category.objects.create(**validated_data)
        
        # Créer les sous-catégories associées à cette catégorie
        for subcategory_data in subcategories_data:
            Category.objects.create(parent=category, **subcategory_data)
        
        return category

    def update(self, instance, validated_data):
        # Mettre à jour les informations de la catégorie
        subcategories_data = validated_data.pop('subcategories', [])
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        # Mettre à jour les sous-catégories
        for subcategory_data in subcategories_data:
            Category.objects.update_or_create(
                parent=instance,
                name=subcategory_data['name'],
                defaults=subcategory_data
            )
        return instance


    


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'owner', 'name', 'description', 'address', 'contact_email', 
                  'contact_phone', 'shop_image', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Traitement personnalisé pour l'image téléchargée si nécessaire
        shop_image = validated_data.pop('shop_image', None)
        shop = Shop.objects.create(**validated_data)
        if shop_image:
            shop.shop_image = shop_image
            shop.save()
        return shop


class ProductSerializer(serializers.ModelSerializer):
    # Gestion des relations avec shop et category via leurs ID
    shop_id = serializers.PrimaryKeyRelatedField(queryset=Shop.objects.all(), source='shop')
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category')
    
    # Sérialisation des objets shop et category (en lecture seule)
    shop = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)
    
    # Champs pour l'image et la vidéo (fichiers)
    product_image = serializers.ImageField(required=False)
    product_demo = serializers.FileField(required=False)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'stock', 'product_image', 
            'product_demo', 'shop_id', 'category_id', 'shop', 'category'
        ]

    def create(self, validated_data):
        # Séparer les fichiers (image, vidéo) des autres données
        product_image = validated_data.pop('product_image', None)
        product_demo = validated_data.pop('product_demo', None)
        
        # Créer le produit sans les fichiers pour l'instant
        product = Product.objects.create(**validated_data)

        # Ajouter les fichiers si présents
        if product_image:
            product.product_image = product_image
        if product_demo:
            product.product_demo = product_demo
        
        # Sauvegarder le produit
        product.save()
        return product

    def update(self, instance, validated_data):
        # Récupérer les fichiers potentiels
        product_image = validated_data.pop('product_image', None)
        product_demo = validated_data.pop('product_demo', None)
        
        # Mettre à jour les autres champs
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Mettre à jour les fichiers si présents
        if product_image:
            instance.product_image = product_image
        if product_demo:
            instance.product_demo = product_demo

        # Sauvegarder l'instance
        instance.save()
        return instance


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'price']




class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'author', 'created_at', 'total_amount', 'shop', 'status', 'status_display', 'items']

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.StringRelatedField()

    class Meta:
        model = Review
        fields = ['id', 'product', 'reviewer', 'rating', 'comment', 'review_date']


from rest_framework import serializers
from .models import Like, CartItem, Product


# Serializer pour les likes
class LikeSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    user_name = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Like
        fields = ['id', 'user', 'product', 'product_name', 'user_name', 'created_at']
        read_only_fields = ['id', 'created_at']


# Serializer pour les articles du panier
class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_price = serializers.ReadOnlyField(source='product.price')
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'user', 'product', 'product_name', 'product_price', 'quantity', 'total_price', 'added_at']
        read_only_fields = ['id', 'added_at']

    def get_total_price(self, obj):
        return obj.product.price * obj.quantity


##################################################################################
##############  SERIALIZERS POUR LES DASHBOARDS  #################################

from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Report

class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ['id', 'app_label', 'model']

class ReportSerializer(serializers.ModelSerializer):
    related_object_type = ContentTypeSerializer(read_only=True)  # Lecture seule
    related_object_type_id = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all(),
        source='related_object_type',
        write_only=True
    )  # Lecture/écriture avec ID
    related_object = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id', 'report_type', 'related_object_type', 'related_object_type_id',
            'related_object_id', 'related_object', 'data', 'created_at', 'updated_at'
        ]

    def get_related_object(self, obj):
        """Récupère une représentation simplifiée de l'objet lié."""
        if obj.related_object:
            return str(obj.related_object)
        return None
