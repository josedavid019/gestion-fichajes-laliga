import React, { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { CreateUserData } from "@/hooks/useAdminUsers";

interface UserFormData extends CreateUserData {}

interface UserFormProps {
  initialData?: Partial<UserFormData>;
  onSubmit: (data: UserFormData) => void;
  onCancel: () => void;
  isEditing?: boolean;
}

const UserForm: React.FC<UserFormProps> = ({
  initialData = {},
  onSubmit,
  onCancel,
  isEditing = false,
}) => {
  const [formData, setFormData] = useState<UserFormData>({
    email: initialData.email || "",
    username: initialData.username || "",
    first_name: initialData.first_name || "",
    last_name: initialData.last_name || "",
    password: initialData.password || "",
    is_active: initialData.is_active ?? true,
    is_staff: initialData.is_staff ?? false,
    is_superuser: initialData.is_superuser ?? false,
    role: initialData.role ?? "scout",
    phone: initialData.phone || "",
    bio: initialData.bio || "",
    avatar: null,
  });

  useEffect(() => {
    setFormData({
      email: initialData.email || "",
      username: initialData.username || "",
      first_name: initialData.first_name || "",
      last_name: initialData.last_name || "",
      password: initialData.password || "",
      is_active: initialData.is_active ?? true,
      is_staff: initialData.is_staff ?? false,
      is_superuser: initialData.is_superuser ?? false,
      role: initialData.role ?? "scout",
      phone: initialData.phone || "",
      bio: initialData.bio || "",
      avatar: null,
    });
  }, [initialData]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (
      !formData.email ||
      !formData.username ||
      !formData.first_name ||
      !formData.last_name ||
      (!isEditing && !formData.password)
    ) {
      alert("Por favor completa todos los campos requeridos");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      alert("Por favor ingresa un email válido");
      return;
    }

    const usernameRegex = /^[a-zA-Z0-9_]+$/;
    if (!usernameRegex.test(formData.username)) {
      alert("El username solo puede contener letras, números y guiones bajos");
      return;
    }

    if (!isEditing && formData.password && formData.password.length < 6) {
      alert("La contraseña debe tener al menos 6 caracteres");
      return;
    }

    onSubmit(formData);
  };

  const handleChange = (
    field: keyof UserFormData,
    value: string | boolean | File | null,
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 gap-8 xl:grid-cols-2">
        <div className="bg-white border border-slate-200 rounded-3xl shadow-sm p-8">
          <div className="space-y-3">
            <div>
              <p className="text-xl font-semibold text-slate-900">
                Datos de cuenta
              </p>
              <p className="text-sm text-slate-500">
                Configura los detalles de acceso, permisos y estado.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <Label htmlFor="email" className="text-slate-700">
                  Email *
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="usuario@example.com"
                  value={formData.email}
                  onChange={(e) => handleChange("email", e.target.value)}
                  required
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="username" className="text-slate-700">
                  Username *
                </Label>
                <Input
                  id="username"
                  type="text"
                  placeholder="usuario123"
                  value={formData.username}
                  onChange={(e) => handleChange("username", e.target.value)}
                  required
                  className="mt-1"
                />
              </div>
              {!isEditing && (
                <div>
                  <Label htmlFor="password" className="text-slate-700">
                    Contraseña *
                  </Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={(e) => handleChange("password", e.target.value)}
                    required={!isEditing}
                    minLength={6}
                    className="mt-1"
                  />
                </div>
              )}
              <div>
                <Label htmlFor="role" className="text-slate-700">
                  Rol
                </Label>
                <Select
                  value={formData.role}
                  onValueChange={(value) => handleChange("role", value)}
                >
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Selecciona un rol" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="scout">Scout</SelectItem>
                    <SelectItem value="director">Directivo</SelectItem>
                    <SelectItem value="admin">Administrador</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label className="text-slate-700">Permisos y estado</Label>
                <div className="mt-3 space-y-3">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="is_active"
                      checked={formData.is_active}
                      onCheckedChange={(checked) =>
                        handleChange("is_active", checked as boolean)
                      }
                    />
                    <Label
                      htmlFor="is_active"
                      className="text-slate-700 cursor-pointer"
                    >
                      Activo
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="is_staff"
                      checked={formData.is_staff}
                      onCheckedChange={(checked) =>
                        handleChange("is_staff", checked as boolean)
                      }
                    />
                    <Label
                      htmlFor="is_staff"
                      className="text-slate-700 cursor-pointer"
                    >
                      Staff
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="is_superuser"
                      checked={formData.is_superuser}
                      onCheckedChange={(checked) =>
                        handleChange("is_superuser", checked as boolean)
                      }
                    />
                    <Label
                      htmlFor="is_superuser"
                      className="text-slate-700 cursor-pointer"
                    >
                      Superusuario
                    </Label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-3xl shadow-sm p-8">
          <div className="space-y-3">
            <div>
              <p className="text-xl font-semibold text-slate-900">
                Información personal
              </p>
              <p className="text-sm text-slate-500">
                Datos de perfil que completan la ficha del usuario.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <Label htmlFor="first_name" className="text-slate-700">
                  Nombre *
                </Label>
                <Input
                  id="first_name"
                  type="text"
                  placeholder="Juan"
                  value={formData.first_name}
                  onChange={(e) => handleChange("first_name", e.target.value)}
                  required
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="last_name" className="text-slate-700">
                  Apellido *
                </Label>
                <Input
                  id="last_name"
                  type="text"
                  placeholder="García"
                  value={formData.last_name}
                  onChange={(e) => handleChange("last_name", e.target.value)}
                  required
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="phone" className="text-slate-700">
                  Teléfono
                </Label>
                <Input
                  id="phone"
                  type="tel"
                  placeholder="+34 600 000 000"
                  value={formData.phone}
                  onChange={(e) => handleChange("phone", e.target.value)}
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="avatar" className="text-slate-700">
                  Avatar
                </Label>
                <Input
                  id="avatar"
                  type="file"
                  accept="image/*"
                  onChange={(e) =>
                    handleChange("avatar", e.target.files?.[0] || null)
                  }
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="bio" className="text-slate-700">
                  Biografía
                </Label>
                <textarea
                  id="bio"
                  placeholder="Breve descripción personal..."
                  value={formData.bio}
                  onChange={(e) => handleChange("bio", e.target.value)}
                  className="mt-1 w-full min-h-[120px] rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:justify-end">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancelar
        </Button>
        <Button
          type="submit"
          className="bg-primary text-primary-foreground hover:bg-primary/90"
        >
          {isEditing ? "Actualizar" : "Crear"}
        </Button>
      </div>
    </form>
  );
};

export default UserForm;
