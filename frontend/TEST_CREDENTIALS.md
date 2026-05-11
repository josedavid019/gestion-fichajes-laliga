# Credenciales de Prueba - Frontend Testing

## 📝 Usuarios de Prueba

Usa cualquiera de estos datos para iniciar sesión en el frontend **sin necesidad de tener el backend corriendo**:

| Email                    | Contraseña    | Rol             |
| ------------------------ | ------------- | --------------- |
| `admin@example.com`      | `admin123`    | Admin           |
| `scout@example.com`      | `scout123`    | Scout           |
| `director@example.com`   | `director123` | Director        |
| `juan.perez@example.com` | `password123` | Usuario Regular |

## ⚙️ Cómo Funciona

El sistema tiene un **modo de prueba automático** que:

1. ✅ **Intenta conectar con el backend primero** (si está corriendo)
2. 🔄 **Si el backend no está disponible**, automáticamente cambia a **modo mock**
3. 💾 **Guarda la sesión en localStorage** para que persista dentro de la sesión actual
4. ✨ **Funciona transparentemente** - no necesitas cambiar nada

## 🚀 Pasos

1. Abre la aplicación frontend
2. Ve a la página de Login
3. Ingresa cualquiera de las credenciales de arriba
4. ¡Listo! Acceso instantáneo sin backend

## 📦 Archivos Modificados

- `src/lib/mockUsers.ts` - Datos de usuarios de prueba
- `src/lib/authService.ts` - Servicio con fallback automático a mock mode

## 🔐 Nota

El modo de prueba está completamente separado del backend real. Cuando el backend esté corriendo, el sistema lo utilizará automáticamente.
