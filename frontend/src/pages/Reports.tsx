import { Download, Filter, FileSpreadsheet, FileDown, BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState } from "react";

const tableData = [
  { id: 1, name: "Lamine Yamal", club: "FC Barcelona", position: "EXT", age: 17, value: "€180M", change: "+15%", risk: "Bajo" },
  { id: 2, name: "Jude Bellingham", club: "Real Madrid", position: "MED", age: 21, value: "€150M", change: "+8%", risk: "Bajo" },
  { id: 3, name: "Florian Wirtz", club: "B. Leverkusen", position: "MED", age: 21, value: "€135M", change: "+22%", risk: "Medio" },
  { id: 4, name: "Jamal Musiala", club: "Bayern München", position: "MED", age: 21, value: "€120M", change: "+12%", risk: "Bajo" },
  { id: 5, name: "Pedri", club: "FC Barcelona", position: "MED", age: 21, value: "€100M", change: "-5%", risk: "Medio" },
  { id: 6, name: "Bukayo Saka", club: "Arsenal FC", position: "EXT", age: 22, value: "€140M", change: "+10%", risk: "Bajo" },
  { id: 7, name: "Phil Foden", club: "Manchester City", position: "MED", age: 24, value: "€130M", change: "+5%", risk: "Bajo" },
  { id: 8, name: "Vinícius Jr", club: "Real Madrid", position: "EXT", age: 24, value: "€200M", change: "+3%", risk: "Bajo" },
];

const summaryKpis = [
  { label: "Total Jugadores", value: "157" },
  { label: "Valor Acumulado", value: "€2.4B" },
  { label: "Promedio Edad", value: "22.3" },
  { label: "Alertas Activas", value: "5" },
];

export default function Reports() {
  const [filter, setFilter] = useState("");
  const filtered = tableData.filter((r) =>
    r.name.toLowerCase().includes(filter.toLowerCase()) ||
    r.club.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-heading font-bold">Reportes</h1>
          <p className="text-sm text-muted-foreground mt-1">Exporta y analiza datos del sistema</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" className="gap-2">
            <FileDown className="w-3.5 h-3.5" /> PDF
          </Button>
          <Button variant="outline" size="sm" className="gap-2">
            <FileSpreadsheet className="w-3.5 h-3.5" /> Excel
          </Button>
          <Button size="sm" className="gap-2">
            <BarChart3 className="w-3.5 h-3.5" /> Power BI
          </Button>
        </div>
      </div>

      {/* Summary KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {summaryKpis.map((kpi) => (
          <div key={kpi.label} className="stat-card text-center">
            <p className="text-[10px] text-muted-foreground uppercase tracking-wider">{kpi.label}</p>
            <p className="text-xl font-heading font-bold mt-1">{kpi.value}</p>
          </div>
        ))}
      </div>

      {/* Table */}
      <div className="glass-card p-5">
        <div className="flex items-center gap-3 mb-4">
          <div className="relative flex-1 max-w-xs">
            <Filter className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Filtrar jugadores..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="pl-9 bg-muted/30 border-border/50 h-9 text-sm"
            />
          </div>
          <p className="text-xs text-muted-foreground">{filtered.length} resultados</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border/50">
                {["Jugador", "Club", "Pos", "Edad", "Valor", "Var.", "Riesgo"].map((h) => (
                  <th key={h} className="text-left py-3 px-3 text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((row) => (
                <tr key={row.id} className="border-b border-border/20 hover:bg-muted/20 transition-colors">
                  <td className="py-3 px-3 text-xs font-medium text-foreground">{row.name}</td>
                  <td className="py-3 px-3 text-xs text-muted-foreground">{row.club}</td>
                  <td className="py-3 px-3">
                    <span className="text-[10px] bg-primary/10 text-primary px-2 py-0.5 rounded-md font-medium">{row.position}</span>
                  </td>
                  <td className="py-3 px-3 text-xs text-muted-foreground">{row.age}</td>
                  <td className="py-3 px-3 text-xs font-semibold gradient-text">{row.value}</td>
                  <td className="py-3 px-3">
                    <span className={`text-xs font-medium ${row.change.startsWith("+") ? "text-success" : "text-destructive"}`}>{row.change}</span>
                  </td>
                  <td className="py-3 px-3">
                    <span className={`text-[10px] px-2 py-0.5 rounded-md font-medium ${
                      row.risk === "Bajo" ? "bg-success/10 text-success" : "bg-warning/10 text-warning"
                    }`}>
                      {row.risk}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
