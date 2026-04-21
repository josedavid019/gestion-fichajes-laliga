import { useState, useMemo } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from "recharts";
import { Plus, X, Users, Loader2 } from "lucide-react";
import { usePlayers } from "@/hooks/usePlayers";

interface Player {
  id: number;
  first_name: string;
  last_name: string;
  position: string;
  age: number | null;
  current_club?: {
    id: number;
    name: string;
    city: string;
    logo_url: string;
  } | null;
  nationality?: {
    id: number;
    name: string;
    code: string;
    flag_url: string;
  } | null;
  market_value_eur: string | null;
  photo_url: string;
  height_cm: number | null;
  weight_kg: number | null;
  preferred_foot: string;
  shirt_number: number | null;
}

interface ComparablePlayer extends Player {
  displayName: string;
  marketValue: number;
  stats: {
    goals: number;
    assists: number;
    matches: number;
    rating: number;
  };
  attributes: {
    pace: number;
    shooting: number;
    passing: number;
    dribbling: number;
    defense: number;
    physical: number;
  };
}

// Función para convertir valor de mercado
const parseMarketValue = (value: string | null): number => {
  if (!value) return 0;
  const parsed = parseInt(value.replace(/[^0-9]/g, ""));
  return isNaN(parsed) ? 0 : Math.round(parsed / 1000000); // Convertir a millones
};

// Función para generar atributos basados en posición y otros datos
const generateAttributes = (player: Player): ComparablePlayer["attributes"] => {
  const position = player.position || "";
  const age = player.age || 25;
  const height = player.height_cm || 180;

  // Valores base por posición
  const baseAttrs: Record<string, ComparablePlayer["attributes"]> = {
    ST: { pace: 85, shooting: 90, passing: 75, dribbling: 85, defense: 35, physical: 80 },
    CF: { pace: 82, shooting: 88, passing: 78, dribbling: 82, defense: 38, physical: 82 },
    LW: { pace: 88, shooting: 82, passing: 80, dribbling: 87, defense: 40, physical: 78 },
    RW: { pace: 88, shooting: 82, passing: 80, dribbling: 87, defense: 40, physical: 78 },
    AM: { pace: 80, shooting: 78, passing: 85, dribbling: 82, defense: 45, physical: 75 },
    CM: { pace: 75, shooting: 70, passing: 85, dribbling: 75, defense: 75, physical: 80 },
    DM: { pace: 72, shooting: 60, passing: 78, dribbling: 68, defense: 85, physical: 85 },
    CB: { pace: 70, shooting: 50, passing: 75, dribbling: 50, defense: 88, physical: 88 },
    LB: { pace: 82, shooting: 55, passing: 75, dribbling: 70, defense: 85, physical: 82 },
    RB: { pace: 82, shooting: 55, passing: 75, dribbling: 70, defense: 85, physical: 82 },
    GK: { pace: 50, shooting: 15, passing: 60, dribbling: 20, defense: 80, physical: 75 },
  };

  const attrs = baseAttrs[position] || { pace: 75, shooting: 70, passing: 75, dribbling: 75, defense: 70, physical: 75 };

  // Ajustar por edad
  const ageModifier = age > 28 ? -2 : age < 22 ? 1 : 0;

  return {
    pace: Math.min(99, Math.max(20, attrs.pace + ageModifier)),
    shooting: Math.min(99, Math.max(20, attrs.shooting + ageModifier)),
    passing: Math.min(99, Math.max(20, attrs.passing + ageModifier)),
    dribbling: Math.min(99, Math.max(20, attrs.dribbling + ageModifier)),
    defense: Math.min(99, Math.max(20, attrs.defense + ageModifier)),
    physical: Math.min(99, Math.max(20, attrs.physical + ageModifier)),
  };
};

// Función para generar estadísticas basadas en posición
const generateStats = (player: Player): ComparablePlayer["stats"] => {
  const position = player.position || "";
  const age = player.age || 25;

  if (position === "GK") {
    return { goals: 0, assists: 0, matches: 30, rating: 7.0 };
  }
  if (position.startsWith("C") || position.startsWith("D")) {
    return { goals: 2, assists: 3, matches: 28, rating: 7.2 };
  }
  if (position === "AM") {
    return { goals: 6, assists: 8, matches: 25, rating: 7.5 };
  }
  // Delanteros y extremos
  return { goals: 10, assists: 5, matches: 26, rating: 7.4 };
};

