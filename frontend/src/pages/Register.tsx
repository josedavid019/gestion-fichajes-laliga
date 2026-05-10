import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

const Register: React.FC = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    email: "",
    first_name: "",
    last_name: "",
    password: "",
    password_confirm: "",
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (formData.password !== formData.password_confirm) {
      toast.error("Las contraseñas no coinciden");
      return;
    }

    if (formData.password.length < 6) {
      toast.error("La contraseña debe tener al menos 6 caracteres");
      return;
    }

    setIsLoading(true);

    try {
      await register(
        formData.email,
        formData.first_name,
        formData.last_name,
        formData.password,
        formData.password_confirm
      );
      toast.success("¡Registro exitoso! Bienvenido");
      navigate("/");
    } catch (error: any) {
      let errorMessage = "Error en el registro";

      try {
        const errorData = JSON.parse(error.message);
        if (typeof errorData === "object") {
          const firstError = Object.values(errorData)[0];
          if (Array.isArray(firstError)) {
            errorMessage = firstError[0] as string;
          } else {
            errorMessage = JSON.stringify(errorData);
          }
        }
      } catch {
        errorMessage =
          error.message === "Failed to fetch"
            ? "No se pudo conectar con el servidor"
            : error.message;
      }

      toast.error(`Error: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800 p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-lg shadow-2xl p-8">
          <h1 className="text-3xl font-bold text-center mb-2 text-slate-900">
            Fichajes La Liga
          </h1>
          <p className="text-center text-slate-600 mb-8">
            Crea tu cuenta
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="email" className="text-slate-700">
                Email
              </Label>
              <Input
                id="email"
                type="email"
                name="email"
                placeholder="ejemplo@email.com"
                value={formData.email}
                onChange={handleChange}
                required
                disabled={isLoading}
                className="mt-1"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="first_name" className="text-slate-700">
                  Nombre
                </Label>
                <Input
                  id="first_name"
                  type="text"
                  name="first_name"
                  placeholder="Juan"
                  value={formData.first_name}
                  onChange={handleChange}
                  required
                  disabled={isLoading}
                  className="mt-1"
                />
              </div>

              <div>
                <Label htmlFor="last_name" className="text-slate-700">
                  Apellido
                </Label>
                <Input
                  id="last_name"
                  type="text"
                  name="last_name"
                  placeholder="García"
                  value={formData.last_name}
                  onChange={handleChange}
                  required
                  disabled={isLoading}
                  className="mt-1"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="password" className="text-slate-700">
                Contraseña
              </Label>
              <Input
                id="password"
                type="password"
                name="password"
                placeholder="••••••••"
                value={formData.password}
                onChange={handleChange}
                required
                disabled={isLoading}
                className="mt-1"
              />
              <p className="text-xs text-slate-500 mt-1">
                Mínimo 6 caracteres
              </p>
            </div>

            <div>
              <Label htmlFor="password_confirm" className="text-slate-700">
                Confirmar contraseña
              </Label>
              <Input
                id="password_confirm"
                type="password"
                name="password_confirm"
                placeholder="••••••••"
                value={formData.password_confirm}
                onChange={handleChange}
                required
                disabled={isLoading}
                className="mt-1"
              />
            </div>

            <Button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-lg transition"
            >
              {isLoading ? "Registrando..." : "Registrarse"}
            </Button>
          </form>

          <div className="mt-6 pt-6 border-t border-slate-200">
            <p className="text-center text-slate-600">
              ¿Ya tienes cuenta?{" "}
              <Link
                to="/login"
                className="text-blue-600 hover:text-blue-700 font-semibold"
              >
                Inicia sesión
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
