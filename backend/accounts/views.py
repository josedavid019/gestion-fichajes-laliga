from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    ProfileSerializer,
    AuditLogSerializer,
)
from .models import User, Profile, AuditLog


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """Registrar nuevo usuario."""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        login(request, user)
        return Response(
            {
                "message": "Usuario registrado exitosamente",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """Autenticar usuario."""
    serializer = LoginSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        user = serializer.context["user"]
        login(request, user)
        return Response(
            {
                "message": "Autenticación exitosa",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Cerrar sesión del usuario."""
    logout(request)
    return Response(
        {"message": "Sesión cerrada exitosamente"},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Obtener información del usuario actual."""
    return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def check_auth(request):
    """Verificar si el usuario está autenticado."""
    if request.user.is_authenticated:
        return Response(
            {"authenticated": True, "user": UserSerializer(request.user).data},
            status=status.HTTP_200_OK,
        )
    return Response(
        {"authenticated": False},
        status=status.HTTP_200_OK,
    )


@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def profile_detail(request):
    """Obtener o actualizar el perfil del usuario actual."""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        # Crear perfil si no existe
        profile = Profile.objects.create(user=request.user)

    if request.method == "GET":
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method in ["PUT", "PATCH"]:
        serializer = ProfileSerializer(
            profile, data=request.data, partial=request.method == "PATCH"
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def audit_logs(request):
    """Obtener logs de auditoría. Solo para administradores."""
    if not request.user.is_staff:
        return Response(
            {"error": "No tienes permisos para ver los logs de auditoría"},
            status=status.HTTP_403_FORBIDDEN,
        )

    logs = AuditLog.objects.all().order_by("-created_at")

    # Filtros opcionales
    user_id = request.query_params.get("user_id")
    action = request.query_params.get("action")
    entity = request.query_params.get("entity")

    if user_id:
        logs = logs.filter(user_id=user_id)
    if action:
        logs = logs.filter(action=action)
    if entity:
        logs = logs.filter(entity=entity)

    serializer = AuditLogSerializer(logs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
