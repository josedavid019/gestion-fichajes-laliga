import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { Search, Calendar, User, Activity } from "lucide-react";

interface AuditLog {
  id: number;
  user: number | null;
  user_email: string | null;
  user_username: string | null;
  action: string;
  entity: string;
  entity_id: number | null;
  old_data: any;
  new_data: any;
  created_at: string;
}

const AuditLogs: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filters, setFilters] = useState({
    user_id: "",
    action: "",
    entity: "",
  });

  useEffect(() => {
    fetchAuditLogs();
  }, [filters]);

  const fetchAuditLogs = async () => {
    try {
      const queryParams = new URLSearchParams();
      if (filters.user_id) queryParams.append("user_id", filters.user_id);
      if (filters.action) queryParams.append("action", filters.action);
      if (filters.entity) queryParams.append("entity", filters.entity);

      const response = await fetch(`/api/accounts/audit-logs/?${queryParams}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setLogs(data);
      } else if (response.status === 500) {
        // Backend not running or internal error
        toast.error(
          "El servidor backend no está disponible. Los logs de auditoría requieren que el backend esté ejecutándose.",
        );
        setLogs([]);
      } else {
        toast.error("Error al cargar los logs de auditoría");
        setLogs([]);
      }
    } catch (error) {
      // Network error - backend not running
      toast.error(
        "No se puede conectar al servidor backend. Asegúrate de que el backend esté ejecutándose.",
      );
      console.error("Error de conexión:", error);
      setLogs([]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString("es-ES");
  };

  const getActionColor = (action: string) => {
    switch (action.toLowerCase()) {
      case "create":
        return "bg-green-100 text-green-800";
      case "update":
        return "bg-blue-100 text-blue-800";
      case "delete":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-lg text-slate-600">
          Cargando logs de auditoría...
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">
            Logs de Auditoría
          </h1>
          <p className="text-slate-600 mt-1">
            Total de logs: <span className="font-semibold">{logs.length}</span>
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-4">Filtros</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <Label htmlFor="user_filter">Usuario</Label>
            <Input
              id="user_filter"
              placeholder="ID de usuario"
              value={filters.user_id}
              onChange={(e) =>
                setFilters({ ...filters, user_id: e.target.value })
              }
            />
          </div>
          <div>
            <Label htmlFor="action_filter">Acción</Label>
            <Select
              value={filters.action}
              onValueChange={(value) =>
                setFilters({ ...filters, action: value === "all" ? "" : value })
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="Todas las acciones" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas las acciones</SelectItem>
                <SelectItem value="create">Crear</SelectItem>
                <SelectItem value="update">Actualizar</SelectItem>
                <SelectItem value="delete">Eliminar</SelectItem>
                <SelectItem value="login">Login</SelectItem>
                <SelectItem value="logout">Logout</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="entity_filter">Entidad</Label>
            <Select
              value={filters.entity}
              onValueChange={(value) =>
                setFilters({ ...filters, entity: value === "all" ? "" : value })
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="Todas las entidades" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas las entidades</SelectItem>
                <SelectItem value="user">Usuario</SelectItem>
                <SelectItem value="player">Jugador</SelectItem>
                <SelectItem value="match">Partido</SelectItem>
                <SelectItem value="profile">Perfil</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Logs Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Fecha
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Usuario
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Acción
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Entidad
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">
                  Detalles
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {logs.length > 0 ? (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-50 transition">
                    <td className="px-6 py-4 text-sm text-slate-900">
                      <div className="flex items-center">
                        <Calendar className="w-4 h-4 mr-2 text-slate-400" />
                        {formatDate(log.created_at)}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-900">
                      <div className="flex items-center">
                        <User className="w-4 h-4 mr-2 text-slate-400" />
                        {log.user_username || log.user_email || "Sistema"}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getActionColor(
                          log.action,
                        )}`}
                      >
                        <Activity className="w-3 h-3 mr-1" />
                        {log.action}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-900">
                      {log.entity} {log.entity_id && `(${log.entity_id})`}
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-900">
                      <div className="max-w-xs truncate">
                        {log.old_data && log.new_data
                          ? "Datos modificados"
                          : log.new_data
                            ? "Registro creado"
                            : "Registro eliminado"}
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan={5}
                    className="px-6 py-12 text-center text-slate-500"
                  >
                    <div className="flex flex-col items-center">
                      <Activity className="w-12 h-12 text-slate-300 mb-4" />
                      <p className="text-lg font-medium">
                        No hay logs de auditoría
                      </p>
                      <p className="text-sm mt-1">
                        {isLoading
                          ? "Cargando..."
                          : "Los logs aparecerán aquí cuando se realicen acciones en el sistema."}
                      </p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AuditLogs;
