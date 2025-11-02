from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from rest_framework.response import Response
from .models import Category, Product, Order, OrderItem, Review, Shop
from .serializers import CategorySerializer, ShopSerializer, ProductSerializer, OrderSerializer, OrderItemSerializer, ReviewSerializer
from rest_framework.parsers import MultiPartParser, FormParser,JSONParser
from rest_framework.decorators import action
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Like, CartItem, Product
from .serializers import LikeSerializer, CartItemSerializer
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import action
from .models import Order, OrderItem, CartItem, Shop
from .serializers import OrderSerializer
from users.models import CustomUser

class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]  # Permet de gérer les uploads de fichiers (images)

    def create(self, request, *args, **kwargs):
        # Créer une catégorie avec l'image téléchargée et les sous-catégories
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        # Sauvegarder la catégorie et les sous-catégories
        serializer.save()

    

class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser,JSONParser]  # Permet de gérer les fichiers multipart (image et vidéo)
    # Action personnalisée pour filtrer les produits par shop ID
    @action(detail=False, methods=['get'], url_path='by-shop/(?P<shop_id>[^/.]+)')
    def get_products_by_shop(self, request, shop_id=None):
        try:
            products = Product.objects.filter(shop_id=shop_id)
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=False, methods=['post'])
    def create_product(self, request):
        # Récupérer les données du formulaire
        name = request.data.get('name')
        description = request.data.get('description')
        category_id = request.data.get('category_id')
        shop_id = request.data.get('shop_id')
        price = request.data.get('price')
        stock = request.data.get('stock')

        # Récupérer les fichiers téléchargés
        image = request.FILES.get('product_image')
        video = request.FILES.get('product_demo')

        # Créer un dictionnaire de données pour le serializer
        data = {
            'name': name,
            'description': description,
            'category_id': category_id,
            'shop_id': shop_id,
            'price': price,
            'stock': stock,
            'product_image': image,
            'product_demo': video
        }

        # Sérialiser les données
        serializer = ProductSerializer(data=data)

        if serializer.is_valid():
            # Sauvegarder le produit dans la base de données
            product = serializer.save()

            # Retourner la réponse avec les informations du produit créé
            return JsonResponse({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': str(product.price),
                'stock': product.stock,
                'image_url': product.product_image.url if product.product_image else None,
                'video_url': product.product_demo.url if product.product_demo else None,
            }, status=201)
        else:
            # Retourner une erreur si les données sont invalides
             return JsonResponse(serializer.errors, status=400)
             
    @action(detail=False, methods=['post'])
    def create_shop_product(self, request):
        # Récupérer l'ID de la boutique depuis les paramètres
        shop_id = request.data.get('shop_id')
        
        # Vérifier si la boutique existe
        try:
            shop = Shop.objects.get(id=shop_id)
        except Shop.DoesNotExist:
            return JsonResponse({'error': 'La boutique n\'existe pas'}, status=status.HTTP_404_NOT_FOUND)
        
        # Récupérer les autres données du produit
        name = request.data.get('name')
        description = request.data.get('description')
        category_id = request.data.get('category_id')
        price = request.data.get('price')
        stock = request.data.get('stock')

        # Récupérer les fichiers téléchargés
        image = request.FILES.get('product_image')
        video = request.FILES.get('product_demo')

        # Créer un dictionnaire de données pour le sérialiseur
        data = {
            'name': name,
            'description': description,
            'price': price,
            'stock': stock,
            'product_image': image,
            'product_demo': video,
            'shop_id': shop.id,
            'category_id': category_id
        }

        # Sérialiser les données
        serializer = ProductSerializer(data=data)

        if serializer.is_valid():
            # Sauvegarder le produit dans la base de données
            product = serializer.save(shop=shop)  # Associer le produit à la boutique

            # Retourner la réponse avec les informations du produit créé
            return JsonResponse({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': str(product.price),
                'stock': product.stock,
                'image_url': product.product_image.url if product.product_image else None,
                'video_url': product.product_demo.url if product.product_demo else None,
            }, status=status.HTTP_201_CREATED)
        else:
            # Retourner une erreur si les données sont invalides
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
         
    @action(detail=False, methods=['put', 'patch'])
    def update_shop_product(self, request):
      
      
    # Récupérer l'ID du produit à mettre à jour
      product_id = request.data.get('product_id')
      if not product_id:
        return JsonResponse({'error': 'ID du produit manquant'}, status=status.HTTP_400_BAD_REQUEST)
      # Récupérer le produit
      try:
          product = Product.objects.get(id=product_id)
      except Product.DoesNotExist:
        return JsonResponse({'error': 'Produit non trouvé'}, status=status.HTTP_404_NOT_FOUND)
       # Vérification que la boutique correspond (optionnel)
      shop_id = request.data.get('shop_id')
      if shop_id and product.shop.id != int(shop_id):
        return JsonResponse({'error': 'Ce produit n\'appartient pas à cette boutique'}, status=status.HTTP_400_BAD_REQUEST)

      updated_data = {
        'name': request.data.get('name', product.name),
        'description': request.data.get('description', product.description),
        'price': request.data.get('price', product.price),
        'stock': request.data.get('stock', product.stock),
        'category_id': request.data.get('category_id', product.category.id if product.category else None),
    }
      
      image = request.FILES.get('product_image')
      video = request.FILES.get('product_demo')

      if image:
        updated_data['product_image'] = image
      if video:
        updated_data['product_demo'] = video

      serializer = ProductSerializer(product, data=updated_data, partial=True)

      if serializer.is_valid():
         
         product = serializer.save()

         return JsonResponse({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': str(product.price),
            'stock': product.stock,
            'image_url': product.product_image.url if product.product_image else None,
            'video_url': product.product_demo.url if product.product_demo else None,
        }, status=status.HTTP_200_OK)
      else:
         
         return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Pour la méthode 'update' (Update: Mettre à jour un produit)
    def update(self, request, *args, **kwargs):
        product = self.get_object()  # Récupérer l'objet produit
        serializer = self.get_serializer(product, data=request.data, partial=False)  # Sérialiser avec les nouvelles données
        if serializer.is_valid():
            product = serializer.save()  # Sauvegarder les modifications
            return Response(serializer.data)  # Retourner la réponse avec le produit mis à jour
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Pour la méthode 'partial_update' (Update partiel: Mettre à jour certains champs du produit)
    def partial_update(self, request, *args, **kwargs):
        product = self.get_object()  # Récupérer l'objet produit
        serializer = self.get_serializer(product, data=request.data, partial=True)  # Sérialiser avec les nouvelles données
        if serializer.is_valid():
            product = serializer.save()  # Sauvegarder les modifications
            return Response(serializer.data)  # Retourner la réponse avec le produit partiellement mis à jour
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Pour la méthode 'destroy' (Delete: Supprimer un produit)
    def destroy(self, request, *args, **kwargs):
        product = self.get_object()  # Récupérer l'objet produit
        product.delete()  # Supprimer l'objet produit
        return Response(status=status.HTTP_204_NO_CONTENT)  # Retourner une réponse vide avec le code 204
    
    # Méthode pour récupérer les reviews d'un produit spécifique
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        product = self.get_object()
        reviews = Review.objects.filter(product=product)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Méthode pour créer une review pour un produit spécifique
    @action(detail=True, methods=['post'])
    def add_review(self, request, pk=None):
        product = self.get_object()
        data = request.data.copy()
        data['product'] = product.id  # Associer l'ID du produit à la review
        serializer = ReviewSerializer(data=data)

        if serializer.is_valid():
            serializer.save(reviewer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # Méthode pour récupérer les commandes effectuées par un utilisateur
    @action(detail=False, methods=['get'], url_path='user_orders')
    def get_user_orders(self, request):
        user = request.user  # Récupérer l'utilisateur connecté
        orders = Order.objects.filter(author=user)  # Filtrer les commandes de l'utilisateur

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


     
    
    #pour générer une commande à partir du panier et envoyer des emails au clients et vendeurs
    @action(detail=False, methods=['post'])
    def create_order(self, request):
        user = request.user
        cart_items = CartItem.objects.filter(user=user)

        if not cart_items.exists():
            return Response({"error": "Votre panier est vide."}, status=status.HTTP_400_BAD_REQUEST)

        shop_orders = {}

        for item in cart_items:
            shop = item.product.shop
            if shop not in shop_orders:
                shop_orders[shop] = []
            shop_orders[shop].append(item)

        order_list = []
        for shop, items in shop_orders.items():
            total_amount = sum(item.product.price * item.quantity for item in items)

            order = Order.objects.create(
                author=user,
                shop=shop,
                total_amount=total_amount,
                status='pending'
            )

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            order_list.append(order)

            # Supprimer les éléments du panier après la commande
            cart_items.filter(product__shop=shop).delete()

            # 📧 Envoi d'email au vendeur
            send_mail(
                subject=f"Nouvelle commande #{order.id}",
                message=f"Bonjour {shop.owner.username},\n\n"
                        f"Vous avez reçu une nouvelle commande sur votre boutique {shop.name}.\n"
                        f"Total: {order.total_amount} FCFA\n\n"
                        f"Connectez-vous pour voir les détails.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[shop.owner.email],
                fail_silently=False,
            )

        # 📧 Envoi d'email au client
        send_mail(
            subject="Votre commande a été enregistrée",
            message=f"Bonjour {user.username},\n\n"
                    f"Votre commande a bien été enregistrée.\n"
                    f"Vous serez notifié dès qu'elle sera confirmée.\n"
                    f"Merci pour votre confiance !",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({"message": "Commande créée avec succès.", "orders": [o.id for o in order_list]}, status=status.HTTP_201_CREATED)
     
     #############################################"
     # ###############################################""
    # Vue pour annuler une commande 

    @action(detail=True, methods=['post'])
    def cancel_order(self, request, pk=None):
        user = request.user
        try:
            order = Order.objects.get(pk=pk, author=user)
        except Order.DoesNotExist:
            return Response({"error": "Commande non trouvée ou vous n'avez pas l'autorisation."},
                            status=status.HTTP_404_NOT_FOUND)

        if order.status in ['canceled', 'shipped', 'delivered']:
            return Response({"message": "Cette commande ne peut pas être annulée."},
                            status=status.HTTP_400_BAD_REQUEST)

        order.status = 'canceled'
        order.save()

        # 📧 Envoi d'e-mail au vendeur
        if order.shop:
            send_mail(
                subject=f"Commande #{order.id} annulée",
                message=f"Bonjour {order.shop.owner.username},\n\n"
                        f"La commande #{order.id} de {user.username} a été annulée.\n"
                        f"Connectez-vous à votre compte pour voir les détails.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.shop.owner.email],
                fail_silently=False,
            )

        # 📧 Envoi d'e-mail au client
        send_mail(
            subject="Votre commande a été annulée",
            message=f"Bonjour {user.username},\n\n"
                    f"Votre commande #{order.id} a été annulée avec succès.\n"
                    f"Merci pour votre compréhension.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({"message": "Commande annulée avec succès."}, status=status.HTTP_200_OK)
    
    #############################################
    ############################################
    # Vue pour relancer une commande
    
    @action(detail=True, methods=['post'])
    def relaunch_order(self, request, pk=None):
        user = request.user
        try:
            order = Order.objects.get(pk=pk, author=user)
        except Order.DoesNotExist:
            return Response({"error": "Commande non trouvée ou vous n'avez pas l'autorisation."},
                            status=status.HTTP_404_NOT_FOUND)

        if order.status == 'delivered':
            return Response({"message": "Seules les commandes non livrées peuvent être relancées."},
                            status=status.HTTP_400_BAD_REQUEST)

        order.status = 'pending'
        order.save()

        # 📧 Envoi d'e-mail au vendeur
        if order.shop:
            send_mail(
                subject=f"Commande #{order.id} relancée",
                message=f"Bonjour {order.shop.owner.username},\n\n"
                        f"La commande #{order.id} de {user.username} a été relancée et est en attente de confirmation.\n"
                        f"Connectez-vous pour traiter la commande.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.shop.owner.email],
                fail_silently=False,
            )

        # 📧 Envoi d'e-mail au client
        send_mail(
            subject="Votre commande a été relancée",
            message=f"Bonjour {user.username},\n\n"
                    f"Votre commande #{order.id} a été relancée avec succès.\n"
                    f"Vous recevrez une notification dès qu'elle sera confirmée.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({"message": "Commande relancée avec succès."}, status=status.HTTP_200_OK)



    def perform_create(self, serializer):
        serializer.save(author=self.request.user)  # Spécifier l'auteur (utilisateur).

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save()  # Pas besoin de spécifier l'auteur ici pour `Order`.

    def destroy(self, request, *args, **kwargs):
        order = self.get_object()
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    # méthode pour mettre à jour le statut d'une commande
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')

        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({'error': 'Statut invalide'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()

        # 📧 Envoi d'email au client si la commande est confirmée ou expédiée
        if new_status in ['confirmed', 'shipped', 'delivered']:
            send_mail(
                subject=f"Commande #{order.id} - {dict(Order.STATUS_CHOICES)[new_status]}",
                message=f"Bonjour {order.author.username},\n\n"
                        f"Le statut de votre commande #{order.id} a été mis à jour : {dict(Order.STATUS_CHOICES)[new_status]}.\n"
                        f"Merci de suivre l'évolution de votre commande depuis votre compte.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.author.email],
                fail_silently=False,
            )

        return Response({'message': f'Statut mis à jour : {new_status}'}, status=status.HTTP_200_OK)


class OrderItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

    def create(self, request, *args, **kwargs):
        serializer = OrderItemSerializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()  # Pas besoin de spécifier l'auteur ici pour `OrderItem`.

    def update(self, request, *args, **kwargs):
        order_item = self.get_object()
        serializer = OrderItemSerializer(order_item, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save()  # Pas besoin de spécifier l'auteur ici pour `OrderItem`.

    def destroy(self, request, *args, **kwargs):
        order_item = self.get_object()
        order_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def create(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id')  # Récupère l'ID du produit depuis l'URL
        if not product_id:
            return Response({"detail": "L'ID du produit est requis."}, status=status.HTTP_400_BAD_REQUEST)

        # Ajoute l'ID du produit aux données de la requête
        data = request.data.copy()
        data['product'] = product_id

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)

    @action(detail=False, methods=['get'], url_path='product/(?P<product_id>[^/.]+)')
    def reviews_for_product(self, request, product_id=None):
        reviews = self.queryset.filter(product_id=product_id)
        if not reviews.exists():
            return Response({"detail": "Aucun avis trouvé pour ce produit."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    parser_classes = [MultiPartParser, FormParser]

    # Action personnalisée pour créer un produit dans une boutique donnée
    @action(detail=True, methods=['post'])
    def create_product(self, request, pk=None):
        # Récupérer l'objet Shop à partir de l'ID de la boutique (pk)
        try:
            shop = Shop.objects.get(id=pk)
        except Shop.DoesNotExist:
            return JsonResponse({'error': 'Boutique non trouvée'}, status=status.HTTP_404_NOT_FOUND)

        # Récupérer les données du produit envoyées dans la requête
        name = request.data.get('name')
        description = request.data.get('description')
        category_id = request.data.get('category_id')
        price = request.data.get('price')
        stock = request.data.get('stock')

        # Récupérer les fichiers téléchargés (image et vidéo)
        image = request.FILES.get('product_image')
        video = request.FILES.get('product_demo')

        # Créer un dictionnaire de données pour le sérialiseur du produit
        data = {
            'name': name,
            'description': description,  
            'price': price,
            'stock': stock,
            'product_image': image,
            'product_demo': video,
            'shop_id': shop.id,
            'category_id': category_id
        }

        # Sérialiser les données du produit
        serializer = ProductSerializer(data=data)

        if serializer.is_valid():
            # Sauvegarder le produit dans la base de données
            product = serializer.save(shop=shop)  # Associer le produit à la boutique spécifiée

            # Retourner une réponse avec les détails du produit créé
            return JsonResponse({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': str(product.price),
                'stock': product.stock,
                'image_url': product.product_image.url if product.product_image else None,
                'video_url': product.product_demo.url if product.product_demo else None,
            }, status=status.HTTP_201_CREATED)
        else:
            # Retourner une erreur si les données sont invalides
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
from rest_framework.views import APIView


class ShopCategoriesView(APIView):

    """
    Vue pour afficher les catégories de produits dans une boutique spécifique.
    """
    permission_classes = [AllowAny]
    def get(self, request, shop_id, *args, **kwargs):
        try:
            shop = Shop.objects.get(id=shop_id)
            products = Product.objects.filter(shop=shop)
            categories = Category.objects.filter(id__in=products.values_list('category', flat=True)).distinct()
            
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Shop.DoesNotExist:
            return Response({"error": "Boutique non trouvée"}, status=status.HTTP_404_NOT_FOUND)
        




from rest_framework import generics, filters, permissions

# 5. Afficher les boutiques associées à un utilisateur
class UserShopsAPIView(generics.ListAPIView):
    serializer_class = ShopSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Shop.objects.filter(owner_id=user_id)



class ProductsByCategoryAPIView(generics.ListAPIView):
    """
    API pour récupérer tous les produits dans une catégorie donnée.
    """
    serializer_class = ProductSerializer

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Product.objects.filter(category_id=category_id)


class ShopProductsByCategoryAPIView(generics.ListAPIView):
    """
    API pour récupérer tous les produits dans une catégorie donnée.
    """
    serializer_class = ProductSerializer

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        shop_id=self.kwargs['shop_id']
        return Product.objects.filter(shop_id=shop_id, category_id=category_id )



" Vue pour liker un produit "
class ToggleLikeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            user = request.user  # Assurez-vous que l'utilisateur est authentifié

            # Vérifier si le like existe déjà
            like, created = Like.objects.get_or_create(user=user, product=product)
            
            if not created:
                # Si le like existe déjà, le supprimer
                like.delete()
                return Response({"message": "Like removed."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Like added."}, status=status.HTTP_201_CREATED)
        
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)



# Logique qui recupere le nombre de like sur un produit 

class ProductLikesView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)  # Récupérer le produit
            like_count = Like.objects.filter(product=product).count()  # Compter les likes pour ce produit
            
            return Response({
                "product_id": product.id,
                "product_name": product.name,
                "like_count": like_count
            }, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({
                "error": "Product not found."
            }, status=status.HTTP_404_NOT_FOUND)


# Vue pour gérer les articles du panier

class CartItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # Ajouter ou mettre à jour un article dans le panier
    def post(self, request):
        user = request.user
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            return Response({"error": "Le champ 'product' est requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Le produit n'existe pas."}, status=status.HTTP_404_NOT_FOUND)

        # Vérifier si l'article existe déjà dans le panier
        cart_item, created = CartItem.objects.get_or_create(user=user, product=product)

        if not created:
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity = int(quantity)

        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Supprimer un article du panier
    def delete(self, request, product_id):
        user = request.user

        try:
            cart_item = CartItem.objects.get(user=user, product_id=product_id)
            cart_item.delete()
            return Response({"message": "Article supprimé du panier avec succès."}, status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({"error": "Cet article n'est pas dans votre panier."}, status=status.HTTP_404_NOT_FOUND)


class ResetCartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        CartItem.objects.filter(user=user).delete()
        return Response({"message": "Panier réinitialisé avec succès."}, status=status.HTTP_200_OK)





class CartItemListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        cart_items = CartItem.objects.filter(user=user)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

###########################################################################
##############   VUES POUR LES DASHBOARDS #################################


from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Report
from .serializers import ReportSerializer
from django.contrib.contenttypes.models import ContentType

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

    def create(self, request, *args, **kwargs):
        """
        Crée un nouveau rapport.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        """
        Enregistrement personnalisé pour créer le rapport.
        """
        serializer.save()

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """
        Récupère les rapports filtrés par type.
        """
        report_type = request.query_params.get('type')
        if not report_type:
            return Response({"error": "Le paramètre 'type' est requis."}, status=status.HTTP_400_BAD_REQUEST)
        
        reports = Report.objects.filter(report_type=report_type)
        serializer = self.get_serializer(reports, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def related_to(self, request):
        """
        Récupère les rapports liés à un objet spécifique.
        """
        related_object_type = request.query_params.get('related_object_type')
        related_object_id = request.query_params.get('related_object_id')

        if not related_object_type or not related_object_id:
            return Response(
                {"error": "Les paramètres 'related_object_type' et 'related_object_id' sont requis."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            content_type = ContentType.objects.get(model=related_object_type)
            reports = Report.objects.filter(
                related_object_type=content_type,
                related_object_id=related_object_id
            )
            serializer = self.get_serializer(reports, many=True)
            return Response(serializer.data)
        except ContentType.DoesNotExist:
            return Response({"error": "Type d'objet lié invalide."}, status=status.HTTP_400_BAD_REQUEST)
#///////////////////////////////////////////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////////////////////////////////////
#//////////////////// Vues pour les rapports des boutiques ////////////////////////////////////////////

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from .models import Shop, Product, Like

class MostLikedProductInShopView(APIView):
    """
    Retourne le produit le plus aimé dans une boutique spécifique.
    """
    def get(self, request, shop_id):
        try:
            shop = Shop.objects.get(id=shop_id)
            most_liked_product = (
                Product.objects.filter(shop=shop)
                .annotate(like_count=Count('likes'))
                .order_by('-like_count')
                .first()
            )
            if not most_liked_product:
                return Response({"message": "Aucun produit trouvé pour cette boutique."}, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                "product_id": most_liked_product.id,
                "product_name": most_liked_product.name,
                "like_count": most_liked_product.like_count
            }, status=status.HTTP_200_OK)
        except Shop.DoesNotExist:
            return Response({"error": "Boutique introuvable."}, status=status.HTTP_404_NOT_FOUND)


from .models import Order, OrderItem

class ShopStatisticsView(APIView):
    """
    Retourne les statistiques globales d'une boutique.
    """
    def get(self, request, shop_id):
        try:
            shop = Shop.objects.get(id=shop_id)
            
            # Récupération des statistiques
            total_products = Product.objects.filter(shop=shop).count()
            total_likes = Like.objects.filter(product__shop=shop).count()
            total_orders = OrderItem.objects.filter(product__shop=shop).count()
            
            return Response({
                "shop_id": shop.id,
                "shop_name": shop.name,
                "total_products": total_products,
                "total_likes": total_likes,
                "total_orders": total_orders
            }, status=status.HTTP_200_OK)
        except Shop.DoesNotExist:
            return Response({"error": "Boutique introuvable."}, status=status.HTTP_404_NOT_FOUND)

class MostSoldProductsInShopView(APIView):
    """
    Retourne les produits les plus vendus dans une boutique.
    """
    def get(self, request, shop_id):
        try:
            shop = Shop.objects.get(id=shop_id)
            most_sold_products = (
                Product.objects.filter(shop=shop)
                .annotate(sales_count=Count('orderitem'))
                .order_by('-sales_count')[:5]
            )
            
            data = [
                {
                    "product_id": product.id,
                    "product_name": product.name,
                    "sales_count": product.sales_count
                }
                for product in most_sold_products
            ]
            
            return Response(data, status=status.HTTP_200_OK)
        except Shop.DoesNotExist:
            return Response({"error": "Boutique introuvable."}, status=status.HTTP_404_NOT_FOUND)


from django.db.models import Sum, F


class ShopRevenueView(APIView):
    """
    Retourne les revenus totaux générés par une boutique.
    """
    def get(self, request, shop_id):
        try:
            shop = Shop.objects.get(id=shop_id)
            total_revenue = (
                OrderItem.objects.filter(product__shop=shop)
                .aggregate(total_revenue=Sum(F('price') * F('quantity')))['total_revenue'] or 0
            )
            
            return Response({
                "shop_id": shop.id,
                "shop_name": shop.name,
                "total_revenue": total_revenue
            }, status=status.HTTP_200_OK)
        except Shop.DoesNotExist:
            return Response({"error": "Boutique introuvable."}, status=status.HTTP_404_NOT_FOUND)



from django.db.models import Avg

class AverageProductRatingInShopView(APIView):
    """
    Retourne la note moyenne des produits d'une boutique.
    """
    def get(self, request, shop_id):
        try:
            shop = Shop.objects.get(id=shop_id)
            average_rating = (
                Review.objects.filter(product__shop=shop)
                .aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
            )
            
            return Response({
                "shop_id": shop.id,
                "shop_name": shop.name,
                "average_rating": round(average_rating, 2)
            }, status=status.HTTP_200_OK)
        except Shop.DoesNotExist:
            return Response({"error": "Boutique introuvable."}, status=status.HTTP_404_NOT_FOUND)



class LowStockProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, shop_id):
        products = Product.objects.filter(shop_id=shop_id, stock__lte=5).values('id', 'name', 'stock')
        return Response({"low_stock_products": list(products)}, status=status.HTTP_200_OK)


from .models import Order

class IncompleteOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, shop_id):
        incomplete_orders = (
            Order.objects.filter(
                items__product__shop_id=shop_id, status__in=['pending', 'cancelled']
            )
            .distinct()
            .values('id', 'author__username', 'status', 'created_at')
        )
        return Response({"incomplete_orders": list(incomplete_orders)}, status=status.HTTP_200_OK)


from django.db.models import Sum

class ProductsByCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, shop_id):
        products_by_category = (
            Product.objects.filter(shop_id=shop_id)
            .values('category__name')
            .annotate(total_sales=Sum('orderitem__quantity'))
            .order_by('-total_sales')
        )
        return Response({"products_by_category": list(products_by_category)}, status=status.HTTP_200_OK)


class TopCustomersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, shop_id):
        top_customers = (
            OrderItem.objects.filter(product__shop_id=shop_id)
            .values('order__author__username')
            .annotate(total_spent=Sum(F('price') * F('quantity')))
            .order_by('-total_spent')[:5]
        )
        return Response({"top_customers": list(top_customers)}, status=status.HTTP_200_OK)
