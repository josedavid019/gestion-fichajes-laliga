from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Profile, AuditLog
import random
import string


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "is_active", "date_joined")
        read_only_fields = ("id", "date_joined")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password", "password_confirm")

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                {"password": "Las contraseñas no coinciden."}
            )
        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError(
                {"email": "Este email ya está registrado."}
            )
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        # Generate unique username from email
        email = validated_data["email"]
        base_username = email.split("@")[0].replace(".", "").replace("+", "")
        username = base_username

        # If username already exists, append random numbers
        while User.objects.filter(username=username).exists():
            random_suffix = "".join(random.choices(string.digits, k=3))
            username = f"{base_username}{random_suffix}"

        validated_data["username"] = username
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("Email o contraseña incorrectos.")

        if not user.check_password(data["password"]):
            raise serializers.ValidationError("Email o contraseña incorrectos.")

        if not user.is_active:
            raise serializers.ValidationError("Usuario inactivo.")

        self.context["user"] = user
        return data


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "user", "avatar", "phone", "bio", "created_at", "updated_at")
        read_only_fields = ("id", "user", "created_at", "updated_at")


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = AuditLog
        fields = (
            "id",
            "user",
            "user_email",
            "user_username",
            "action",
            "entity",
            "entity_id",
            "old_data",
            "new_data",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
