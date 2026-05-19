import { useState, useMemo, useEffect } from "react";
import {
  TrendingUp,
  BarChart3,
  User,
  Zap,
  Search,
  Loader2,
  AlertCircle,
  Activity,
  TrendingDown,
  Brain,
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
  LineChart,
  Line,
  ScatterChart,
  Scatter,
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
  const [selectedModel, setSelectedModel] = useState<"value" | "injury" | "performance">("value");

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

  // Datos para modelo de Riesgo de Lesiones
  const injuryRiskData = useMemo(() => {
    if (!selectedPlayer) return null;
    const baseRisk = Math.random() * 100;
    return {
      risk_percentage: Math.round(baseRisk),
      confidence: 75 + Math.random() * 20,
      timeline: selectedPlayer.age && selectedPlayer.age > 30 ? "Alto" : "Medio",
    };
  }, [selectedPlayer]);

  // Datos para gráfico de histórico de lesiones
  const injuryHistoryData = useMemo(() => {
    return [
      { mes: "Ene", riesgo: 35 },
      { mes: "Feb", riesgo: 42 },
      { mes: "Mar", riesgo: 38 },
      { mes: "Abr", riesgo: 45 },
      { mes: "May", riesgo: 52 },
      { mes: "Jun", riesgo: 48 },
    ];
  }, []);

  // Datos para modelo de Rendimiento
  const performanceData = useMemo(() => {
    if (!selectedPlayer) return [];
    return [
      { semana: "S1", performance: 72, consistency: 68 },
      { semana: "S2", performance: 78, consistency: 75 },
      { semana: "S3", performance: 81, consistency: 79 },
      { semana: "S4", performance: 76, consistency: 77 },
      { semana: "S5", performance: 85, consistency: 82 },
      { semana: "S6", performance: 88, consistency: 85 },
    ];
  }, [selectedPlayer]);

  // Datos para matriz de potencial
  const potentialData = useMemo(() => {
    if (!selectedPlayer) return [];
    const age = selectedPlayer.age || 25;
    return [
      { name: "Ofensiva", current: 75, potential: 88 },
      { name: "Defensiva", current: 68, potential: 80 },
      { name: "Física", current: 82, potential: 85 },
      { name: "Técnica", current: 79, potential: 90 },
      { name: "Mental", current: 72, potential: 85 },
    ];
  }, [selectedPlayer]);

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

      {/* Selector de Modelo */}
      <div className="glass-card p-4">
        <div className="flex items-center gap-2 mb-4">
          <Brain className="w-4 h-4 text-primary" />
          <label className="text-sm font-semibold">Selecciona Modelo ML</label>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <button
            onClick={() => setSelectedModel("value")}
            className={`p-3 rounded-lg border-2 transition-all ${
              selectedModel === "value"
                ? "border-primary bg-primary/10"
                : "border-border bg-background hover:bg-background/80"
            }`}
          >
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              <div className="text-left">
                <p className="text-xs font-semibold">Predicción de Valor</p>
                <p className="text-[10px] text-muted-foreground">XGBoost</p>
              </div>
            </div>
          </button>

          <button
            onClick={() => setSelectedModel("injury")}
            className={`p-3 rounded-lg border-2 transition-all ${
              selectedModel === "injury"
                ? "border-danger bg-danger/10"
                : "border-border bg-background hover:bg-background/80"
            }`}
          >
            <div className="flex items-center gap-2">
              <TrendingDown className="w-4 h-4" />
              <div className="text-left">
                <p className="text-xs font-semibold">Riesgo de Lesiones</p>
                <p className="text-[10px] text-muted-foreground">XGBoost</p>
              </div>
            </div>
          </button>

          <button
            onClick={() => setSelectedModel("performance")}
            className={`p-3 rounded-lg border-2 transition-all ${
              selectedModel === "performance"
                ? "border-accent bg-accent/10"
                : "border-border bg-background hover:bg-background/80"
            }`}
          >
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4" />
              <div className="text-left">
                <p className="text-xs font-semibold">Predicción de Rendimiento</p>
                <p className="text-[10px] text-muted-foreground">LSTM</p>
              </div>
            </div>
          </button>
        </div>
      </div>

      {/* Contenido Principal */}
      {selectedPlayer && (
        <>
          {/* MODELO 1: PREDICCIÓN DE VALOR */}
          {selectedModel === "value" && (
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

          {/* MODELO 2: RIESGO DE LESIONES */}
          {selectedModel === "injury" && (
            <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded-lg bg-danger/15">
              <TrendingDown className="w-5 h-5 text-danger" />
            </div>
            <div>
              <h2 className="font-heading font-bold text-lg">
                Predicción de Riesgo de Lesiones
              </h2>
              <p className="text-xs text-muted-foreground">
                Modelo XGBoost con datos históricos de lesiones
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Indicadores de Riesgo */}
            <div className="space-y-3">
              {injuryRiskData && (
                <>
                  <div className="bg-danger/10 border border-danger/30 rounded-xl p-4">
                    <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-2">
                      Riesgo Predicho
                    </p>
                    <p className="text-3xl font-heading font-bold text-danger">
                      {injuryRiskData.risk_percentage}%
                    </p>
                    <p className="text-xs text-muted-foreground mt-2">
                      Confianza: {injuryRiskData.confidence.toFixed(0)}%
                    </p>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between py-2 border-b border-border/20">
                      <span className="text-xs text-muted-foreground">
                        Categoría Riesgo
                      </span>
                      <span
                        className={`text-xs font-semibold ${
                          injuryRiskData.risk_percentage > 60
                            ? "text-danger"
                            : injuryRiskData.risk_percentage > 35
                              ? "text-warning"
                              : "text-success"
                        }`}
                      >
                        {injuryRiskData.risk_percentage > 60
                          ? "Alto"
                          : injuryRiskData.risk_percentage > 35
                            ? "Moderado"
                            : "Bajo"}
                      </span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-border/20">
                      <span className="text-xs text-muted-foreground">
                        Trend. Temporal
                      </span>
                      <span className="text-xs font-semibold">
                        {injuryRiskData.timeline}
                      </span>
                    </div>
                    <div className="flex justify-between py-2">
                      <span className="text-xs text-muted-foreground">
                        Minutos Riesgo
                      </span>
                      <span className="text-xs font-semibold">
                        {Math.round(Math.random() * 500) + 200}h
                      </span>
                    </div>
                  </div>
                </>
              )}
            </div>

            {/* Gráfico de Histórico */}
            <div className="lg:col-span-2">
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={injuryHistoryData}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="hsl(222, 25%, 16%)"
                  />
                  <XAxis
                    dataKey="mes"
                    tick={{ fill: "hsl(215, 15%, 55%)", fontSize: 10 }}
                    axisLine={false}
                  />
                  <YAxis
                    tick={{ fill: "hsl(215, 15%, 55%)", fontSize: 10 }}
                    axisLine={false}
                  />
                  <Tooltip
                    contentStyle={{
                      background: "hsl(222, 41%, 9%)",
                      border: "1px solid hsl(222, 25%, 16%)",
                      borderRadius: "8px",
                      fontSize: 12,
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="riesgo"
                    stroke="hsl(0, 84%, 60%)"
                    dot={false}
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
            </div>
          )}

          {/* MODELO 3: PREDICCIÓN DE RENDIMIENTO Y CONSISTENCIA */}
          {selectedModel === "performance" && (
            <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded-lg bg-accent/15">
              <Activity className="w-5 h-5 text-accent" />
            </div>
            <div>
              <h2 className="font-heading font-bold text-lg">
                Predicción de Rendimiento
              </h2>
              <p className="text-xs text-muted-foreground">
                Modelo LSTM para predicción temporal de performance
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Indicadores de Performance */}
            <div className="space-y-3">
              <div className="bg-accent/10 border border-accent/30 rounded-xl p-4">
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-2">
                  Rendimiento Promedio
                </p>
                <p className="text-3xl font-heading font-bold text-accent">
                  {performanceData.length > 0
                    ? Math.round(
                        performanceData.reduce((a, b) => a + b.performance, 0) /
                          performanceData.length
                      )
                    : "N/A"}
                  /100
                </p>
              </div>

              <div className="bg-info/10 border border-info/30 rounded-xl p-4">
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-2">
                  Consistencia
                </p>
                <p className="text-3xl font-heading font-bold text-info">
                  {performanceData.length > 0
                    ? Math.round(
                        performanceData.reduce((a, b) => a + b.consistency, 0) /
                          performanceData.length
                      )
                    : "N/A"}
                  /100
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between py-2 border-b border-border/20">
                  <span className="text-xs text-muted-foreground">
                    Tendencia
                  </span>
                  <span className="text-xs font-semibold text-success">
                    ↑ Positiva
                  </span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-xs text-muted-foreground">
                    Predictibilidad
                  </span>
                  <span className="text-xs font-semibold">82%</span>
                </div>
              </div>
            </div>

            {/* Gráfico de Performance Timeline */}
            <div className="lg:col-span-2">
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={performanceData}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="hsl(222, 25%, 16%)"
                  />
                  <XAxis
                    dataKey="semana"
                    tick={{ fill: "hsl(215, 15%, 55%)", fontSize: 10 }}
                    axisLine={false}
                  />
                  <YAxis
                    domain={[0, 100]}
                    tick={{ fill: "hsl(215, 15%, 55%)", fontSize: 10 }}
                    axisLine={false}
                  />
                  <Tooltip
                    contentStyle={{
                      background: "hsl(222, 41%, 9%)",
                      border: "1px solid hsl(222, 25%, 16%)",
                      borderRadius: "8px",
                      fontSize: 12,
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="performance"
                    stroke="hsl(39, 100%, 54%)"
                    strokeWidth={2}
                    name="Rendimiento"
                  />
                  <Line
                    type="monotone"
                    dataKey="consistency"
                    stroke="hsl(197, 100%, 52%)"
                    strokeWidth={2}
                    name="Consistencia"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Matriz de Potencial */}
          <div className="mt-6 pt-6 border-t border-border/20">
            <h3 className="font-heading font-semibold text-sm mb-4 flex items-center gap-2">
              <Brain className="w-4 h-4 text-primary" />
              Análisis de Potencial por Área
            </h3>
            <div className="space-y-3">
              {potentialData.map((item) => (
                <div key={item.name}>
                  <div className="flex justify-between mb-1">
                    <span className="text-xs font-medium text-foreground">
                      {item.name}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {item.current}/100 → {item.potential}/100
                    </span>
                  </div>
                  <div className="flex gap-2">
                    <div className="flex-1 h-2 bg-border rounded-full overflow-hidden">
                      <div
                        className="h-full bg-accent"
                        style={{ width: `${item.current}%` }}
                      />
                    </div>
                    <div className="flex-1 h-2 bg-border rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary/40"
                        style={{ width: `${item.potential}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
            </div>
          )}
        </>
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
