import { X } from "lucide-react";
import { Button } from "@/components/ui/button";

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

interface PlayerCardProps {
  player: Player;
  onClose: () => void;
}

export default function PlayerCard({ player, onClose }: PlayerCardProps) {
  const marketValue = player.market_value_eur
    ? `€${(parseFloat(player.market_value_eur as string) / 1000000).toFixed(1)}M`
    : "N/A";

  const statusColors: Record<string, string> = {
    active: "bg-success/10 text-success",
    injured: "bg-warning/10 text-warning",
    suspended: "bg-destructive/10 text-destructive",
    retired: "bg-muted/10 text-muted-foreground",
    free_agent: "bg-blue-500/10 text-blue-500",
  };

  const statusLabels: Record<string, string> = {
    active: "Activo",
    injured: "Lesionado",
    suspended: "Sancionado",
    retired: "Retirado",
    free_agent: "Libre",
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="glass-card w-full max-w-2xl max-h-96 overflow-y-auto p-6 relative">
        <Button
          variant="ghost"
          size="sm"
          className="absolute top-4 right-4 z-10"
          onClick={onClose}
        >
          <X className="w-4 h-4" />
        </Button>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Left: Photo */}
          <div className="flex flex-col items-center">
            {player.photo_url ? (
              <img
                src={player.photo_url}
                alt={player.alias}
                className="w-32 h-32 rounded-full object-cover mb-3 border-2 border-primary/20"
              />
            ) : (
              <div className="w-32 h-32 rounded-full bg-muted/30 mb-3 flex items-center justify-center border-2 border-primary/20">
                <span className="text-4xl">👤</span>
              </div>
            )}
            <h2 className="text-lg font-heading font-bold text-center">{player.alias}</h2>
            <p className="text-xs text-muted-foreground mt-1">{player.current_club?.name || "Sin club"}</p>
          </div>

          {/* Middle: Stats */}
          <div className="space-y-3">
            <div className="bg-primary/10 p-3 rounded-lg">
              <p className="text-xs text-muted-foreground">Posición</p>
              <p className="text-lg font-bold">{player.position || "-"}</p>
            </div>
            <div className="bg-primary/10 p-3 rounded-lg">
              <p className="text-xs text-muted-foreground">Edad</p>
              <p className="text-lg font-bold">{player.age || "-"} años</p>
            </div>
            <div className="bg-primary/10 p-3 rounded-lg">
              <p className="text-xs text-muted-foreground">Nacionalidad</p>
              <p className="text-lg font-bold">{player.nationality?.name || "-"}</p>
            </div>
          </div>

          {/* Right: More Info */}
          <div className="space-y-3">
            <div className="bg-emerald-500/10 p-3 rounded-lg">
              <p className="text-xs text-muted-foreground">Valor Mercado</p>
              <p className="text-lg font-bold gradient-text">{marketValue}</p>
            </div>
            <div className="bg-blue-500/10 p-3 rounded-lg">
              <p className="text-xs text-muted-foreground">Estado</p>
              <span
                className={`inline-block text-xs px-3 py-1 rounded-full font-medium ${
                  statusColors[player.status] || "bg-muted/10 text-muted-foreground"
                }`}
              >
                {statusLabels[player.status] || player.status}
              </span>
            </div>
          </div>
        </div>

        {/* Close Button */}
        <Button onClick={onClose} className="w-full mt-6">
          Cerrar
        </Button>
      </div>
    </div>
  );
}
