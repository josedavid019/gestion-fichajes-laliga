import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { AlertCircle } from "lucide-react";

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await login(email, password);
      toast.success("¡Sesión iniciada correctamente!");
      navigate("/");
    } catch (error: any) {
      let errorMessage = "Error desconocido";

      // Try to parse JSON error from backend
      try {
        const parsedError = JSON.parse(error.message);
        if (parsedError.non_field_errors) {
          errorMessage = parsedError.non_field_errors[0];
        } else if (parsedError.email) {
          errorMessage = parsedError.email[0];
        } else if (parsedError.password) {
          errorMessage = parsedError.password[0];
        } else {
          errorMessage =
            Object.values(parsedError)[0]?.[0] || JSON.stringify(parsedError);
        }
      } catch {
        // If not JSON, use error message as-is
        errorMessage =
          error.message === "Failed to fetch"
            ? "No se pudo conectar con el servidor"
            : error.message;
      }

      console.error("Login error:", error);
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
            Inicia sesión en tu cuenta
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="email" className="text-slate-700">
                Email
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="ejemplo@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={isLoading}
                className="mt-1"
              />
            </div>

            <div>
              <Label htmlFor="password" className="text-slate-700">
                Contraseña
              </Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
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
              {isLoading ? "Iniciando sesión..." : "Iniciar sesión"}
            </Button>
          </form>

          <div className="mt-6 p-4 bg-blue-50 rounded-lg flex gap-3">
            <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-blue-700">
              Si es tu primer acceso, contacta con el administrador para obtener
              tus credenciales.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
