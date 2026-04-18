import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from "recharts";
import { Plus, X, TrendingUp, DollarSign, Users } from "lucide-react";

interface Player {
  id: string;
  name: string;
  position: string;
  age: number;
  club: string;
  nationality: string;
  marketValue: number;
  predictedValue: number;
  stats: {
    goals: number;
    assists: number;
    matches: number;
    rating: number;
  };
  form: { month: string; value: number }[];
  attributes: {
    pace: number;
    shooting: number;
    passing: number;
    dribbling: number;
    defense: number;
    physical: number;
  };
}

const mockPlayers: Player[] = [
  {
    id: "1",
    name: "Vinícius Júnior",
    position: "LW",
    age: 24,
    club: "Real Madrid",
    nationality: "Brasil",
    marketValue: 180,
    predictedValue: 200,
    stats: { goals: 15, assists: 8, matches: 28, rating: 8.5 },
    form: [
      { month: "Ago", value: 150 },
      { month: "Sep", value: 155 },
      { month: "Oct", value: 165 },
      { month: "Nov", value: 175 },
      { month: "Dic", value: 185 },
    ],
    attributes: { pace: 94, shooting: 86, passing: 81, dribbling: 91, defense: 40, physical: 78 },
  },
  {
    id: "2",
    name: "Jude Bellingham",
    position: "CM",
    age: 21,
    club: "Real Madrid",
    nationality: "Inglaterra",
    marketValue: 120,
    predictedValue: 160,
    stats: { goals: 8, assists: 5, matches: 25, rating: 8.2 },
    form: [
      { month: "Ago", value: 90 },
      { month: "Sep", value: 105 },
      { month: "Oct", value: 115 },
      { month: "Nov", value: 125 },
      { month: "Dic", value: 135 },
    ],
    attributes: { pace: 85, shooting: 76, passing: 84, dribbling: 80, defense: 79, physical: 87 },
  },
  {
    id: "3",
    name: "Kylian Mbappé",
    position: "ST",
    age: 25,
    club: "Real Madrid",
    nationality: "Francia",
    marketValue: 200,
    predictedValue: 190,
    stats: { goals: 18, assists: 6, matches: 30, rating: 8.7 },
    form: [
      { month: "Ago", value: 195 },
      { month: "Sep", value: 200 },
      { month: "Oct", value: 205 },
      { month: "Nov", value: 200 },
      { month: "Dic", value: 190 },
    ],
    attributes: { pace: 97, shooting: 94, passing: 80, dribbling: 92, defense: 38, physical: 76 },
  },
];

