import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle, Clock, Zap, Filter, Bell, CheckCircle } from "lucide-react";
import { Progress } from "@/components/ui/progress";

interface ContractAlert {
  id: string;
  player: string;
  club: string;
  position: string;
  expiryDate: string;
  daysRemaining: number;
  severity: "critical" | "warning" | "info";
  status: "active" | "resolved";
  releaseClause?: number;
}

interface TransferWindow {
  id: string;
  season: string;
  startDate: string;
  endDate: string;
  daysRemaining: number;
  type: "summer" | "winter";
}

const mockAlerts: ContractAlert[] = [
  {
    id: "1",
    player: "Vinícius Júnior",
    club: "Real Madrid",
    position: "LW",
    expiryDate: "2025-06-30",
    daysRemaining: 163,
    severity: "info",
    status: "active",
    releaseClause: 1000,
  },
  {
    id: "2",
    player: "Eduardo Camavinga",
    club: "Real Madrid",
    position: "CM",
    expiryDate: "2024-06-30",
    daysRemaining: 73,
    severity: "warning",
    status: "active",
  },
  {
    id: "3",
    player: "Nacho Fernández",
    club: "Real Madrid",
    position: "CB",
    expiryDate: "2024-05-01",
    daysRemaining: 13,
    severity: "critical",
    status: "active",
  },
  {
    id: "4",
    player: "Luka Modrić",
    club: "Real Madrid",
    position: "CM",
    expiryDate: "2024-06-30",
    daysRemaining: 73,
    severity: "critical",
    status: "active",
  },
  {
    id: "5",
    player: "Jude Bellingham",
    club: "Real Madrid",
    position: "CM",
    expiryDate: "2029-06-30",
    daysRemaining: 1828,
    severity: "info",
    status: "resolved",
  },
];

const transferWindows: TransferWindow[] = [
  {
    id: "1",
    season: "Summer 2024",
    startDate: "2024-07-01",
    endDate: "2024-09-02",
    daysRemaining: 106,
    type: "summer",
  },
  {
    id: "2",
    season: "Winter 2024-2025",
    startDate: "2025-01-01",
    endDate: "2025-02-03",
    daysRemaining: 319,
    type: "winter",
  },
];

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case "critical":
      return "destructive";
    case "warning":
      return "default";
    default:
      return "secondary";
  }
};

const getSeverityBgColor = (severity: string) => {
  switch (severity) {
    case "critical":
      return "bg-red-50 border-red-200";
    case "warning":
      return "bg-yellow-50 border-yellow-200";
    default:
      return "bg-blue-50 border-blue-200";
  }
};

