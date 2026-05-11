from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = "Crea usuarios de prueba para desarrollo"

    def handle(self, *args, **options):
        test_users = [
            {
                "email": "admin@example.com",
                "first_name": "Admin",
                "last_name": "User",
                "password": "admin123",
                "is_staff": True,
                "is_superuser": True,
            },
            {
                "email": "scout@example.com",
                "first_name": "Scout",
                "last_name": "Pro",
                "password": "scout123",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "email": "director@example.com",
                "first_name": "Director",
                "last_name": "General",
                "password": "director123",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "email": "juan.perez@example.com",
                "first_name": "Juan",
                "last_name": "Pérez",
                "password": "password123",
                "is_staff": False,
                "is_superuser": False,
            },
        ]

        created_count = 0
        for user_data in test_users:
            email = user_data.pop("email")
            password = user_data.pop("password")

            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    email=email, password=password, **user_data
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Usuario creado: {email} (contraseña: {password})"
                    )
                )
                created_count += 1
            else:
                self.stdout.write(self.style.WARNING(f"⚠ Usuario ya existe: {email}"))

        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Total usuarios creados: {created_count}")
        )
        self.stdout.write(
            self.style.SUCCESS("\n📝 Credenciales disponibles para login:")
        )
        self.stdout.write("─" * 50)

        # Display credentials
        test_credentials = [
            ("admin@example.com", "admin123"),
            ("scout@example.com", "scout123"),
            ("director@example.com", "director123"),
            ("juan.perez@example.com", "password123"),
        ]

        for email, password in test_credentials:
            self.stdout.write(f"  📧 Email: {email}")
            self.stdout.write(f"  🔑 Contraseña: {password}")
            self.stdout.write("─" * 50)
