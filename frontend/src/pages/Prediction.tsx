import { TrendingUp, BarChart3, User, Zap } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from "recharts";

const playerData = {
  name: "Florian Wirtz",
  age: 21,
  position: "Mediapunta",
  club: "Bayer Leverkusen",
  estimatedValue: "€135M",
  variables: [
    { label: "Goles/temporada", value: "18" },
    { label: "Asistencias/temporada", value: "12" },
    { label: "Minutos jugados", value: "2,840" },
    { label: "Rating promedio", value: "8.2" },
    { label: "Edad", value: "21" },
    { label: "Contrato restante", value: "3 años" },
  ],
  explanation: "El modelo XGBoost predice un valor de €135M basado en la alta contribución goleadora (18 goles + 12 asistencias), la juventud del jugador (21 años) con margen de mejora, la duración del contrato (3 años) y su rendimiento consistente (rating 8.2). Los factores más influyentes son: edad (28%), goles (22%) y rating (18%).",
};

const radarData = [
  { skill: "Ritmo", A: 88, B: 82 },
  { skill: "Tiro", A: 84, B: 78 },
  { skill: "Pase", A: 86, B: 90 },
  { skill: "Regate", A: 90, B: 85 },
  { skill: "Defensa", A: 42, B: 55 },
  { skill: "Físico", A: 68, B: 72 },
];

const comparisonData = [
  { name: "Wirtz", value: 135 },
  { name: "Musiala", value: 120 },
  { name: "Pedri", value: 100 },
  { name: "Szoboszlai", value: 70 },
  { name: "Olmo", value: 60 },
];

export default function Prediction() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-heading font-bold">Predicción de Valor</h1>
        <p className="text-sm text-muted-foreground mt-1">Modelo ML para estimación de valor de mercado</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Player Info */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-14 h-14 rounded-full bg-primary/15 flex items-center justify-center">
              <User className="w-7 h-7 text-primary" />
            </div>
            <div>
              <h3 className="font-heading font-bold text-lg">{playerData.name}</h3>
              <p className="text-xs text-muted-foreground">{playerData.position} · {playerData.club}</p>
            </div>
          </div>

          <div className="text-center py-4 mb-5 rounded-xl glow-border bg-primary/5">
            <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1">Valor Estimado</p>
            <p className="text-3xl font-heading font-bold gradient-text">{playerData.estimatedValue}</p>
          </div>

          <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Variables de Entrada</h4>
          <div className="space-y-2">
            {playerData.variables.map((v) => (
              <div key={v.label} className="flex justify-between py-1.5 border-b border-border/20">
                <span className="text-xs text-muted-foreground">{v.label}</span>
                <span className="text-xs font-medium text-foreground">{v.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Explanation + Radar */}
        <div className="lg:col-span-2 space-y-4">
          {/* Explanation */}
          <div className="glass-card p-5">
            <div className="flex items-center gap-2 mb-3">
              <Zap className="w-4 h-4 text-warning" />
              <h3 className="font-heading font-semibold text-sm">Explicación del Modelo</h3>
            </div>
            <p className="text-sm text-foreground/85 leading-relaxed">{playerData.explanation}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Radar Chart */}
            <div className="glass-card p-5">
              <h3 className="font-heading font-semibold text-sm mb-4">Perfil vs Comparables</h3>
              <ResponsiveContainer width="100%" height={220}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="hsl(222, 25%, 16%)" />
                  <PolarAngleAxis dataKey="skill" tick={{ fill: 'hsl(215, 15%, 55%)', fontSize: 10 }} />
                  <PolarRadiusAxis tick={false} axisLine={false} />
                  <Radar name="Wirtz" dataKey="A" stroke="hsl(160, 84%, 39%)" fill="hsl(160, 84%, 39%)" fillOpacity={0.2} />
                  <Radar name="Comparable" dataKey="B" stroke="hsl(187, 92%, 45%)" fill="hsl(187, 92%, 45%)" fillOpacity={0.1} />
                </RadarChart>
              </ResponsiveContainer>
            </div>

            {/* Comparison */}
            <div className="glass-card p-5">
              <div className="flex items-center gap-2 mb-4">
                <BarChart3 className="w-4 h-4 text-accent" />
                <h3 className="font-heading font-semibold text-sm">Comparación (€M)</h3>
              </div>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={comparisonData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(222, 25%, 16%)" />
                  <XAxis type="number" tick={{ fill: 'hsl(215, 15%, 55%)', fontSize: 10 }} axisLine={false} />
                  <YAxis type="category" dataKey="name" tick={{ fill: 'hsl(215, 15%, 55%)', fontSize: 10 }} axisLine={false} width={70} />
                  <Tooltip contentStyle={{ background: 'hsl(222, 41%, 9%)', border: '1px solid hsl(222, 25%, 16%)', borderRadius: '8px', fontSize: 12 }} />
                  <Bar dataKey="value" fill="hsl(160, 84%, 39%)" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
