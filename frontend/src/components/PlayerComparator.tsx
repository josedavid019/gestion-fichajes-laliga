import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { Plus, X, Users } from "lucide-react";
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

export const PlayerComparator = () => {
  const { data: allPlayers = [], isLoading, error } = usePlayers();
  const [selectedPlayers, setSelectedPlayers] = useState<Player[]>([]);
  const [searchTerm, setSearchTerm] = useState("");

  const addPlayer = (player: Player) => {
    if (selectedPlayers.length < 6 && !selectedPlayers.find((p) => p.id === player.id)) {
      setSelectedPlayers([...selectedPlayers, player]);
    }
  };

  const removePlayer = (id: number) => {
    setSelectedPlayers(selectedPlayers.filter((p) => p.id !== id));
  };

  const availablePlayers = allPlayers.filter(
    (p) =>
      !selectedPlayers.find((sp) => sp.id === p.id) &&
      (searchTerm === "" ||
        p.alias.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (p.current_club?.name && p.current_club.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
        `${p.first_name} ${p.last_name}`.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const comparisonData = selectedPlayers
    .sort((a, b) => (parseFloat(b.market_value_eur || "0") - parseFloat(a.market_value_eur || "0")))
    .map((p) => ({
      name: p.alias || `${p.first_name} ${p.last_name}`,
      "Valor de Mercado": parseFloat(p.market_value_eur || "0") / 1000000,
    }));

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            Comparador de Jugadores
          </CardTitle>
          <CardDescription>Selecciona y compara hasta 6 jugadores registrados</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Selector de Jugadores */}
          <div className="space-y-3">
            <label className="text-sm font-medium">Agregar Jugadores ({selectedPlayers.length}/6)</label>
            <div className="flex gap-2">
              <Input
                placeholder="Buscar por nombre o club..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="flex-1"
              />
            </div>

            {isLoading ? (
              <p className="text-center py-4">Cargando jugadores...</p>
            ) : availablePlayers.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 max-h-96 overflow-y-auto">
                {availablePlayers.map((player) => (
                  <Button
                    key={player.id}
                    variant="outline"
                    className="justify-start text-left h-auto py-2"
                    onClick={() => addPlayer(player)}
                    disabled={selectedPlayers.length >= 6}
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    <div className="flex-1">
                      <div className="font-medium text-sm">{player.alias || `${player.first_name} ${player.last_name}`}</div>
                      <div className="text-xs text-muted-foreground">{player.current_club?.name || "Sin club"}</div>
                    </div>
                  </Button>
                ))}
              </div>
            ) : (
              <p className="text-center py-4 text-muted-foreground">No se encontraron jugadores disponibles</p>
            )}
          </div>

          {/* Jugadores Seleccionados */}
          <div className="space-y-3">
            <label className="text-sm font-medium">Jugadores Seleccionados ({selectedPlayers.length})</label>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {selectedPlayers.map((player) => (
                <Card key={player.id} className="relative">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="absolute top-1 right-1 h-6 w-6 p-0"
                    onClick={() => removePlayer(player.id)}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                  <CardContent className="pt-4 pb-3">
                    <h3 className="font-semibold text-sm">{player.alias || `${player.first_name} ${player.last_name}`}</h3>
                    <p className="text-xs text-muted-foreground">{player.position || "N/A"} • {player.age ? `${player.age} años` : "Edad N/A"}</p>
                    <p className="text-xs text-muted-foreground mb-2">{player.current_club?.name || "Sin club"}</p>
                    
                    <div className="space-y-1 text-xs">
                      <div className="flex justify-between">
                        <span>Valor:</span>
                        <span className="font-medium">
                          {player.market_value_eur ? `€${(parseFloat(player.market_value_eur) / 1000000).toFixed(1)}M` : "N/A"}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Estado:</span>
                        <Badge
                          variant={player.status === "active" ? "default" : "secondary"}
                          className="text-xs"
                        >
                          {player.status}
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Comparación */}
          {selectedPlayers.length >= 2 && (
            <Tabs defaultValue="value" className="w-full">
              <TabsList>
                <TabsTrigger value="value">Valor de Mercado</TabsTrigger>
                <TabsTrigger value="stats">Estadísticas</TabsTrigger>
              </TabsList>

              {/* Valor de Mercado */}
              <TabsContent value="value" className="space-y-4">
                <div className="h-80 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={comparisonData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis label={{ value: "Valor (Millones €)", angle: -90, position: "insideLeft" }} />
                      <Tooltip formatter={(value) => [`€${value}M`, "Valor de Mercado"]} />
                      <Legend />
                      <Bar dataKey="Valor de Mercado" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Tabla de Comparación */}
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-2 px-3 font-medium">Jugador</th>
                        <th className="text-right py-2 px-3 font-medium">Valor de Mercado</th>
                        <th className="text-right py-2 px-3 font-medium">Ranking</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedPlayers
                        .sort((a, b) => (parseFloat(b.market_value_eur || "0") - parseFloat(a.market_value_eur || "0")))
                        .map((player, index) => (
                        <tr key={player.id} className="border-b hover:bg-muted/50">
                          <td className="py-3 px-3 font-medium">{player.alias || `${player.first_name} ${player.last_name}`}</td>
                          <td className="text-right py-3 px-3">
                            {player.market_value_eur ? `€${(parseFloat(player.market_value_eur) / 1000000).toFixed(1)}M` : "N/A"}
                          </td>
                          <td className="text-right py-3 px-3">
                            <Badge variant="outline" className="text-xs">
                              #{index + 1}
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </TabsContent>

              {/* Estadísticas */}
              <TabsContent value="stats">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {selectedPlayers.map((player) => (
                    <Card key={player.id}>
                      <CardHeader>
                        <CardTitle className="text-lg">{player.alias || `${player.first_name} ${player.last_name}`}</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="grid grid-cols-2 gap-3">
                          <div className="bg-blue-50 p-3 rounded">
                            <p className="text-xs text-muted-foreground">Posición</p>
                            <p className="text-lg font-bold text-blue-600">{player.position || "N/A"}</p>
                          </div>
                          <div className="bg-green-50 p-3 rounded">
                            <p className="text-xs text-muted-foreground">Edad</p>
                            <p className="text-lg font-bold text-green-600">{player.age || "N/A"}</p>
                          </div>
                          <div className="bg-yellow-50 p-3 rounded">
                            <p className="text-xs text-muted-foreground">Altura</p>
                            <p className="text-lg font-bold text-yellow-600">{player.height_cm ? `${player.height_cm}cm` : "N/A"}</p>
                          </div>
                          <div className="bg-purple-50 p-3 rounded">
                            <p className="text-xs text-muted-foreground">Peso</p>
                            <p className="text-lg font-bold text-purple-600">{player.weight_kg ? `${player.weight_kg}kg` : "N/A"}</p>
                          </div>
                        </div>
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span>Pierna preferida:</span>
                            <span className="font-medium">{player.preferred_foot || "N/A"}</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span>Nacionalidad:</span>
                            <span className="font-medium">{player.nationality?.name || "N/A"}</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>
            </Tabs>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
