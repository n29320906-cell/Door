
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema

from .models import StoreProfile
from .serializers import (
    StoreProfileSerializer,
    LoginSerializer,
    RegisterSerializer,
)

User = get_user_model()


# REGISTRATION
@extend_schema(
    request=RegisterSerializer,
    responses={201: dict},
    summary="Регистрация",
    description="Создание нового пользователя и профиля магазина."
)
@api_view(["POST"])
def register(request):
    first_name = request.data.get("first_name", "").strip()
    last_name = request.data.get("last_name", "").strip()
    username = request.data.get("username", "").strip()
    email = request.data.get("email", "").strip()
    password = request.data.get("password", "")
    password2 = request.data.get("password2", "")

    if not all([
        first_name, last_name, username,
        email, password, password2
    ]):
        return Response(
            {"error": "Заполните все поля"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if password != password2:
        return Response(
            {"error": "Пароли не совпадают"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Это имя пользователя уже зарегистрировано"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email__iexact=email).exists():
        return Response(
            {"error": "Этот адрес электронной почты уже зарегистрирован"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        validate_password(password)
    except ValidationError as error:
        return Response(
            {"error": list(error.messages)},
            status=status.HTTP_400_BAD_REQUEST
        )

    with transaction.atomic():
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )

        StoreProfile.objects.create(
            user=user,
            manager_name=f"{first_name} {last_name}".strip()
        )

    return Response(
        {
            "message": "Регистрация успешно завершена",
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "email": user.email
            },
            "store_profile": {
                "store_name": "",
                "manager_name": f"{first_name} {last_name}".strip(),
                "phone": "",
                "city": "",
                "street": "",
                "house": ""
            }
        },
        status=status.HTTP_201_CREATED
    )


# LOGIN
@extend_schema(
    request=LoginSerializer,
    responses={200: dict},
    summary="Авторизация",
    description="Вход по имени пользователя и паролю."
)
@api_view(["POST"])
def login(request):
    username = request.data.get("username", "").strip()
    password = request.data.get("password", "")

    if not username or not password:
        return Response(
            {"error": "Введите имя пользователя и пароль"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(
        request,
        username=username,
        password=password
    )

    if user is None:
        return Response(
            {"error": "Неверное имя пользователя или пароль"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user)

    return Response({
        "message": "Авторизация прошла успешно",
        "user": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "email": user.email
        },
        "tokens": {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }
    })


# STORE PROFILE
class StoreProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get_profile(self, user):
        profile, created = StoreProfile.objects.get_or_create(
            user=user,
            defaults={
                "manager_name": (
                    f"{user.first_name} {user.last_name}".strip()
                )
            }
        )
        return profile

    # Получение профиля
    def get(self, request):
        profile = self.get_profile(request.user)

        serializer = StoreProfileSerializer(
            profile,
            context={"request": request}
        )

        return Response(serializer.data)

    # Изменение профиля
    def patch(self, request):
        profile = self.get_profile(request.user)

        serializer = StoreProfileSerializer(
            profile,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response({
                "message": "Данные магазина успешно сохранены",
                "store_profile": serializer.data
            })

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request):
        return self.patch(request)


# CHANGE PASSWORD
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get("old_password", "")
        new_password = request.data.get("new_password", "")

        if not old_password or not new_password:
            return Response(
                {"error": "Введите старый и новый пароль"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user

        if not user.check_password(old_password):
            return Response(
                {"error": "Старый пароль указан неверно"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_password(new_password, user=user)
        except ValidationError as error:
            return Response(
                {"error": list(error.messages)},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return Response({
            "message": (
                "Пароль успешно изменён. "
                "Войдите в систему с новым паролем."
            )
        })