export const ContractAlerts = () => {
  const [filterStatus, setFilterStatus] = useState<"all" | "active" | "resolved">("active");
  const [filterSeverity, setFilterSeverity] = useState<"all" | "critical" | "warning" | "info">("all");
  const [searchTerm, setSearchTerm] = useState("");

  const filteredAlerts = mockAlerts.filter((alert) => {
    const statusMatch = filterStatus === "all" || alert.status === filterStatus;
    const severityMatch = filterSeverity === "all" || alert.severity === filterSeverity;
    const searchMatch =
      alert.player.toLowerCase().includes(searchTerm.toLowerCase()) ||
      alert.club.toLowerCase().includes(searchTerm.toLowerCase());

    return statusMatch && severityMatch && searchMatch;
  });

  const criticalCount = mockAlerts.filter((a) => a.severity === "critical" && a.status === "active").length;
  const warningCount = mockAlerts.filter((a) => a.severity === "warning" && a.status === "active").length;

  const getDaysProgressColor = (days: number) => {
    if (days < 30) return "bg-red-500";
    if (days < 90) return "bg-yellow-500";
    return "bg-green-500";
  };

  return (
    <div className="space-y-6">
      {/* Alertas Críticas */}
      {criticalCount > 0 && (
        <Alert className="border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertTitle className="text-red-900">Acciones Urgentes Requeridas</AlertTitle>
          <AlertDescription className="text-red-800">
            Hay {criticalCount} contrato(s) que vence(n) en menos de 30 días. Se requiere acción inmediata.
          </AlertDescription>
        </Alert>
      )}

      {/* Tabs */}
      <Tabs defaultValue="contracts" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="contracts" className="flex items-center gap-2">
            <Clock className="w-4 h-4" />
            Contratos
          </TabsTrigger>
          <TabsTrigger value="windows" className="flex items-center gap-2">
            <Zap className="w-4 h-4" />
            Ventanas de Transferencia
          </TabsTrigger>
        </TabsList>

        {/* Tab: Contratos */}
        <TabsContent value="contracts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="w-5 h-5" />
                Alertas de Vencimiento de Contratos
              </CardTitle>
              <CardDescription>
                Monitorea los vencimientos de contratos y toma decisiones de renovación a tiempo
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Filtros */}
              <div className="flex flex-col sm:flex-row gap-3">
                <Input
                  placeholder="Buscar por jugador o club..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="flex-1"
                />
                <Select value={filterStatus} onValueChange={(value: any) => setFilterStatus(value)}>
                  <SelectTrigger className="w-full sm:w-40">
                    <SelectValue placeholder="Estado" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos</SelectItem>
                    <SelectItem value="active">Activos</SelectItem>
                    <SelectItem value="resolved">Resueltos</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={filterSeverity} onValueChange={(value: any) => setFilterSeverity(value)}>
                  <SelectTrigger className="w-full sm:w-40">
                    <SelectValue placeholder="Severidad" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos</SelectItem>
                    <SelectItem value="critical">Crítico</SelectItem>
                    <SelectItem value="warning">Advertencia</SelectItem>
                    <SelectItem value="info">Información</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Estadísticas Rápidas */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <Card className="bg-blue-50">
                  <CardContent className="pt-4">
                    <p className="text-xs text-muted-foreground">Total de Alertas</p>
                    <p className="text-2xl font-bold text-blue-600">{mockAlerts.length}</p>
                  </CardContent>
                </Card>
                <Card className="bg-red-50">
                  <CardContent className="pt-4">
                    <p className="text-xs text-muted-foreground">Críticas</p>
                    <p className="text-2xl font-bold text-red-600">{criticalCount}</p>
                  </CardContent>
                </Card>
                <Card className="bg-yellow-50">
                  <CardContent className="pt-4">
                    <p className="text-xs text-muted-foreground">Advertencias</p>
                    <p className="text-2xl font-bold text-yellow-600">{warningCount}</p>
                  </CardContent>
                </Card>
                <Card className="bg-green-50">
                  <CardContent className="pt-4">
                    <p className="text-xs text-muted-foreground">Resueltas</p>
                    <p className="text-2xl font-bold text-green-600">
                      {mockAlerts.filter((a) => a.status === "resolved").length}
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Lista de Alertas */}
              <div className="space-y-3">
                {filteredAlerts.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <p>No hay alertas que coincidan con los filtros</p>
                  </div>
                ) : (
                  filteredAlerts.map((alert) => (
                    <div
                      key={alert.id}
                      className={`border rounded-lg p-4 ${getSeverityBgColor(alert.severity)} ${
                        alert.status === "resolved" ? "opacity-60" : ""
                      }`}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold text-base">{alert.player}</h3>
                            <Badge variant={getSeverityColor(alert.severity)}>
                              {alert.severity === "critical"
                                ? "Crítico"
                                : alert.severity === "warning"
                                  ? "Advertencia"
                                  : "Información"}
                            </Badge>
                            {alert.status === "resolved" && (
                              <Badge variant="outline" className="flex items-center gap-1">
                                <CheckCircle className="w-3 h-3" />
                                Resuelto
                              </Badge>
                            )}
                          </div>
                          <p className="text-xs text-muted-foreground">
                            {alert.position} • {alert.club}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold text-sm">{alert.daysRemaining}</p>
                          <p className="text-xs text-muted-foreground">días</p>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-xs">
                          <span>Vence: {alert.expiryDate}</span>
                          <span className="font-medium">{alert.daysRemaining} días restantes</span>
                        </div>
                        <Progress value={(alert.daysRemaining / 365) * 100} className="h-2" />
                      </div>

                      {alert.releaseClause && (
                        <div className="mt-2 text-xs text-muted-foreground">
                          Cláusula liberatoria: ${alert.releaseClause}M
                        </div>
                      )}

                      <div className="mt-3 flex gap-2">
                        {alert.status === "active" && (
                          <>
                            <Button size="sm" variant="default">
                              Ver Detalles
                            </Button>
                            <Button size="sm" variant="outline">
                              Iniciar Negociación
                            </Button>
                          </>
                        )}
                        {alert.status === "resolved" && (
                          <Button size="sm" variant="outline" disabled>
                            Renovación Completada
                          </Button>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab: Ventanas de Transferencia */}
        <TabsContent value="windows" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="w-5 h-5" />
                Ventanas de Transferencia
              </CardTitle>
              <CardDescription>Próximas ventanas de transferencia disponibles para actividades</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {transferWindows.map((window) => {
                  const progress = (window.daysRemaining / 240) * 100;
                  return (
                    <Card key={window.id} className="border-2">
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div>
                            <CardTitle className="text-lg">{window.season}</CardTitle>
                            <CardDescription>
                              {window.type === "summer" ? "Mercado de Verano" : "Mercado de Invierno"}
                            </CardDescription>
                          </div>
                          <Badge variant={window.type === "summer" ? "default" : "secondary"}>
                            {window.daysRemaining < 30 ? "Próximo" : "Disponible"}
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span>Inicia: {window.startDate}</span>
                            <span className="font-medium">Finaliza: {window.endDate}</span>
                          </div>
                          <Progress value={progress} className="h-3" />
                          <p className="text-xs text-muted-foreground">{window.daysRemaining} días restantes</p>
                        </div>

                        <div className="grid grid-cols-2 gap-2">
                          <div className="bg-muted p-2 rounded">
                            <p className="text-xs text-muted-foreground">Últimos Días</p>
                            <p className="font-bold text-lg">{Math.max(0, window.daysRemaining - 14)}</p>
                          </div>
                          <div className="bg-muted p-2 rounded">
                            <p className="text-xs text-muted-foreground">Estado</p>
                            <p className="font-bold">
                              {window.daysRemaining > 60 ? "Abierta" : "Cierre Próximo"}
                            </p>
                          </div>
                        </div>

                        <Button className="w-full">
                          Ver Jugadores Disponibles
                        </Button>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>

              {/* Recomendaciones */}
              <Card className="border-blue-200 bg-blue-50">
                <CardHeader>
                  <CardTitle className="text-base">Recomendaciones de Transferencia</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  <p>• Considera renovaciones antes de que se cierren las ventanas</p>
                  <p>• Negocia con jugadores en el mercado durante ventanas abiertas</p>
                  <p>• Prepara listados de objetivos antes de cada ventana</p>
                  <p>• Monitorea las cláusulas de rescisión de jugadores objetivo</p>
                </CardContent>
              </Card>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};
