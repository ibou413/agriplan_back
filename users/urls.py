# userapp/urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView, TokenBlacklistView
#from django_rest_passwordreset.views import ResetPasswordRequestToken, ResetPasswordConfirm
from .views import RegisterView, LoginView, UserListView, UserProfileView,PartialUpdateUserProfileView
from . import views
from .views import RegisterAndBindDeviceView, AutoLoginView
urlpatterns = [
    # JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('logout/', TokenBlacklistView.as_view(), name='token_blacklist'),

    # Inscription, Connexion, Profil


    path('register-with-device/', RegisterAndBindDeviceView.as_view(), name='register-device'),
    
    path('auto-login/', AutoLoginView.as_view(), name='auto-login'),

    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/update/', PartialUpdateUserProfileView.as_view(), name='user-profile-update'),
    path('users/', UserListView.as_view(), name='user_list'),

    # Réinitialisation du mot de passe
    #path('password_reset/', ResetPasswordRequestToken.as_view(), name='password_reset'),
    #path('password_reset/confirm/', ResetPasswordConfirm.as_view(), name='password_reset_confirm'),
    path('password_reset/', views.password_reset_request, name='reset-password-request'),
    path('password_reset/confirm/<str:token>/', views.password_reset, name='reset-password-confirm'),
]
