from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Profile, AuditLog, Role, UserRole
import random
import string


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "username", "created_at", "updated_at")


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


class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer para crear y actualizar usuarios desde admin."""

    password = serializers.CharField(write_only=True, required=False, min_length=6)
    role = serializers.ChoiceField(choices=Role.ROLES, required=False)
    phone = serializers.CharField(
        source="profile.phone", required=False, allow_blank=True
    )
    bio = serializers.CharField(source="profile.bio", required=False, allow_blank=True)
    avatar = serializers.ImageField(
        source="profile.avatar", required=False, allow_null=True
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["role"] = self.get_role(instance)
        return data

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
            "is_active",
            "is_staff",
            "is_superuser",
            "role",
            "phone",
            "bio",
            "avatar",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_role(self, obj):
        """Get the role name from UserRole relationship."""
        user_role = obj.user_roles.first()
        return user_role.role.name if user_role else None

    def create(self, validated_data):
        # Extract profile and role data
        profile_data = validated_data.pop("profile", {})
        role_name = validated_data.pop("role", None)
        password = validated_data.pop("password", None)

        # Create user
        user = User.objects.create(**validated_data)

        if password:
            user.set_password(password)
        else:
            # Generar contraseña temporal si no se proporciona
            temp_password = "".join(
                random.choices(string.ascii_letters + string.digits, k=12)
            )
            user.set_password(temp_password)
        user.save()

        # Create profile
        Profile.objects.create(user=user, **profile_data)

        # Assign role if provided
        if role_name:
            role, created = Role.objects.get_or_create(name=role_name)
            UserRole.objects.create(user=user, role=role)

        return user

    def update(self, instance, validated_data):
        # Extract profile and role data
        profile_data = validated_data.pop("profile", {})
        role_name = validated_data.pop("role", None)
        password = validated_data.pop("password", None)

        # Update user
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        instance.save()

        # Update or create profile
        profile, created = Profile.objects.get_or_create(user=instance)
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        # Update role if provided
        if role_name is not None:
            # Remove existing roles
            UserRole.objects.filter(user=instance).delete()
            if role_name:
                role, created = Role.objects.get_or_create(name=role_name)
                UserRole.objects.create(user=instance, role=role)

        return instance


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("id", "name", "description", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")
