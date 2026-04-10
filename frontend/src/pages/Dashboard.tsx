import { useState, useMemo } from "react";
import { Search, SlidersHorizontal, X, Footprints, Target, ArrowRightLeft, DollarSign, Ruler, Calendar } from "lucide-react";
import { Input } from "@/components/ui/input";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription,
} from "@/components/ui/dialog";

const players = [
  { name: "Lamine Yamal", position: "Extremo", height: 180, team: "FC Barcelona", age: 17, value: "€180M", confidence: 97, goals: 10, assists: 15, foot: "Izquierda", image: "https://img.a.transfermarkt.technology/portrait/header/766515-1730797371.png" },
  { name: "Jude Bellingham", position: "Mediocampista", height: 186, team: "Real Madrid", age: 21, value: "€150M", confidence: 94, goals: 23, assists: 13, foot: "Derecha", image: "https://img.a.transfermarkt.technology/portrait/header/581678-1694590415.png" },
  { name: "Florian Wirtz", position: "Mediocampista", height: 176, team: "Bayer Leverkusen", age: 21, value: "€130M", confidence: 91, goals: 18, assists: 20, foot: "Derecha", image: "https://img.a.transfermarkt.technology/portrait/header/521361-1694590561.png" },
  { name: "Jamal Musiala", position: "Mediocampista", height: 183, team: "Bayern Múnich", age: 21, value: "€120M", confidence: 89, goals: 12, assists: 16, foot: "Derecha", image: "https://img.a.transfermarkt.technology/portrait/header/580195-1694590337.png" },
  { name: "Pedri", position: "Mediocampista", height: 174, team: "FC Barcelona", age: 21, value: "€100M", confidence: 93, goals: 8, assists: 11, foot: "Derecha", image: "https://img.a.transfermarkt.technology/portrait/header/901307-1694590620.png" },
  { name: "Gavi", position: "Mediocampista", height: 173, team: "FC Barcelona", age: 20, value: "€90M", confidence: 88, goals: 6, assists: 9, foot: "Derecha", image: "https://img.a.transfermarkt.technology/portrait/header/855550-1694590495.png" },
  { name: "Endrick", position: "Delantero", height: 173, team: "Real Madrid", age: 18, value: "€60M", confidence: 85, goals: 14, assists: 4, foot: "Derecha", image: "https://img.a.transfermarkt.technology/portrait/header/988629-1694590680.png" },
  { name: "Alejandro Garnacho", position: "Extremo", height: 180, team: "Manchester United", age: 20, value: "€50M", confidence: 82, goals: 10, assists: 7, foot: "Derecha", image: "https://img.a.transfermarkt.technology/portrait/header/741898-1694590740.png" },
  { name: "Pau Cubarsí", position: "Defensa", height: 184, team: "FC Barcelona", age: 17, value: "€60M", confidence: 90, goals: 1, assists: 3, foot: "Derecha", image: "https://img.a.transfermarkt.technology/portrait/header/1072498-1710928050.png" },
  { name: "Kobbie Mainoo", position: "Mediocampista", height: 178, team: "Manchester United", age: 19, value: "€55M", confidence: 84, goals: 5, assists: 8, foot: "Derecha", image: "https://img.a.transfermarkt.technology/portrait/header/975964-1710928110.png" },
  { name: "Giorgi Mamardashvili", position: "Portero", height: 197, team: "Valencia CF", age: 23, value: "€40M", confidence: 87, goals: 0, assists: 0, foot: "Derecha", image: "https://img.a.transfermarkt.technology/portrait/header/597399-1694590800.png" },
  { name: "Sandro Tonali", position: "Mediocampista", height: 181, team: "Newcastle United", age: 24, value: "€45M", confidence: 80, goals: 7, assists: 10, foot: "Derecha", image: "https://img.a.transfermarkt.technology/portrait/header/539662-1694590860.png" },
];

const positions = ["Todas", "Delantero", "Extremo", "Mediocampista", "Defensa", "Portero"];
const heightRanges = [
  { label: "Todas", min: 0, max: 300 },
  { label: "< 175 cm", min: 0, max: 174 },
  { label: "175 - 180 cm", min: 175, max: 180 },
  { label: "181 - 185 cm", min: 181, max: 185 },
  { label: "> 185 cm", min: 186, max: 300 },
];

type Player = typeof players[0];

