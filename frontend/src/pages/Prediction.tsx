import { useState, useMemo, useEffect } from "react";
import {
  TrendingUp,
  BarChart3,
  User,
  Zap,
  Search,
  Loader2,
  AlertCircle,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from "recharts";
import { usePlayers } from "../hooks/usePlayers";
import {
  usePrediction,
  useTopPerformers,
  useModels,
} from "../hooks/usePrediction";

export default function Prediction() {
  const [selectedPlayerId, setSelectedPlayerId] = useState<number | null>(null);
  const [searchTerm, setSearchTerm] = useState("");

  const [debouncedSearch, setDebouncedSearch] = useState("");

  // Use debounced term to drive server-side search
  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(searchTerm.trim()), 300);
    return () => clearTimeout(t);
  }, [searchTerm]);

  const { data: playersData = [], isLoading: playersLoading } = usePlayers(
    debouncedSearch ? { search: debouncedSearch } : undefined,
  );
  const { data: prediction, isLoading: predictionLoading } =
    usePrediction(selectedPlayerId);
  const { data: topPerformers = [] } = useTopPerformers(5);
  const { data: models = [] } = useModels();

  const filteredPlayers = useMemo(() => {
    if (!playersData || !searchTerm) return playersData;
    const lower = searchTerm.toLowerCase();
    return playersData.filter((p) => {
      const matchesSearch =
        p.alias?.toLowerCase().includes(lower) ||
        p.first_name?.toLowerCase().includes(lower) ||
        p.last_name?.toLowerCase().includes(lower) ||
        p.full_name?.toLowerCase().includes(lower) ||
        p.current_club?.name?.toLowerCase().includes(lower);

      return matchesSearch;
    });
  }, [playersData, searchTerm]);

  const selectedPlayer = useMemo(() => {
    if (!selectedPlayerId || !filteredPlayers) return null;
    return filteredPlayers.find((p) => p.id === selectedPlayerId);
  }, [selectedPlayerId, filteredPlayers]);

  // Datos para gráfico radar (skills comparativos)
  const radarData = useMemo(() => {
    if (!selectedPlayer) return [];
    return [
      {
        skill: "Edad",
        jugador: Math.min((selectedPlayer.age || 20) * 3.5, 100),
        promedio: 70,
      },
      { skill: "Valor Mercado", jugador: 85, promedio: 65 },
      {
        skill: "Experiencia",
        jugador: Math.min((selectedPlayer.age || 20) * 2, 100),
        promedio: 60,
      },
      { skill: "Potencial", jugador: 78, promedio: 70 },
      { skill: "Consistencia", jugador: 82, promedio: 72 },
    ];
  }, [selectedPlayer]);

  // Datos para gráfico de comparables
  const comparableData = useMemo(() => {
    if (!topPerformers || topPerformers.length === 0) return [];
    const baseValue = prediction?.predicted_value_eur || 0;
    return topPerformers.map((p) => ({
      name: p.player.alias || "Jugador",
      value: Math.round(p.predicted_value_eur / 1000000),
    }));
  }, [topPerformers, prediction]);

  const activeModel = models.find((m) => m.status === "active");
  const topFeatures = prediction?.shap_values?.top_features || [
    "age",
    "goals_per_90",
    "avg_rating",
    "minutes",
    "assists_per_90",
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-heading font-bold">Predicción de Valor</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Modelo ML para estimación de valor de mercado
        </p>
      </div>

      {/* Selector de Jugador */}
      <div className="glass-card p-4">
        <div className="flex items-center gap-2 mb-3">
          <Search className="w-4 h-4 text-primary" />
          <label className="text-sm font-semibold">Buscar Jugador</label>
        </div>
        <div className="relative">
          <input
            type="text"
            placeholder="Busca por nombre, club..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        {/* Lista de jugadores */}
        {searchTerm && (
          <div className="mt-3 max-h-64 overflow-y-auto rounded-lg border border-border bg-background/50">
            {filteredPlayers.length > 0 ? (
              filteredPlayers.slice(0, 10).map((player) => (
                <button
                  key={player.id}
                  onClick={() => {
                    setSelectedPlayerId(player.id);
                    setSearchTerm("");
                  }}
                  className="w-full text-left px-3 py-2 hover:bg-primary/10 border-b border-border/50 last:border-b-0 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">
                        {player.alias || `${player.first_name} ${player.last_name}`}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {player.position} • {player.current_club?.name || "Sin club"}
                      </p>
                    </div>
                    <span className="text-xs font-semibold text-primary">
                      €
                      {player.market_value_eur
                        ? (parseFloat(player.market_value_eur) / 1000000).toFixed(
                            1
                          )
                        : "N/A"}
                      M
                    </span>
                  </div>
                </button>
              ))
            ) : (
              <div className="px-4 py-3 text-sm text-muted-foreground">
                No se encontraron jugadores con "{searchTerm}".
              </div>
            )}
          </div>
        )}
      </div>

      {/* Contenido Principal */}
      {selectedPlayer && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Información del Jugador y Predicción */}
          <div className="glass-card p-6">
            <div className="flex items-center gap-3 mb-5">
              {selectedPlayer.photo_url ? (
                <img
                  src={selectedPlayer.photo_url}
                  alt={selectedPlayer.alias}
                  className="w-14 h-14 rounded-full object-cover"
                />
              ) : (
                <div className="w-14 h-14 rounded-full bg-primary/15 flex items-center justify-center">
                  <User className="w-7 h-7 text-primary" />
                </div>
              )}
              <div>
                <h3 className="font-heading font-bold text-lg">
                  {selectedPlayer.alias ||
                    `${selectedPlayer.first_name} ${selectedPlayer.last_name}`}
                </h3>
                <p className="text-xs text-muted-foreground">
                  {selectedPlayer.position} • {selectedPlayer.current_club?.name}
                </p>
              </div>
            </div>

            {/* Predicción o Loading */}
            {predictionLoading ? (
              <div className="text-center py-4 mb-5">
                <Loader2 className="w-5 h-5 animate-spin mx-auto text-primary" />
                <p className="text-xs text-muted-foreground mt-2">
                  Generando predicción...
                </p>
              </div>
            ) : prediction ? (
              <>
                <div className="text-center py-4 mb-5 rounded-xl glow-border bg-primary/5">
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1">
                    Valor Predicho
                  </p>
                  <p className="text-3xl font-heading font-bold gradient-text">
                    €
                    {(
                      prediction.predicted_value_eur / 1000000
                    ).toFixed(1)}M
                  </p>
                  <p className="text-xs text-muted-foreground mt-2">
                    Confianza: {(prediction.confidence * 100).toFixed(0)}%
                  </p>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex justify-between py-1.5 border-b border-border/20">
                    <span className="text-xs text-muted-foreground">
                      Valor Actual
                    </span>
                    <span className="text-xs font-medium">
                      €
                      {selectedPlayer.market_value_eur
                        ? (
                            parseFloat(selectedPlayer.market_value_eur) /
                            1000000
                          ).toFixed(1)
                        : "N/A"}
                      M
                    </span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-border/20">
                    <span className="text-xs text-muted-foreground">Edad</span>
                    <span className="text-xs font-medium">
                      {selectedPlayer.age} años
                    </span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-border/20">
                    <span className="text-xs text-muted-foreground">Altura</span>
                    <span className="text-xs font-medium">
                      {selectedPlayer.height_cm} cm
                    </span>
                  </div>
                  <div className="flex justify-between py-1.5">
                    <span className="text-xs text-muted-foreground">Pie</span>
                    <span className="text-xs font-medium">
                      {selectedPlayer.preferred_foot || "N/A"}
                    </span>
                  </div>
                </div>
              </>
            ) : (
              <div className="text-center py-4 text-muted-foreground text-xs">
                Error cargando predicción
              </div>
            )}
          </div>

          {/* Gráficos y Explicación */}
          <div className="lg:col-span-2 space-y-4">
            {/* Explicación del Modelo */}
            <div className="glass-card p-5">
              <div className="flex items-center gap-2 mb-3">
                <Zap className="w-4 h-4 text-warning" />
                <h3 className="font-heading font-semibold text-sm">
                  Explicación del Modelo
                </h3>
              </div>
              <p className="text-sm text-foreground/85 leading-relaxed">
                {prediction ? (
                  <>
                    El modelo XGBoost predice un valor de{" "}
                    <span className="font-semibold">
                      €{(prediction.predicted_value_eur / 1000000).toFixed(1)}M
                    </span>{" "}
                    basado en análisis de estadísticas históricas. Los factores
                    más influyentes son:{" "}
                    <span className="font-semibold">
                      {topFeatures.slice(0, 3).join(", ")}
                    </span>
                    . La confianza del modelo es{" "}
                    <span className="font-semibold">
                      {(prediction.confidence * 100).toFixed(0)}%
                    </span>
                    .
                    {activeModel && (
                      <>
                        {" "}
                        Modelo:{" "}
                        <span className="text-xs text-muted-foreground">
                          {activeModel.name} v{activeModel.version}
                        </span>
                      </>
                    )}
                  </>
                ) : (
                  "Selecciona un jugador para ver la explicación del modelo"
                )}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Radar Chart */}
              {radarData.length > 0 && (
                <div className="glass-card p-5">
                  <h3 className="font-heading font-semibold text-sm mb-4">
                    Perfil vs Promedio
                  </h3>
                  <ResponsiveContainer width="100%" height={220}>
                    <RadarChart data={radarData}>
                      <PolarGrid stroke="hsl(222, 25%, 16%)" />
                      <PolarAngleAxis
                        dataKey="skill"
                        tick={{ fill: "hsl(215, 15%, 55%)", fontSize: 10 }}
                      />
                      <PolarRadiusAxis
                        tick={false}
                        axisLine={false}
                      />
                      <Radar
                        name="Jugador"
                        dataKey="jugador"
                        stroke="hsl(160, 84%, 39%)"
                        fill="hsl(160, 84%, 39%)"
                        fillOpacity={0.2}
                      />
                      <Radar
                        name="Promedio"
                        dataKey="promedio"
                        stroke="hsl(187, 92%, 45%)"
                        fill="hsl(187, 92%, 45%)"
                        fillOpacity={0.1}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* Comparables */}
              {comparableData.length > 0 && (
                <div className="glass-card p-5">
                  <div className="flex items-center gap-2 mb-4">
                    <BarChart3 className="w-4 h-4 text-accent" />
                    <h3 className="font-heading font-semibold text-sm">
                      Top Jugadores (€M)
                    </h3>
                  </div>
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={comparableData} layout="vertical">
                      <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="hsl(222, 25%, 16%)"
                      />
                      <XAxis
                        type="number"
                        tick={{ fill: "hsl(215, 15%, 55%)", fontSize: 10 }}
                        axisLine={false}
                      />
                      <YAxis
                        type="category"
                        dataKey="name"
                        tick={{ fill: "hsl(215, 15%, 55%)", fontSize: 10 }}
                        axisLine={false}
                        width={90}
                      />
                      <Tooltip
                        contentStyle={{
                          background: "hsl(222, 41%, 9%)",
                          border: "1px solid hsl(222, 25%, 16%)",
                          borderRadius: "8px",
                          fontSize: 12,
                        }}
                      />
                      <Bar
                        dataKey="value"
                        fill="hsl(160, 84%, 39%)"
                        radius={[0, 4, 4, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {!selectedPlayer && !playersLoading && (
        <div className="glass-card p-8 text-center">
          <AlertCircle className="w-8 h-8 text-muted-foreground mx-auto mb-3" />
          <p className="text-muted-foreground">
            Busca y selecciona un jugador para ver su predicción de valor
          </p>
        </div>
      )}
    </div>
  );
}