export const PlayerComparator = () => {
  const [selectedPlayers, setSelectedPlayers] = useState<Player[]>([mockPlayers[0]]);
  const [searchTerm, setSearchTerm] = useState("");

  const addPlayer = (player: Player) => {
    if (!selectedPlayers.find((p) => p.id === player.id)) {
      setSelectedPlayers([...selectedPlayers, player]);
    }
  };

  const removePlayer = (id: string) => {
    setSelectedPlayers(selectedPlayers.filter((p) => p.id !== id));
  };

  const availablePlayers = mockPlayers.filter(
    (p) =>
      !selectedPlayers.find((sp) => sp.id === p.id) &&
      (p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.club.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const comparisonData = selectedPlayers.map((p) => ({
    name: p.name.split(" ")[p.name.split(" ").length - 1],
    "Valor Actual": p.marketValue,
    "Predicción": p.predictedValue,
    Diferencia: p.predictedValue - p.marketValue,
  }));

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            Comparador de Jugadores
          </CardTitle>
          <CardDescription>Selecciona y compara jugadores, visualiza predicciones de valor de mercado</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Selector de Jugadores */}
          <div className="space-y-3">
            <label className="text-sm font-medium">Agregar Jugadores</label>
            <div className="flex gap-2">
              <Input
                placeholder="Buscar por nombre o club..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="flex-1"
              />
            </div>

            {availablePlayers.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 max-h-40 overflow-y-auto">
                {availablePlayers.map((player) => (
                  <Button
                    key={player.id}
                    variant="outline"
                    className="justify-start text-left h-auto py-2"
                    onClick={() => addPlayer(player)}
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    <div className="flex-1">
                      <div className="font-medium text-sm">{player.name}</div>
                      <div className="text-xs text-muted-foreground">{player.club}</div>
                    </div>
                  </Button>
                ))}
              </div>
            )}
          </div>

          {/* Jugadores Seleccionados */}
          <div className="space-y-3">
            <label className="text-sm font-medium">Jugadores Seleccionados ({selectedPlayers.length})</label>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
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
                    <h3 className="font-semibold text-sm">{player.name}</h3>
                    <p className="text-xs text-muted-foreground">{player.position} • {player.age} años</p>
                    <p className="text-xs text-muted-foreground mb-2">{player.club}</p>
                    
                    <div className="space-y-1 text-xs">
                      <div className="flex justify-between">
                        <span>Valor Actual:</span>
                        <span className="font-medium">${player.marketValue}M</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Predicción:</span>
                        <span className="font-medium text-green-600">${player.predictedValue}M</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Cambio:</span>
                        <Badge
                          variant={player.predictedValue >= player.marketValue ? "default" : "secondary"}
                          className="text-xs"
                        >
                          {player.predictedValue >= player.marketValue ? "+" : ""}
                          {player.predictedValue - player.marketValue}M
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Tabs de Comparación */}
          {selectedPlayers.length > 0 && (
            <Tabs defaultValue="value" className="w-full">
              <TabsList>
                <TabsTrigger value="value">Valor de Mercado</TabsTrigger>
                <TabsTrigger value="form">Forma</TabsTrigger>
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
                      <YAxis label={{ value: "Valor (Millones $)", angle: -90, position: "insideLeft" }} />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="Valor Actual" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                      <Bar dataKey="Predicción" fill="#10b981" radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Tabla de Comparación */}
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-2 px-3 font-medium">Jugador</th>
                        <th className="text-right py-2 px-3 font-medium">Valor Actual</th>
                        <th className="text-right py-2 px-3 font-medium">Predicción</th>
                        <th className="text-right py-2 px-3 font-medium">Cambio</th>
                        <th className="text-right py-2 px-3 font-medium">% Cambio</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedPlayers.map((player) => {
                        const change = player.predictedValue - player.marketValue;
                        const percentChange = ((change / player.marketValue) * 100).toFixed(1);
                        return (
                          <tr key={player.id} className="border-b hover:bg-muted/50">
                            <td className="py-3 px-3 font-medium">{player.name}</td>
                            <td className="text-right py-3 px-3">${player.marketValue}M</td>
                            <td className="text-right py-3 px-3 font-semibold text-green-600">${player.predictedValue}M</td>
                            <td className="text-right py-3 px-3">
                              <Badge variant={change >= 0 ? "default" : "secondary"}>
                                {change >= 0 ? "+" : ""}{change}M
                              </Badge>
                            </td>
                            <td className="text-right py-3 px-3 font-medium text-green-600">{percentChange}%</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </TabsContent>

              {/* Forma */}
              <TabsContent value="form" className="space-y-4">
                <div className="h-80 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={selectedPlayers[0]?.form || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis label={{ value: "Valor (Millones $)", angle: -90, position: "insideLeft" }} />
                      <Tooltip />
                      <Legend />
                      {selectedPlayers.map((player, idx) => (
                        <Line
                          key={player.id}
                          type="monotone"
                          dataKey="value"
                          stroke={["#3b82f6", "#10b981", "#f59e0b"][idx]}
                          name={player.name}
                          connectNulls
                        />
                      ))}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </TabsContent>

              {/* Atributos */}
              <TabsContent value="attributes" className="space-y-4">
                <div className="h-96 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={selectedPlayers[0]?.attributes ? Object.entries(selectedPlayers[0].attributes).map(([key, value]) => ({ name: key.charAt(0).toUpperCase() + key.slice(1), value })) : []}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="name" />
                      <PolarRadiusAxis angle={90} domain={[0, 100]} />
                      <Radar name={selectedPlayers[0]?.name} dataKey="value" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                      {selectedPlayers.length > 1 && (
                        <Radar name={selectedPlayers[1]?.name} dataKey="value" stroke="#10b981" fill="#10b981" fillOpacity={0.3} />
                      )}
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
                        <CardTitle className="text-lg">{player.name}</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="grid grid-cols-2 gap-3">
                          <div className="bg-blue-50 p-3 rounded">
                            <p className="text-xs text-muted-foreground">Goles</p>
                            <p className="text-2xl font-bold text-blue-600">{player.stats.goals}</p>
                          </div>
                          <div className="bg-green-50 p-3 rounded">
                            <p className="text-xs text-muted-foreground">Asistencias</p>
                            <p className="text-2xl font-bold text-green-600">{player.stats.assists}</p>
                          </div>
                          <div className="bg-yellow-50 p-3 rounded">
                            <p className="text-xs text-muted-foreground">Partidos</p>
                            <p className="text-2xl font-bold text-yellow-600">{player.stats.matches}</p>
                          </div>
                          <div className="bg-purple-50 p-3 rounded">
                            <p className="text-xs text-muted-foreground">Rating</p>
                            <p className="text-2xl font-bold text-purple-600">{player.stats.rating}</p>
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
