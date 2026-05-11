# CRUD de Gestión de Usuarios - Admin

## 📋 Descripción

Se ha implementado un **CRUD completo para la gestión de usuarios** en el frontend, **accesible solo para administradores**. Este sistema funciona con datos en frontend (localStorage) y está listo para integrarse con el backend más adelante.

## ✨ Características

### ✅ Funcionalidades Implementadas

1. **Listar Usuarios**
   - Tabla con todos los usuarios registrados
   - Información: Email, Nombre, Apellido, Estado, Fecha de Registro
   - Búsqueda en tiempo real por email, nombre o apellido

2. **Crear Usuario**
   - Formulario modal para crear nuevo usuario
   - Validaciones: email válido, campos requeridos, email único
   - Los usuarios nuevos se guardan en localStorage

3. **Editar Usuario**
   - Editar cualquier información del usuario
   - Validación de email único (excepto el email actual)
   - Cambiar estado (Activo/Inactivo)

4. **Eliminar Usuario**
   - Botón de eliminar con confirmación
   - Protección: No permite eliminar al admin principal (admin@example.com)

### 🔐 Seguridad

- ✅ Solo accesible para usuario admin (email: admin@example.com)
- ✅ Si un usuario no-admin intenta acceder a `/admin/users` es redirigido al home
- ✅ El link solo aparece en el sidebar para admins
- ✅ Protección en el componente `AdminRoute`

## 📁 Archivos Creados/Modificados

### Archivos Nuevos:

- `src/pages/UserManagement.tsx` - Página principal del CRUD
- `src/hooks/useAdminUsers.ts` - Hook para gestionar usuarios con localStorage
- `src/components/AdminRoute.tsx` - Componente para proteger rutas de admin

### Archivos Modificados:

- `src/App.tsx` - Agregó ruta `/admin/users` con AdminRoute
- `src/components/AppSidebar.tsx` - Agregó link a gestión de usuarios (solo para admin)

## 🚀 Cómo Acceder

### 1. Inicia sesión como Admin

```
Email: admin@example.com
Contraseña: admin123
```

### 2. En el Sidebar aparecerá:

```
ADMINISTRACIÓN
├── Gestión de Usuarios
```

### 3. O accede directamente a:

```
http://localhost:5173/admin/users
```

## 💾 Datos

- Los usuarios se guardan en **localStorage** con key `admin_users_mock`
- Datos iniciales incluyen 4 usuarios de prueba
- Los cambios persisten dentro de la sesión del navegador
- Se reinician al limpiar localStorage o recargar la app desde cero

## 🔄 Próximos Pasos (Backend)

Para conectar esto con el backend:

1. Crear endpoint `/api/auth/users/` (GET) - Listar usuarios
2. Crear endpoint `/api/auth/users/` (POST) - Crear usuario
3. Crear endpoint `/api/auth/users/{id}/` (PUT) - Editar usuario
4. Crear endpoint `/api/auth/users/{id}/` (DELETE) - Eliminar usuario
5. Agregar autenticación y permisos (solo admin)

Los servicios en `authService.ts` deberán adaptarse para llamar a estos endpoints.

## 📊 Datos de Prueba Iniciales

| Email                  | Nombre   | Apellido | Estado |
| ---------------------- | -------- | -------- | ------ |
| admin@example.com      | Admin    | User     | Activo |
| scout@example.com      | Scout    | Pro      | Activo |
| director@example.com   | Director | General  | Activo |
| juan.perez@example.com | Juan     | Pérez    | Activo |

## 🎯 Notas Importantes

- Solo el admin puede crear, editar y eliminar usuarios
- No se puede eliminar al admin principal
- Los emails deben ser únicos
- Los cambios se guardan automáticamente en localStorage
- Validaciones en frontend (email, campos requeridos)

## 🧪 Testing

Para probar el CRUD:

1. Login como `admin@example.com` / `admin123`
2. Click en "Gestión de Usuarios" en el sidebar
3. Prueba crear, editar y eliminar usuarios
4. Prueba la búsqueda
5. Intenta cambiar el estado de los usuarios
6. Verifica que no puedas eliminar el admin principal

¡Listo para empezar! 🎉
