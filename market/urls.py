from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ResetCartAPIView, ReviewViewSet,CategoryViewSet, OrderItemViewSet, OrderViewSet,ShopViewSet, ShopCategoriesView
from .views import UserShopsAPIView, ProductsByCategoryAPIView
from .views import  CartItemAPIView
from .views import    ReportViewSet, ProductLikesView,ToggleLikeView, CartItemListAPIView
from .views import (
    MostLikedProductInShopView,
    ShopStatisticsView,
    MostSoldProductsInShopView,
    ShopRevenueView,
    AverageProductRatingInShopView,
    LowStockProductsView,
    IncompleteOrdersView,
    ProductsByCategoryView,
    TopCustomersView,
    ShopProductsByCategoryAPIView
    
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'shops', ShopViewSet)
router.register(r'reports', ReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('shops/<int:shop_id>/categories/', ShopCategoriesView.as_view(), name='shop_categories'),
   
    path('users/<int:user_id>/shops/', UserShopsAPIView.as_view(), name='user-shops'),
    path('categories/<int:category_id>/products/', ProductsByCategoryAPIView.as_view(), name='products-by-category'),
    path('categories/<int:shop_id>/shops/<category_id>/products/', ShopProductsByCategoryAPIView.as_view(), name='products-by-category'),
    path('products/<int:product_id>/toggle-like/', ToggleLikeView.as_view(), name='toggle-like'),
    path('products/<int:product_id>/likes/', ProductLikesView.as_view(), name='product-likes'),
    


    path('shop/<int:shop_id>/most-liked-product/', MostLikedProductInShopView.as_view(), name='most_liked_product'),
    path('shop/<int:shop_id>/statistics/', ShopStatisticsView.as_view(), name='shop_statistics'),
    path('shop/<int:shop_id>/most-sold-products/', MostSoldProductsInShopView.as_view(), name='most_sold_products'),
    path('shop/<int:shop_id>/revenue/', ShopRevenueView.as_view(), name='shop_revenue'),
    path('shop/<int:shop_id>/average-rating/', AverageProductRatingInShopView.as_view(), name='average_product_rating'),
    path('shop/<int:shop_id>/low-stock-products/', LowStockProductsView.as_view(), name='low-stock-products'),
    path('shop/<int:shop_id>/products-by-category/', ProductsByCategoryView.as_view(), name='products-by-category'),
    path('shop/<int:shop_id>/top-customers/', TopCustomersView.as_view(), name='top-customers'),
    path('shop/<int:shop_id>/incomplete-orders/', IncompleteOrdersView.as_view(), name='incomplete-orders'),


    # Routes pour le panier
    path('cart/', CartItemAPIView.as_view(), name='cart-item'),
    path('cart_user/', CartItemListAPIView.as_view(), name='cart-list'),
    path('cart/reset/', ResetCartAPIView.as_view(), name='reset_cart'),  # Réinitialiser le panier
    path('cart/<int:product_id>/', CartItemAPIView.as_view(), name='delete_cart_item'),  # Supprimer un produit

]






