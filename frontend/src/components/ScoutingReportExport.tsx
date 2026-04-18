import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { FileDown, Plus, List, Grid, Eye, Settings, Download, Mail } from "lucide-react";

interface ScoutingReport {
  id: string;
  playerName: string;
  position: string;
  age: number;
  club: string;
  createdDate: string;
  lastModified: string;
  status: "draft" | "completed" | "archived";
  sections: string[];
  rating: number;
}

const mockReports: ScoutingReport[] = [
  {
    id: "1",
    playerName: "Vinícius Júnior",
    position: "LW",
    age: 24,
    club: "Real Madrid",
    createdDate: "2024-04-10",
    lastModified: "2024-04-15",
    status: "completed",
    sections: ["General", "Técnico", "Físico", "Mental", "Análisis Video"],
    rating: 9.2,
  },
  {
    id: "2",
    playerName: "Jude Bellingham",
    position: "CM",
    age: 21,
    club: "Real Madrid",
    createdDate: "2024-03-20",
    lastModified: "2024-04-12",
    status: "completed",
    sections: ["General", "Técnico", "Físico"],
    rating: 8.8,
  },
  {
    id: "3",
    playerName: "Adolfo Fernández",
    position: "CB",
    age: 23,
    club: "Celta Vigo",
    createdDate: "2024-04-01",
    lastModified: "2024-04-14",
    status: "draft",
    sections: ["General", "Técnico"],
    rating: 7.5,
  },
  {
    id: "4",
    playerName: "Kylian Mbappé",
    position: "ST",
    age: 25,
    club: "Real Madrid",
    createdDate: "2024-02-15",
    lastModified: "2024-04-10",
    status: "archived",
    sections: ["General", "Técnico", "Físico", "Mental", "Análisis Video"],
    rating: 9.5,
  },
];

const reportSections = [
  { id: "general", label: "Información General", description: "Datos personales y datos básicos del jugador" },
  { id: "tecnico", label: "Análisis Técnico", description: "Habilidades técnicas y capacidades" },
  { id: "fisico", label: "Análisis Físico", description: "Evaluación física y atributos" },
  { id: "mental", label: "Aspecto Mental", description: "Personalidad, mentalidad y liderazgo" },
  { id: "video", label: "Análisis Video", description: "Análisis de video del jugador" },
  { id: "comparativa", label: "Análisis Comparativo", description: "Comparación con otros jugadores" },
  { id: "financiero", label: "Análisis Financiero", description: "Valor de mercado y costos" },
  { id: "riesgos", label: "Análisis de Riesgos", description: "Identificación de riesgos potenciales" },
];

const exportFormats = [
  { id: "pdf", label: "PDF", description: "Documento profesional en PDF" },
  { id: "excel", label: "Excel", description: "Hoja de cálculo con datos", disabled: true },
  { id: "html", label: "HTML", description: "Página web interactiva", disabled: true },
];

const getStatusColor = (status: string) => {
  switch (status) {
    case "completed":
      return "default";
    case "draft":
      return "secondary";
    case "archived":
      return "outline";
    default:
      return "secondary";
  }
};

const getStatusLabel = (status: string) => {
  switch (status) {
    case "completed":
      return "Completado";
    case "draft":
      return "Borrador";
    case "archived":
      return "Archivado";
    default:
      return status;
  }
};

