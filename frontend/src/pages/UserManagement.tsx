import React, { useState } from "react";
import {
  useAdminUsers,
  AdminUser,
  CreateUserData,
} from "@/hooks/useAdminUsers";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { Trash2, Edit2, Plus, Search, Shield, User } from "lucide-react";
import UserForm from "@/components/UserForm";

interface FormData extends CreateUserData {}

const ROLE_COLORS: Record<string, string> = {
  admin: "bg-red-100 text-red-800",
  director: "bg-purple-100 text-purple-800",
  scout: "bg-blue-100 text-blue-800",
};

const ROLE_LABELS: Record<string, string> = {
  admin: "Administrador",
  director: "Directivo",
  scout: "Scout",
};

const UserManagement: React.FC = () => {
  const { users, isLoading, createUser, updateUser, deleteUser } =
    useAdminUsers();
  const [searchTerm, setSearchTerm] = useState("");
  const [filterRole, setFilterRole] = useState("all");
  const [filterStatus, setFilterStatus] = useState("all");
  const [filterStaff, setFilterStaff] = useState("all");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<AdminUser | null>(null);
  const [formData, setFormData] = useState<FormData>({
    email: "",
    username: "",
    first_name: "",
    last_name: "",
    password: "",
    is_active: true,
    is_staff: false,
    is_superuser: false,
    role: "scout",
    phone: "",
    bio: "",
    avatar: null,
  });

  const filteredUsers = users.filter((user) => {
    const matchesSearch =
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.last_name.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesRole = filterRole === "all" ? true : user.role === filterRole;

    const matchesStatus =
      filterStatus === "all"
        ? true
        : filterStatus === "active"
          ? user.is_active
          : !user.is_active;

    const matchesStaff =
      filterStaff === "all"
        ? true
        : filterStaff === "staff"
          ? user.is_staff
          : !user.is_staff;

    return matchesSearch && matchesRole && matchesStatus && matchesStaff;
  });

  const handleOpenDialog = (user?: AdminUser) => {
    if (user) {
      setEditingUser(user);
      setFormData({
        email: user.email,
        username: user.username,
        first_name: user.first_name,
        last_name: user.last_name,
        password: "", // No mostrar contraseña existente por seguridad
        is_active: user.is_active,
        is_staff: user.is_staff,
        is_superuser: user.is_superuser,
        role: user.role || "scout",
        phone: user.phone || "",
        bio: user.bio || "",
        avatar: null, // Can't pre-fill file input
      });
    } else {
      setEditingUser(null);
      setFormData({
        email: "",
        username: "",
        first_name: "",
        last_name: "",
        password: "",
        is_active: true,
        is_staff: false,
        is_superuser: false,
        role: "scout",
        phone: "",
        bio: "",
        avatar: null,
      });
    }
    setIsDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setIsDialogOpen(false);
    setEditingUser(null);
    setFormData({
      email: "",
      username: "",
      first_name: "",
      last_name: "",
      password: "",
      is_active: true,
      is_staff: false,
      is_superuser: false,
      role: "scout",
      phone: "",
      bio: "",
      avatar: null,
    });
  };

  const handleSubmit = (data: FormData) => {
    if (!data.email || !data.username || !data.first_name || !data.last_name) {
      toast.error("Por favor completa todos los campos requeridos");
      return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.email)) {
      toast.error("Por favor ingresa un email válido");
      return;
    }

    // Username validation (no spaces, alphanumeric and underscore)
    const usernameRegex = /^[a-zA-Z0-9_]+$/;
    if (!usernameRegex.test(data.username)) {
      toast.error(
        "El username solo puede contener letras, números y guiones bajos",
      );
      return;
    }

    try {
      // Don't auto-set is_staff and is_superuser - let user control them
      let userData = { ...data };

      if (editingUser) {
        // Check if email is already in use by another user
        if (
          data.email !== editingUser.email &&
          users.some((u) => u.email === data.email)
        ) {
          toast.error("Este email ya está en uso");
          return;
        }
        // Check if username is already in use by another user
        if (
          data.username !== editingUser.username &&
          users.some((u) => u.username === data.username)
        ) {
          toast.error("Este username ya está en uso");
          return;
        }
        updateUser(editingUser.id, userData);
        toast.success("Usuario actualizado correctamente");
      } else {
        // Check if email already exists
        if (users.some((u) => u.email === data.email)) {
          toast.error("Este email ya está registrado");
          return;
        }
        // Check if username already exists
        if (users.some((u) => u.username === data.username)) {
          toast.error("Este username ya está registrado");
          return;
        }
        createUser(userData);
        toast.success("Usuario creado correctamente");
      }
      handleCloseDialog();
    } catch (error) {
      toast.error("Error al procesar la solicitud");
      console.error(error);
    }
  };

  const handleDelete = (userId: number) => {
    if (window.confirm("¿Estás seguro de que deseas eliminar este usuario?")) {
      deleteUser(userId);
      toast.success("Usuario eliminado correctamente");
    }
  };

  const formatDate = (isoDate: string) =>
    new Date(isoDate).toLocaleDateString("es-ES", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-lg text-slate-600">Cargando usuarios...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">
            Gestión de Usuarios
          </h1>
          <p className="text-slate-600 mt-1">
            Total de usuarios:{" "}
            <span className="font-semibold">{users.length}</span>
          </p>
        </div>
        <Button
          onClick={() => handleOpenDialog()}
          className="bg-primary text-primary-foreground hover:bg-primary/90"
        >
          <Plus className="w-4 h-4 mr-2" />
          Nuevo Usuario
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="bg-white border border-slate-200 rounded-3xl shadow-sm p-4">
        <div className="grid gap-4 xl:grid-cols-[3fr_1fr_1fr_1fr_0.9fr] items-end">
          <div className="relative xl:col-span-2">
            <Search className="absolute left-3 top-3 text-slate-400 w-5 h-5" />
            <Input
              type="text"
              placeholder="Buscar por email, username, nombre o apellido..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 h-12"
            />
          </div>
          <div>
            <Label htmlFor="role_filter" className="text-slate-700">
              Rol
            </Label>
            <Select
              value={filterRole}
              onValueChange={(value) => setFilterRole(value)}
            >
              <SelectTrigger className="mt-1 h-12">
                <SelectValue placeholder="Todos los roles" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                <SelectItem value="admin">Administrador</SelectItem>
                <SelectItem value="director">Directivo</SelectItem>
                <SelectItem value="scout">Scout</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="status_filter" className="text-slate-700">
              Estado
            </Label>
            <Select
              value={filterStatus}
              onValueChange={(value) => setFilterStatus(value)}
            >
              <SelectTrigger className="mt-1 h-12">
                <SelectValue placeholder="Todos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                <SelectItem value="active">Activo</SelectItem>
                <SelectItem value="inactive">Inactivo</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="staff_filter" className="text-slate-700">
              Staff
            </Label>
            <Select
              value={filterStaff}
              onValueChange={(value) => setFilterStaff(value)}
            >
              <SelectTrigger className="mt-1 h-12">
                <SelectValue placeholder="Todos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                <SelectItem value="staff">Staff</SelectItem>
                <SelectItem value="nonstaff">No Staff</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm text-slate-500">
              Mostrando {filteredUsers.length} de {users.length} usuarios.
            </p>
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setSearchTerm("");
                setFilterRole("all");
                setFilterStatus("all");
                setFilterStaff("all");
              }}
              className="h-12 w-full sm:w-auto border-muted-foreground/30 text-muted-foreground hover:bg-muted"
            >
              Limpiar filtros
            </Button>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white border border-slate-200 rounded-3xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50 text-slate-900">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-900">
                  Nombre completo
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-900">
                  Username
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-900">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-900">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-900">
                  Registrado
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-900">
                  Activo
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-900">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {filteredUsers.length > 0 ? (
                filteredUsers.map((user) => {
                  const roleKey = user.role || "scout";
                  return (
                    <tr
                      key={user.id}
                      className="group bg-white hover:bg-slate-50 transition-colors"
                    >
                      <td className="px-6 py-4 text-sm text-slate-900 whitespace-nowrap">
                        {user.first_name} {user.last_name}
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-700 font-mono whitespace-nowrap">
                        @{user.username}
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-900 whitespace-nowrap">
                        {user.email}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <span
                          className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                            ROLE_COLORS[roleKey] || "bg-gray-100 text-gray-800"
                          }`}
                        >
                          {roleKey === "admin" && (
                            <Shield className="w-3 h-3 mr-1" />
                          )}
                          {ROLE_LABELS[roleKey] || "Sin rol"}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-700">
                        {formatDate(user.created_at)}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <span
                          className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                            user.is_active
                              ? "bg-green-100 text-green-800"
                              : "bg-red-100 text-red-800"
                          }`}
                        >
                          {user.is_active ? "Activo" : "Inactivo"}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm space-x-2">
                        <Button
                          onClick={() => handleOpenDialog(user)}
                          size="sm"
                          variant="outline"
                          className="text-blue-600 hover:text-blue-700"
                        >
                          <Edit2 className="w-4 h-4" />
                        </Button>
                        <Button
                          onClick={() => handleDelete(user.id)}
                          size="sm"
                          variant="outline"
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center">
                    <p className="text-slate-500">
                      {searchTerm
                        ? "No se encontraron usuarios"
                        : "No hay usuarios registrados"}
                    </p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Dialog - Create/Edit User */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="w-full max-w-5xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingUser ? "Editar Usuario" : "Crear Nuevo Usuario"}
            </DialogTitle>
          </DialogHeader>

          <UserForm
            initialData={formData}
            onSubmit={handleSubmit}
            onCancel={handleCloseDialog}
            isEditing={!!editingUser}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default UserManagement;
