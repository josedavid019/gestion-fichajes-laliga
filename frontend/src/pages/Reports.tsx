import { BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useEffect, useRef, useState } from "react";
import PowerBIDashboard from "@/components/PowerBIDashboard";
import PlayerCard from "@/components/PlayerCard";
import { usePlayers } from "@/hooks/usePlayers";

interface Player {
  id: number;
  first_name: string;
  last_name: string;
  alias: string;
  age: number | null;
  position: string;
  nationality: {
    id: number;
    name: string;
    code: string;
    flag_url: string;
  } | null;
  current_club: {
    id: number;
    name: string;
    city: string;
    logo_url: string;
  } | null;
  shirt_number: number | null;
  height_cm: number | null;
  weight_kg: number | null;
  preferred_foot: string;
  status: string;
  market_value_eur: string | null;
  photo_url: string;
}

const ITEMS_PER_LOAD = 15;

export default function Reports() {
  const [filter, setFilter] = useState("");
  const [displayedCount, setDisplayedCount] = useState(ITEMS_PER_LOAD);
  const [selectedPosition, setSelectedPosition] = useState("");
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const observerTarget = useRef<HTMLDivElement>(null);
  const { data: playersData, isLoading, error } = usePlayers();

  const players = playersData || [];

  // Get unique positions
  const uniquePositions = Array.from(
    new Set(players.map((p) => p.position).filter(Boolean))
  ).sort() as string[];

  const filtered = players.filter((p) => {
    const fullName = `${p.first_name} ${p.last_name}`.toLowerCase();
    const club = p.current_club?.name.toLowerCase() || "";
    const filterLower = filter.toLowerCase();

    const matchesSearch = fullName.includes(filterLower) || club.includes(filterLower);
    const matchesPosition = !selectedPosition || p.position === selectedPosition;

    return matchesSearch && matchesPosition;
  });

  const displayedPlayers = filtered.slice(0, displayedCount);

  // Infinite scroll
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && displayedCount < filtered.length) {
          setDisplayedCount((prev) => Math.min(prev + ITEMS_PER_LOAD, filtered.length));
        }
      },
      { threshold: 0.1 }
    );

    if (observerTarget.current) {
      observer.observe(observerTarget.current);
    }

    return () => {
      if (observerTarget.current) {
        observer.unobserve(observerTarget.current);
      }
    };
  }, [displayedCount, filtered.length]);

  // Reset displayed count when filter changes
  useEffect(() => {
    setDisplayedCount(ITEMS_PER_LOAD);
  }, [filter]);

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFilter(e.target.value);
  };

  const totalValue = players.reduce((sum, p) => {
    return sum + (parseFloat(p.market_value_eur as string) || 0);
  }, 0);

  const avgAge =
    players.length > 0
      ? (players.reduce((sum, p) => sum + (p.age || 0), 0) / players.length).toFixed(1)
      : "0";

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-heading font-bold">Dashboard</h1>
          <p className="text-sm text-muted-foreground mt-1">Explora y analiza jugadores de La Liga</p>
        </div>
        <div className="flex gap-2">
          <Button size="sm" className="gap-2" onClick={() => window.open("https://app.powerbi.com/reportEmbed?reportId=95af94a9-e6da-47b0-99f8-91e0d40f0344&autoAuth=true&ctid=740be6bd-fd36-470e-94d9-0f0c777fadb9&actionBarEnabled=true", "_blank")}>
            <BarChart3 className="w-3.5 h-3.5" /> Power BI
          </Button>
        </div>
      </div>

      {/* Summary KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: "Total Jugadores", value: players.length.toString() },
          { label: "Valor Acumulado", value: `€${(totalValue / 1000000).toFixed(1)}M` },
          { label: "Promedio Edad", value: avgAge },
          { label: "Estado Activo", value: players.filter(p => p.status === "active").length.toString() },
        ].map((kpi) => (
          <div key={kpi.label} className="stat-card text-center">
            <p className="text-[10px] text-muted-foreground uppercase tracking-wider">{kpi.label}</p>
            <p className="text-xl font-heading font-bold mt-1">{kpi.value}</p>
          </div>
        ))}
      </div>

      {/* Table */}
      <div className="glass-card p-5">
        <div className="flex items-center gap-3 mb-4 flex-wrap">
          <input
            type="text"
            placeholder="Filtrar jugadores..."
            value={filter}
            onChange={handleFilterChange}
            className="flex-1 min-w-xs px-3 py-2 bg-muted/30 border border-border/50 rounded text-sm"
          />
          <select
            value={selectedPosition}
            onChange={(e) => {
              setSelectedPosition(e.target.value);
              setDisplayedCount(ITEMS_PER_LOAD);
            }}
            className="px-3 py-2 bg-muted/30 border border-border/50 rounded text-sm"
          >
            <option value="">Todas las posiciones</option>
            {uniquePositions.map((pos) => (
              <option key={pos} value={pos}>
                {pos}
              </option>
            ))}
          </select>
          <p className="text-xs text-muted-foreground whitespace-nowrap">{displayedCount} de {filtered.length} resultados</p>
        </div>

        {isLoading ? (
          <p className="text-center py-8">Cargando...</p>
        ) : error ? (
          <p className="text-center py-8 text-destructive">Error cargando datos</p>
        ) : (
          <div className="overflow-y-auto max-h-screen">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-muted/50">
                <tr className="border-b border-border/50">
                  <th className="text-left py-3 px-3 text-[10px] font-semibold text-muted-foreground">Jugador</th>
                  <th className="text-left py-3 px-3 text-[10px] font-semibold text-muted-foreground">Posición</th>
                  <th className="text-left py-3 px-3 text-[10px] font-semibold text-muted-foreground">Club</th>
                  <th className="text-left py-3 px-3 text-[10px] font-semibold text-muted-foreground">Edad</th>
                  <th className="text-left py-3 px-3 text-[10px] font-semibold text-muted-foreground">Valor</th>
                  <th className="text-left py-3 px-3 text-[10px] font-semibold text-muted-foreground">Estado</th>
                </tr>
              </thead>
              <tbody>
                {displayedPlayers.length > 0 ? (
                  displayedPlayers.map((player) => (
                    <tr
                      key={player.id}
                      className="border-b border-border/20 hover:bg-muted/30 cursor-pointer transition-colors"
                      onClick={() => setSelectedPlayer(player)}
                    >
                      <td className="py-3 px-3 text-xs font-medium">{player.alias}</td>
                      <td className="py-3 px-3 text-xs text-muted-foreground">{player.position || "N/A"}</td>
                      <td className="py-3 px-3 text-xs text-muted-foreground">{player.current_club?.name || "N/A"}</td>
                      <td className="py-3 px-3 text-xs text-muted-foreground">{player.age || "N/A"}</td>
                      <td className="py-3 px-3 text-xs font-semibold">{player.market_value_eur ? `€${(parseFloat(player.market_value_eur as string) / 1000000).toFixed(1)}M` : "N/A"}</td>
                      <td className="py-3 px-3 text-xs">
                        <span className={`px-2 py-1 rounded text-[10px] font-medium ${
                          player.status === "active" ? "bg-success/10 text-success" :
                          player.status === "injured" ? "bg-warning/10 text-warning" :
                          "bg-muted/10 text-muted-foreground"
                        }`}>
                          {player.status}
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="py-8 px-3 text-center text-xs">Sin resultados</td>
                  </tr>
                )}
              </tbody>
            </table>

            {/* Intersection observer target for infinite scroll */}
            <div ref={observerTarget} className="py-4 text-center text-xs text-muted-foreground">
              {displayedCount < filtered.length && "Cargando más..."}
              {displayedCount >= filtered.length && filtered.length > 0 && "Fin de los resultados"}
            </div>
          </div>
        )}
      </div>

      {/* Power BI Dashboard */}
      <PowerBIDashboard
        title="Gráficos y Análisis en Profundidad"
        reportId="95af94a9-e6da-47b0-99f8-91e0d40f0344"
        ctid="740be6bd-fd36-470e-94d9-0f0c777fadb9"
      />

      {/* Player Card Modal */}
      {selectedPlayer && (
        <PlayerCard
          player={selectedPlayer}
          onClose={() => setSelectedPlayer(null)}
        />
      )}
    </div>
  );
}
