from environs import Env
from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from accounts.serializers import RegisterSerializer, LoginSerializer


env = Env()
User = get_user_model()


class LoginViewSet(ModelViewSet, TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RegistrationViewSet(ModelViewSet):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.last_login = timezone.now()
        user.save()

        # Generate the activation token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Construct the frontend activation URL
        frontend_base_url = env('FRONTEND_BASE_URL')
        activation_route = env('ACCOUNT_ACTIVATION_ROUTE')
        activation_url = f"{frontend_base_url}/{activation_route}?uid={uid}&token={token}"

        # Render the email message
        html_message = render_to_string('acc_activation_email.html', {
            'user': user,
            'activation_url': activation_url,
        })

        # Create the email message
        email_message = EmailMultiAlternatives(
            "Activate Account",
            "Please use the link below to activate your account.",
            settings.EMAIL_HOST_USER,
            [user.email],
        )

        # Send the email
        email_message.attach_alternative(html_message, "text/html")
        email_message.send()

        # Return the response
        return Response({
            'message': f'Verification email has been sent. UID = {uid}, Token = {token}',
            'email': user.email,
            "user": serializer.data,
        }, status=status.HTTP_201_CREATED)


class VerifyAccountView(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    def retrieve(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            # Check if the token has expired
            if timezone.now() > user.last_login + timedelta(hours=24):
                return Response({'message': 'Activation link has expired!'}, status=status.HTTP_400_BAD_REQUEST)

            if not user.is_active:
                user.is_active = True
                user.is_staff = True if user.role == "admin" else False

                user.save()

                return Response({'message': 'Your account has been activated.'}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Your account is activated!"})
        return Response({'message': 'Activation link is invalid!'}, status=status.HTTP_400_BAD_REQUEST)


class RefreshViewSet(viewsets.ViewSet, TokenRefreshView):
    permission_classes = (AllowAny,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def get(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        # Blacklist the refresh token
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                print(f"Error blacklisting token: {e}")

        response = Response(status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        return response


class DeactivateAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=request.user.pk)
        user.is_active = False
        user.save()
        return Response({"message": "Account deactivated successfully."}, status=status.HTTP_200_OK)