export const ScoutingReportExport = () => {
  const [viewMode, setViewMode] = useState<"list" | "grid">("list");
  const [selectedReports, setSelectedReports] = useState<string[]>([]);
  const [filterStatus, setFilterStatus] = useState<"all" | "completed" | "draft" | "archived">("all");
  const [selectedReport, setSelectedReport] = useState<ScoutingReport | null>(null);
  const [exportFormat, setExportFormat] = useState("pdf");
  const [selectedSections, setSelectedSections] = useState<string[]>(reportSections.map((s) => s.id));

  const filteredReports = mockReports.filter((r) => filterStatus === "all" || r.status === filterStatus);

  const toggleReportSelection = (id: string) => {
    setSelectedReports((prev) => (prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]));
  };

  const toggleAllReports = () => {
    if (selectedReports.length === filteredReports.length) {
      setSelectedReports([]);
    } else {
      setSelectedReports(filteredReports.map((r) => r.id));
    }
  };

  const toggleSection = (id: string) => {
    setSelectedSections((prev) => (prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]));
  };

  const toggleAllSections = () => {
    if (selectedSections.length === reportSections.length) {
      setSelectedSections([]);
    } else {
      setSelectedSections(reportSections.map((s) => s.id));
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileDown className="w-5 h-5" />
            Reportes de Scouting
          </CardTitle>
          <CardDescription>Crea, gestiona y exporta reportes detallados de evaluación de jugadores</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Acciones Superiores */}
          <div className="flex flex-col sm:flex-row gap-3 justify-between items-start sm:items-center">
            <div className="flex gap-2">
              <Button size="sm" variant="outline">
                <Plus className="w-4 h-4 mr-2" />
                Nuevo Reporte
              </Button>
              <Dialog>
                <DialogTrigger asChild>
                  <Button
                    size="sm"
                    variant="default"
                    disabled={selectedReports.length === 0}
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Exportar ({selectedReports.length})
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl">
                  <DialogHeader>
                    <DialogTitle>Exportar Reportes de Scouting</DialogTitle>
                    <DialogDescription>
                      Configura las opciones de exportación para {selectedReports.length} reporte(s)
                    </DialogDescription>
                  </DialogHeader>

                  <Tabs defaultValue="format" className="w-full">
                    <TabsList className="grid w-full grid-cols-3">
                      <TabsTrigger value="format">Formato</TabsTrigger>
                      <TabsTrigger value="sections">Secciones</TabsTrigger>
                      <TabsTrigger value="preview">Vista Previa</TabsTrigger>
                    </TabsList>

                    {/* Selección de Formato */}
                    <TabsContent value="format" className="space-y-4">
                      <Label className="text-base font-semibold">Selecciona el formato de exportación</Label>
                      <div className="grid grid-cols-1 gap-3">
                        {exportFormats.map((format) => (
                          <div
                            key={format.id}
                            className={`p-3 border rounded-lg cursor-pointer transition-all ${
                              exportFormat === format.id && !format.disabled
                                ? "border-blue-500 bg-blue-50"
                                : "border-gray-200 hover:border-gray-300"
                            } ${format.disabled ? "opacity-50 cursor-not-allowed" : ""}`}
                            onClick={() => !format.disabled && setExportFormat(format.id)}
                          >
                            <input
                              type="radio"
                              name="format"
                              value={format.id}
                              checked={exportFormat === format.id}
                              onChange={() => setExportFormat(format.id)}
                              disabled={format.disabled}
                              className="mr-3"
                            />
                            <label className="font-medium cursor-pointer">{format.label}</label>
                            <p className="text-xs text-muted-foreground mt-1">{format.description}</p>
                          </div>
                        ))}
                      </div>

                      {/* Opciones Adicionales */}
                      <div className="space-y-3 mt-4 p-3 bg-muted rounded-lg">
                        <Label className="text-sm font-semibold">Opciones de PDF</Label>
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <Checkbox id="color" defaultChecked />
                            <Label htmlFor="color" className="text-sm cursor-pointer">
                              Incluir gráficos en color
                            </Label>
                          </div>
                          <div className="flex items-center gap-2">
                            <Checkbox id="logo" defaultChecked />
                            <Label htmlFor="logo" className="text-sm cursor-pointer">
                              Incluir logo del club
                            </Label>
                          </div>
                          <div className="flex items-center gap-2">
                            <Checkbox id="confidencial" />
                            <Label htmlFor="confidencial" className="text-sm cursor-pointer">
                              Marcar como confidencial
                            </Label>
                          </div>
                        </div>
                      </div>
                    </TabsContent>

                    {/* Selección de Secciones */}
                    <TabsContent value="sections" className="space-y-4">
                      <div className="flex items-center justify-between mb-3">
                        <Label className="text-base font-semibold">Incluir Secciones</Label>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={toggleAllSections}
                        >
                          {selectedSections.length === reportSections.length ? "Deseleccionar Todo" : "Seleccionar Todo"}
                        </Button>
                      </div>
                      <div className="space-y-3">
                        {reportSections.map((section) => (
                          <div
                            key={section.id}
                            className="flex items-start gap-3 p-3 border rounded hover:bg-muted/50"
                          >
                            <Checkbox
                              id={section.id}
                              checked={selectedSections.includes(section.id)}
                              onCheckedChange={() => toggleSection(section.id)}
                              className="mt-1"
                            />
                            <label htmlFor={section.id} className="flex-1 cursor-pointer">
                              <p className="font-medium">{section.label}</p>
                              <p className="text-xs text-muted-foreground">{section.description}</p>
                            </label>
                          </div>
                        ))}
                      </div>
                      <p className="text-xs text-muted-foreground mt-4">
                        {selectedSections.length} de {reportSections.length} secciones seleccionadas
                      </p>
                    </TabsContent>

                    {/* Vista Previa */}
                    <TabsContent value="preview" className="space-y-4">
                      <div className="bg-muted p-4 rounded-lg space-y-3">
                        <h3 className="font-semibold">Vista Previa de Exportación</h3>
                        <div className="space-y-2 text-sm">
                          <p>
                            <strong>Reportes a exportar:</strong> {selectedReports.length}
                          </p>
                          <p>
                            <strong>Formato:</strong> {exportFormats.find((f) => f.id === exportFormat)?.label}
                          </p>
                          <p>
                            <strong>Secciones:</strong> {selectedSections.length}
                          </p>
                        </div>
                      </div>

                      <div className="bg-blue-50 border border-blue-200 p-3 rounded-lg">
                        <p className="text-xs text-blue-900">
                          El archivo PDF incluirá todos los reportes seleccionados con las secciones elegidas. Se generará un documento combinado o individual según tu preferencia.
                        </p>
                      </div>
                    </TabsContent>
                  </Tabs>

                  <div className="flex gap-2 justify-end mt-6">
                    <Button variant="outline">Cancelar</Button>
                    <Button>
                      <Download className="w-4 h-4 mr-2" />
                      Exportar {selectedReports.length} Reporte(s)
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>

            {/* Controles de Vista */}
            <div className="flex gap-2">
              <Button
                size="sm"
                variant={viewMode === "list" ? "default" : "outline"}
                onClick={() => setViewMode("list")}
              >
                <List className="w-4 h-4" />
              </Button>
              <Button
                size="sm"
                variant={viewMode === "grid" ? "default" : "outline"}
                onClick={() => setViewMode("grid")}
              >
                <Grid className="w-4 h-4" />
              </Button>
              <Select value={filterStatus} onValueChange={(value: any) => setFilterStatus(value)}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Estado" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos</SelectItem>
                  <SelectItem value="completed">Completados</SelectItem>
                  <SelectItem value="draft">Borradores</SelectItem>
                  <SelectItem value="archived">Archivados</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Contador de Seleccionados */}
          {selectedReports.length > 0 && (
            <Card className="bg-blue-50 border-blue-200">
              <CardContent className="pt-4">
                <p className="text-sm">
                  <strong>{selectedReports.length}</strong> reporte(s) seleccionado(s) para exportación
                </p>
              </CardContent>
            </Card>
          )}

          {/* Vista Lista */}
          {viewMode === "list" && (
            <div className="space-y-2">
              <div className="flex items-center gap-3 p-3 border-b border-t font-medium text-sm">
                <Checkbox
                  checked={selectedReports.length === filteredReports.length && filteredReports.length > 0}
                  onCheckedChange={toggleAllReports}
                />
                <span className="flex-1">Jugador</span>
                <span className="w-20">Estado</span>
                <span className="w-20">Calificación</span>
                <span className="w-32">Fecha Modificación</span>
                <span className="w-20">Acciones</span>
              </div>
              {filteredReports.map((report) => (
                <div key={report.id} className="flex items-center gap-3 p-3 border rounded hover:bg-muted/50">
                  <Checkbox
                    checked={selectedReports.includes(report.id)}
                    onCheckedChange={() => toggleReportSelection(report.id)}
                  />
                  <div className="flex-1">
                    <p className="font-medium">{report.playerName}</p>
                    <p className="text-xs text-muted-foreground">
                      {report.position} • {report.club} • {report.age} años
                    </p>
                  </div>
                  <div className="w-20">
                    <Badge variant={getStatusColor(report.status)}>
                      {getStatusLabel(report.status)}
                    </Badge>
                  </div>
                  <div className="w-20 text-center">
                    <span className="font-bold text-amber-600">{report.rating}</span>
                  </div>
                  <div className="w-32 text-sm">{report.lastModified}</div>
                  <div className="w-20 flex gap-1">
                    <Button size="sm" variant="ghost">
                      <Eye className="w-4 h-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setSelectedReport(report)}
                    >
                      <Download className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Vista Grid */}
          {viewMode === "grid" && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredReports.map((report) => (
                <Card key={report.id} className="cursor-pointer hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-base">{report.playerName}</CardTitle>
                        <CardDescription className="text-xs">
                          {report.position} • {report.club}
                        </CardDescription>
                      </div>
                      <Checkbox
                        checked={selectedReports.includes(report.id)}
                        onCheckedChange={() => toggleReportSelection(report.id)}
                      />
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center justify-between">
                      <Badge variant={getStatusColor(report.status)}>
                        {getStatusLabel(report.status)}
                      </Badge>
                      <span className="font-bold text-amber-600">{report.rating}</span>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      <p>Creado: {report.createdDate}</p>
                      <p>Modificado: {report.lastModified}</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-xs font-medium">Secciones incluidas:</p>
                      <div className="flex flex-wrap gap-1">
                        {report.sections.map((section) => (
                          <Badge key={section} variant="secondary" className="text-xs">
                            {section}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div className="flex gap-2 pt-2">
                      <Button size="sm" className="flex-1" variant="outline">
                        <Eye className="w-3 h-3 mr-1" />
                        Ver
                      </Button>
                      <Button size="sm" className="flex-1">
                        <Download className="w-3 h-3 mr-1" />
                        Exportar
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {filteredReports.length === 0 && (
            <div className="text-center py-12 text-muted-foreground">
              <p>No hay reportes que coincidan con los filtros seleccionados</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Template de Nuevos Reportes */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Crear Nuevo Reporte</CardTitle>
          <CardDescription>Plantilla para documentar evaluación de jugadores</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="player-name">Nombre del Jugador</Label>
              <Input id="player-name" placeholder="Ej: Vinícius Júnior" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="position">Posición</Label>
              <Select>
                <SelectTrigger id="position">
                  <SelectValue placeholder="Selecciona posición" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="st">Delantero (ST)</SelectItem>
                  <SelectItem value="lw">Extremo Izquierdo (LW)</SelectItem>
                  <SelectItem value="rw">Extremo Derecho (RW)</SelectItem>
                  <SelectItem value="cm">Centrocampista (CM)</SelectItem>
                  <SelectItem value="cb">Central (CB)</SelectItem>
                  <SelectItem value="lb">Lateral Izquierdo (LB)</SelectItem>
                  <SelectItem value="rb">Lateral Derecho (RB)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="club">Club</Label>
              <Input id="club" placeholder="Ej: Real Madrid" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="age">Edad</Label>
              <Input id="age" type="number" placeholder="Edad del jugador" min="16" max="40" />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">Notas Iniciales</Label>
            <Textarea
              id="notes"
              placeholder="Escribe observaciones iniciales sobre el jugador..."
              className="min-h-24"
            />
          </div>

          <Button className="w-full">
            <Plus className="w-4 h-4 mr-2" />
            Crear Reporte
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};
