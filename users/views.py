# userapp/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserRegistrationSerializer, UserSerializer
from rest_framework.permissions import AllowAny
from rest_framework.generics import ListAPIView
from django.contrib.auth import get_user_model
from . models import CustomUser
from fcm_django.models import FCMDevice


User = CustomUser

class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


# Inscription
class RegisterView(APIView):
    permission_classes = [AllowAny]  # Permet à tout le monde d'accéder à cette vue sans authentification

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "Utilisateur créé avec succès."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# views.py

class RegisterAndBindDeviceView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        device_token = request.data.get('device_token')

        if serializer.is_valid():
            user = serializer.save()

            # Associer le device
            if device_token:
                FCMDevice.objects.update_or_create(
                    registration_id=device_token,
                    defaults={'user': user, 'type': 'android'},  # ou 'ios'
                )

            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Utilisateur enregistré",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Connexion
class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        return Response({"error": "Identifiants invalides."}, status=status.HTTP_401_UNAUTHORIZED)

# views.py



class AutoLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        device_token = request.data.get('device_token')
        if not device_token:
            return Response({"error": "Device token requis"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Récupérer le device
            device = FCMDevice.objects.get(registration_id=device_token)
            user = device.user
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                })
            else:
                return Response({"error": "Aucun utilisateur associé à ce device"}, status=status.HTTP_404_NOT_FOUND)

        except FCMDevice.DoesNotExist:
            return Response({"error": "Device non enregistré"}, status=status.HTTP_404_NOT_FOUND)



# userapp/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from django.conf import settings

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Récupère les informations de l'utilisateur connecté.
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)




from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import UserSerializer

class PartialUpdateUserProfileView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        # On associe l'utilisateur connecté à son profil
        user_profile = self.request.user

        # Utilisation du serializer pour la mise à jour partielle
        serializer = self.get_serializer(
            user_profile, data=request.data, partial=True
        )

        # Vérification de la validité des données
        if serializer.is_valid():
            # Sauvegarde les données mises à jour
            serializer.save()

            # Retourne les données mises à jour, y compris l'URL de l'image de profil
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Retourne les erreurs de validation si la mise à jour échoue
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django.conf import settings

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """Demande de réinitialisation du mot de passe en envoyant un lien avec un token JWT."""
    
    email = request.data.get('email')
    if not email:
        return Response({"detail": "L'email est obligatoire"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = CustomUser.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"detail": "Aucun utilisateur trouvé avec cet email."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Créer un token JWT
    refresh = RefreshToken.for_user(user)
    reset_token = str(refresh.access_token)

    # Envoi du lien de réinitialisation par email (vous pouvez personnaliser l'email)
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    
    # Personnalisez l'email avec votre template
    send_mail(
        'Réinitialisation de votre mot de passe',
        f'Cliquez sur ce lien pour réinitialiser votre mot de passe : {reset_link}',
        'noreply@sukelagri.com',
        [email],
        fail_silently=False,
    )

    return Response({"detail": "Un email de réinitialisation a été envoyé."}, status=status.HTTP_200_OK)




from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.password_validation import validate_password

@api_view(['POST'])
def password_reset(request):
    """Réinitialisation du mot de passe avec un token JWT."""
    
    token = request.data.get('token')
    new_password = request.data.get('new_password')
    
    if not token or not new_password:
        return Response({"detail": "Token et nouveau mot de passe sont obligatoires."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Décoder le token JWT
        access_token = AccessToken(token)
        user_id = access_token['user_id']
        
        # Récupérer l'utilisateur à partir de l'ID
        user = CustomUser.objects.get(id=user_id)
        
        # Valider le mot de passe
        validate_password(new_password, user)
        
        # Mettre à jour le mot de passe
        user.set_password(new_password)
        user.save()

        # Optionnel : Actualiser la session après le changement de mot de passe
        update_session_auth_hash(request, user)
        
        return Response({"detail": "Mot de passe réinitialisé avec succès."}, status=status.HTTP_200_OK)
    
    except AccessToken.Error:
        return Response({"detail": "Token invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({"detail": "Utilisateur non trouvé."}, status=status.HTTP_400_BAD_REQUEST)