function StatItem({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string | number }) {
  return (
    <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50 border border-border/30">
      <div className="w-8 h-8 rounded-md bg-primary/15 flex items-center justify-center shrink-0">
        <Icon className="w-4 h-4 text-primary" />
      </div>
      <div>
        <p className="text-[11px] text-muted-foreground">{label}</p>
        <p className="text-sm font-semibold text-foreground">{value}</p>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [searchName, setSearchName] = useState("");
  const [selectedPosition, setSelectedPosition] = useState("Todas");
  const [selectedHeight, setSelectedHeight] = useState("Todas");
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);

  const filtered = useMemo(() => {
    const hr = heightRanges.find((h) => h.label === selectedHeight) || heightRanges[0];
    return players.filter((p) => {
      const nameMatch = p.name.toLowerCase().includes(searchName.toLowerCase());
      const posMatch = selectedPosition === "Todas" || p.position === selectedPosition;
      const heightMatch = p.height >= hr.min && p.height <= hr.max;
      return nameMatch && posMatch && heightMatch;
    });
  }, [searchName, selectedPosition, selectedHeight]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-heading font-bold">Búsqueda de Jugadores</h1>
        <p className="text-sm text-muted-foreground mt-1">Filtra jugadores por nombre, posición o estatura</p>
      </div>

      {/* Filters */}
      <div className="glass-card p-5">
        <div className="flex items-center gap-2 mb-4">
          <SlidersHorizontal className="w-4 h-4 text-primary" />
          <h3 className="font-heading font-semibold text-sm">Filtros</h3>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="space-y-1.5">
            <label className="text-xs text-muted-foreground">Nombre</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Buscar por nombre..."
                value={searchName}
                onChange={(e) => setSearchName(e.target.value)}
                className="pl-9 bg-card border-border/50"
              />
            </div>
          </div>
          <div className="space-y-1.5">
            <label className="text-xs text-muted-foreground">Posición</label>
            <Select value={selectedPosition} onValueChange={setSelectedPosition}>
              <SelectTrigger className="bg-card border-border/50">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {positions.map((p) => (
                  <SelectItem key={p} value={p}>{p}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1.5">
            <label className="text-xs text-muted-foreground">Estatura</label>
            <Select value={selectedHeight} onValueChange={setSelectedHeight}>
              <SelectTrigger className="bg-card border-border/50">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {heightRanges.map((h) => (
                  <SelectItem key={h.label} value={h.label}>{h.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="glass-card p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-heading font-semibold text-sm">Resultados</h3>
          <span className="text-xs text-muted-foreground">{filtered.length} jugador{filtered.length !== 1 ? "es" : ""}</span>
        </div>

        {filtered.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground">
            <Search className="w-10 h-10 mx-auto mb-3 opacity-40" />
            <p className="text-sm">No se encontraron jugadores con esos filtros</p>
          </div>
        ) : (
          <div className="space-y-2">
            {filtered.map((player) => (
              <div
                key={player.name}
                onClick={() => setSelectedPlayer(player)}
                className="flex items-center justify-between p-3 rounded-lg border border-border/30 hover:border-primary/30 hover:bg-primary/5 transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-full bg-primary/15 flex items-center justify-center text-[10px] font-bold text-primary shrink-0">
                    {player.position.slice(0, 3).toUpperCase()}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-foreground">{player.name}</p>
                    <p className="text-[11px] text-muted-foreground">{player.team} · {player.position} · {player.height} cm · {player.age} años</p>
                  </div>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-sm font-semibold gradient-text">{player.value}</p>
                  <p className="text-[10px] text-muted-foreground">Conf: {player.confidence}%</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Player Detail Dialog */}
      <Dialog open={!!selectedPlayer} onOpenChange={(open) => !open && setSelectedPlayer(null)}>
        <DialogContent className="sm:max-w-md bg-card border-border/50">
          {selectedPlayer && (
            <>
              <DialogHeader className="items-center text-center">
                <div className="w-28 h-28 rounded-full overflow-hidden border-2 border-primary/30 mx-auto mb-2 bg-muted">
                  <img
                    src={selectedPlayer.image}
                    alt={selectedPlayer.name}
                    className="w-full h-full object-cover object-top"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = "/placeholder.svg";
                    }}
                  />
                </div>
                <DialogTitle className="text-xl font-heading">{selectedPlayer.name}</DialogTitle>
                <DialogDescription>{selectedPlayer.team}</DialogDescription>
              </DialogHeader>

              <div className="grid grid-cols-2 gap-2 mt-2">
                <StatItem icon={Target} label="Posición" value={selectedPlayer.position} />
                <StatItem icon={Ruler} label="Estatura" value={`${selectedPlayer.height} cm`} />
                <StatItem icon={Target} label="Goles" value={selectedPlayer.goals} />
                <StatItem icon={ArrowRightLeft} label="Pases / Asistencias" value={selectedPlayer.assists} />
                <StatItem icon={Footprints} label="Pierna hábil" value={selectedPlayer.foot} />
                <StatItem icon={DollarSign} label="Precio" value={selectedPlayer.value} />
                <StatItem icon={Calendar} label="Edad" value={`${selectedPlayer.age} años`} />
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
