from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    objects = UserManager()

    class Meta:
        db_table = "accounts_user"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Role(models.Model):
    ROLES = [
        ("admin", "Admin"),
        ("scout", "Scout"),
        ("analyst", "Analista"),
        ("legal", "Jurista"),
        ("director", "Directivo"),
    ]
    name = models.CharField(max_length=50, choices=ROLES, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "accounts_role"

    def __str__(self):
        return self.name


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role_users")
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_user_role"
        unique_together = ("user", "role")