export const PlayerComparator = () => {
  const { data: allPlayers = [], isLoading } = usePlayers();
  const [selectedPlayerIds, setSelectedPlayerIds] = useState<number[]>([]);
  const [searchTerm, setSearchTerm] = useState("");

  // Convertir jugadores a formato comparable
  const comparablePlayers = useMemo(() => {
    return allPlayers.map((p): ComparablePlayer => ({
      ...p,
      displayName: `${p.first_name} ${p.last_name}`,
      marketValue: parseMarketValue(p.market_value_eur),
      stats: generateStats(p),
      attributes: generateAttributes(p),
    }));
  }, [allPlayers]);

  // Obtener jugadores seleccionados
  const selectedPlayers = useMemo(() => {
    return comparablePlayers.filter((p) => selectedPlayerIds.includes(p.id));
  }, [comparablePlayers, selectedPlayerIds]);

  const addPlayer = (playerId: number) => {
    if (!selectedPlayerIds.includes(playerId) && selectedPlayerIds.length < 2) {
      setSelectedPlayerIds([...selectedPlayerIds, playerId]);
    }
  };

  const removePlayer = (playerId: number) => {
    setSelectedPlayerIds(selectedPlayerIds.filter((id) => id !== playerId));
  };

  const availablePlayers = useMemo(() => {
    return comparablePlayers.filter(
      (p) =>
        !selectedPlayerIds.includes(p.id) &&
        (p.displayName.toLowerCase().includes(searchTerm.toLowerCase()) ||
          p.current_club?.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          p.position?.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  }, [comparablePlayers, selectedPlayerIds, searchTerm]);

  const comparisonData = selectedPlayers.map((p) => ({
    name: p.last_name,
    "Valor Actual": p.marketValue,
  }));

  const attributesData = selectedPlayers[0]
    ? Object.entries(selectedPlayers[0].attributes).map(([key, value]) => ({
        name: key.charAt(0).toUpperCase() + key.slice(1),
        [selectedPlayers[0].displayName]: value,
        ...(selectedPlayers[1] && {
          [selectedPlayers[1].displayName]: selectedPlayers[1].attributes[key as keyof typeof selectedPlayers[0]["attributes"]],
        }),
      }))
    : [];

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            Comparador de Jugadores
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-6 h-6 animate-spin text-primary" />
            <span className="ml-2">Cargando {allPlayers.length} jugadores...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            Comparador de Jugadores
          </CardTitle>
          <CardDescription>Selecciona 2 jugadores de los {allPlayers.length} disponibles para compararlos</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Selector de Jugadores */}
          <div className="space-y-3">
            <label className="text-sm font-medium">Buscar y Agregar Jugadores</label>
            <div className="flex gap-2">
              <Input
                placeholder="Busca por nombre, club o posición..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="flex-1"
              />
            </div>

            {availablePlayers.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-64 overflow-y-auto">
                {availablePlayers.slice(0, 20).map((player) => (
                  <Button
                    key={player.id}
                    variant="outline"
                    className="justify-start text-left h-auto py-2"
                    onClick={() => addPlayer(player.id)}
                    disabled={selectedPlayerIds.length >= 2}
                  >
                    <Plus className="w-4 h-4 mr-2 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm truncate">{player.displayName}</div>
                      <div className="text-xs text-muted-foreground truncate">
                        {player.current_club?.name} • {player.position} • {player.age} años
                      </div>
                    </div>
                    <div className="text-xs font-semibold ml-2 flex-shrink-0 text-primary">
                      €{player.marketValue}M
                    </div>
                  </Button>
                ))}
              </div>
            )}
            {availablePlayers.length === 0 && searchTerm && (
              <div className="text-center py-6 text-sm text-muted-foreground">
                No se encontraron jugadores con "{searchTerm}"
              </div>
            )}
          </div>

          {/* Jugadores Seleccionados */}
          <div className="space-y-3">
            <label className="text-sm font-medium">
              Jugadores Seleccionados ({selectedPlayerIds.length}/2)
            </label>
            {selectedPlayers.length === 0 ? (
              <div className="p-4 text-center text-sm text-muted-foreground border-2 border-dashed rounded-lg">
                Selecciona 2 jugadores para compararlos
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {selectedPlayers.map((player) => (
                  <Card key={player.id} className="relative overflow-hidden">
                    {player.photo_url && (
                      <div className="absolute inset-0 opacity-10">
                        <img src={player.photo_url} alt={player.displayName} className="w-full h-full object-cover" />
                      </div>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      className="absolute top-2 right-2 h-6 w-6 p-0 z-10"
                      onClick={() => removePlayer(player.id)}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                    <CardContent className="pt-4 pb-4 relative z-0">
                      <h3 className="font-semibold text-base">{player.displayName}</h3>
                      <p className="text-xs text-muted-foreground mb-3">
                        {player.position} • {player.age} años • {player.current_club?.name}
                      </p>

                      <div className="space-y-2 text-xs">
                        <div className="flex justify-between items-center">
                          <span className="text-muted-foreground">Valor:</span>
                          <span className="font-semibold text-primary">€{player.marketValue}M</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-muted-foreground">Altura:</span>
                          <span>{player.height_cm} cm</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-muted-foreground">Pierna:</span>
                          <span>{player.preferred_foot}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-muted-foreground">Dorsal:</span>
                          <span>{player.shirt_number || "N/A"}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* Tabs de Comparación */}
          {selectedPlayers.length === 2 && (
            <Tabs defaultValue="value" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="value">Valor</TabsTrigger>
                <TabsTrigger value="info">Info</TabsTrigger>
                <TabsTrigger value="attributes">Atributos</TabsTrigger>
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
                      <Tooltip formatter={(value) => `€${value}M`} />
                      <Legend />
                      <Bar dataKey="Valor Actual" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Tabla de Comparación */}
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4 font-semibold">Jugador</th>
                        <th className="text-right py-3 px-4 font-semibold">Valor Mercado</th>
                        <th className="text-right py-3 px-4 font-semibold">Posición</th>
                        <th className="text-right py-3 px-4 font-semibold">Edad</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedPlayers.map((player) => (
                        <tr key={player.id} className="border-b hover:bg-muted/50">
                          <td className="py-3 px-4 font-semibold">{player.displayName}</td>
                          <td className="text-right py-3 px-4">
                            <Badge variant="default">€{player.marketValue}M</Badge>
                          </td>
                          <td className="text-right py-3 px-4">{player.position}</td>
                          <td className="text-right py-3 px-4">{player.age} años</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </TabsContent>

              {/* Información General */}
              <TabsContent value="info" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {selectedPlayers.map((player) => (
                    <Card key={player.id}>
                      <CardHeader>
                        <CardTitle className="text-base">{player.displayName}</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="grid grid-cols-2 gap-3 text-sm">
                          <div>
                            <p className="text-xs text-muted-foreground">Posición</p>
                            <p className="font-semibold">{player.position}</p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground">Edad</p>
                            <p className="font-semibold">{player.age} años</p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground">Altura</p>
                            <p className="font-semibold">{player.height_cm ? `${player.height_cm} cm` : "N/A"}</p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground">Peso</p>
                            <p className="font-semibold">{player.weight_kg ? `${player.weight_kg} kg` : "N/A"}</p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground">Pierna</p>
                            <p className="font-semibold">{player.preferred_foot}</p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground">Dorsal</p>
                            <p className="font-semibold">#{player.shirt_number || "N/A"}</p>
                          </div>
                          <div className="col-span-2">
                            <p className="text-xs text-muted-foreground">Club</p>
                            <p className="font-semibold">{player.current_club?.name}</p>
                          </div>
                          <div className="col-span-2">
                            <p className="text-xs text-muted-foreground">Nacionalidad</p>
                            <p className="font-semibold">{player.nationality?.name}</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              {/* Atributos */}
              <TabsContent value="attributes" className="space-y-4">
                <div className="h-96 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={attributesData}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="name" />
                      <PolarRadiusAxis angle={90} domain={[0, 100]} />
                      <Radar
                        name={selectedPlayers[0]?.displayName}
                        dataKey={selectedPlayers[0]?.displayName}
                        stroke="#3b82f6"
                        fill="#3b82f6"
                        fillOpacity={0.6}
                      />
                      {selectedPlayers[1] && (
                        <Radar
                          name={selectedPlayers[1]?.displayName}
                          dataKey={selectedPlayers[1]?.displayName}
                          stroke="#10b981"
                          fill="#10b981"
                          fillOpacity={0.3}
                        />
                      )}
                      <Legend />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </TabsContent>

              {/* Estadísticas */}
              <TabsContent value="stats">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {selectedPlayers.map((player) => (
                    <Card key={player.id}>
                      <CardHeader>
                        <CardTitle className="text-base">{player.displayName}</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="grid grid-cols-2 gap-3">
                          <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg">
                            <p className="text-xs text-muted-foreground mb-1">Goles</p>
                            <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                              {player.stats.goals}
                            </p>
                          </div>
                          <div className="bg-green-50 dark:bg-green-950 p-4 rounded-lg">
                            <p className="text-xs text-muted-foreground mb-1">Asistencias</p>
                            <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                              {player.stats.assists}
                            </p>
                          </div>
                          <div className="bg-yellow-50 dark:bg-yellow-950 p-4 rounded-lg">
                            <p className="text-xs text-muted-foreground mb-1">Partidos</p>
                            <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                              {player.stats.matches}
                            </p>
                          </div>
                          <div className="bg-purple-50 dark:bg-purple-950 p-4 rounded-lg">
                            <p className="text-xs text-muted-foreground mb-1">Rating</p>
                            <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                              {player.stats.rating.toFixed(1)}
                            </p>
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
