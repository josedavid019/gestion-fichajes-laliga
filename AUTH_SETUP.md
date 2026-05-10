# Guía de ejecución - Login y Register

## Backend (Django)

### 1. Configurar variables de entorno
Asegúrate de que exista un archivo `.env` en la raíz del proyecto con la configuración necesaria.

### 2. Instalar dependencias
```bash
cd backend
pip install -r requirements.txt
```

### 3. Ejecutar migraciones
```bash
python manage.py migrate
```

### 4. Crear superusuario (opcional, para acceder al admin)
```bash
python manage.py createsuperuser
```

### 5. Iniciar servidor Django
```bash
python manage.py runserver 0.0.0.0:8000
```

El servidor estará disponible en: http://localhost:8000

## Frontend (React + Vite)

### 1. Instalar dependencias
```bash
cd frontend
npm install
# o
bun install
```

### 2. Iniciar servidor de desarrollo
```bash
npm run dev
# o
bun run dev
```

El frontend estará disponible en: http://localhost:5173

## Flujo de autenticación

### Registro
1. Accede a http://localhost:5173/register
2. Completa el formulario con:
   - Email
   - Nombre
   - Apellido
   - Contraseña (mínimo 6 caracteres)
   - Confirmación de contraseña

### Login
1. Accede a http://localhost:5173/login
2. Ingresa tu email y contraseña
3. Serás redirigido al dashboard

### Logout
1. Haz clic en tu avatar/inicial en la esquina superior derecha
2. Selecciona "Cerrar sesión"
3. Serás redirigido al login

## Endpoints de API disponibles

- `POST /api/auth/register/` - Registrar nuevo usuario
- `POST /api/auth/login/` - Iniciar sesión
- `POST /api/auth/logout/` - Cerrar sesión
- `GET /api/auth/me/` - Obtener usuario actual (requiere autenticación)
- `GET /api/auth/check-auth/` - Verificar si el usuario está autenticado

## Características implementadas

✅ Registro de usuarios con validación
✅ Login con sesiones
✅ Logout seguro
✅ Protección de rutas
✅ Menú de usuario con avatar
✅ Manejo de errores
✅ Mensajes de notificación (toast)
✅ Autenticación persistente
