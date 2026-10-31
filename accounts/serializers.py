from rest_framework import serializers
from .models import StoreProfile


class StoreProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreProfile
        fields = [
            "store_name",
            "manager_name",
            "phone",
            "city",
            "street",
            "house",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False
    )
    from rest_framework import serializers

    class RegisterSerializer(serializers.Serializer):
        first_name = serializers.CharField(max_length=150)
        last_name = serializers.CharField(max_length=150)
        username = serializers.CharField(max_length=150)
        email = serializers.EmailField()
        password = serializers.CharField(write_only=True)
        password2 = serializers.CharField(write_only=True)
