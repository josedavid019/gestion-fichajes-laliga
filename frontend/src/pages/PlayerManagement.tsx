import React, { useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import PlayerFormDialog, {
  PlayerFormData,
  defaultFormData,
} from "@/components/PlayerFormDialog";
import PlayerFilters from "@/components/PlayerFilters";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { toast } from "sonner";
import { Plus, Edit2, Trash2 } from "lucide-react";
import { fetchWithAuth } from "@/lib/fetchWithAuth";

const fetchPlayers = async ({
  page,
  search,
  status,
  club,
  position,
}: {
  page: number;
  search: string;
  status: string;
  club: string;
  position: string;
}) => {
  const params = new URLSearchParams();
  params.set("limit", "50");
  params.set("offset", String(page * 50));
  if (search.trim()) params.set("search", search.trim());
  if (status) params.set("status", status);
  if (club) params.set("current_club", club);
  if (position) params.set("positions__position", position);

  const response = await fetchWithAuth(`/api/players/?${params.toString()}`);
  if (!response.ok) {
    throw new Error("No se pudo cargar la lista de jugadores.");
  }
  const data = await response.json();
  return {
    results: data.results ?? data,
    count:
      data.count ??
      (Array.isArray(data.results)
        ? data.results.length
        : Array.isArray(data)
          ? data.length
          : 0),
  };
};

const fetchClubs = async () => {
  const response = await fetchWithAuth("/api/clubs/?limit=200");
  if (!response.ok) {
    throw new Error("No se pudo cargar la lista de clubes.");
  }
  const data = await response.json();
  return data.results ?? data;
};

const PlayerManagement: React.FC = () => {
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [clubFilter, setClubFilter] = useState("");
  const [positionFilter, setPositionFilter] = useState("");
  const [currentPage, setCurrentPage] = useState(0);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingPlayerId, setEditingPlayerId] = useState<number | null>(null);
  const [formData, setFormData] = useState<PlayerFormData>(defaultFormData);

  const { data: playersData, isLoading: loadingPlayers } = useQuery<
    { results: any[]; count: number },
    Error
  >({
    queryKey: [
      "players",
      currentPage,
      searchTerm,
      statusFilter,
      clubFilter,
      positionFilter,
    ],
    queryFn: () =>
      fetchPlayers({
        page: currentPage,
        search: searchTerm,
        status: statusFilter,
        club: clubFilter,
        position: positionFilter,
      }),
    staleTime: 1000 * 60,
  });
  const players = (playersData?.results ?? []) as any[];
  const totalPlayers = playersData?.count ?? 0;

  const { data: clubs = [], isLoading: loadingClubs } = useQuery({
    queryKey: ["clubs"],
    queryFn: fetchClubs,
    staleTime: 1000 * 60 * 5,
  });

  const createPlayer = useMutation({
    mutationFn: async (payload: any) => {
      const response = await fetchWithAuth("/api/players/", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(JSON.stringify(errorBody));
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["players"] });
      toast.success("Jugador creado correctamente.");
      setIsDialogOpen(false);
      setFormData(defaultFormData);
    },
    onError: (error: any) => {
      toast.error("No se pudo crear el jugador.");
      console.error(error);
    },
  });

  const updatePlayer = useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: any }) => {
      const response = await fetchWithAuth(`/api/players/${id}/`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(JSON.stringify(errorBody));
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["players"] });
      toast.success("Jugador actualizado correctamente.");
      setIsDialogOpen(false);
      setEditingPlayerId(null);
      setFormData(defaultFormData);
    },
    onError: (error: any) => {
      toast.error("No se pudo actualizar el jugador.");
      console.error(error);
    },
  });

  const deletePlayer = useMutation({
    mutationFn: async (id: number) => {
      const response = await fetchWithAuth(`/api/players/${id}/`, {
        method: "DELETE",
      });
      if (!response.ok) {
        throw new Error("No se pudo eliminar el jugador.");
      }
      return id;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["players"] });
      toast.success("Jugador eliminado correctamente.");
    },
    onError: (error: any) => {
      toast.error("No se pudo eliminar el jugador.");
      console.error(error);
    },
  });

  const selectedPlayer = useMemo(
    () =>
      (players as any[]).find((player: any) => player.id === editingPlayerId) ??
      null,
    [editingPlayerId, players],
  );

  const positionOptions = useMemo(() => {
    const uniquePositions = new Set<string>();
    players.forEach((player: any) => {
      if (player.position) uniquePositions.add(player.position);
      if (Array.isArray(player.positions)) {
        player.positions.forEach((position: any) => {
          if (position?.position) uniquePositions.add(position.position);
        });
      }
    });
    return Array.from(uniquePositions).sort();
  }, [players]);

  const totalPages = Math.max(1, Math.ceil(totalPlayers / 50));
  const canPrevious = currentPage > 0;
  const canNext = currentPage < totalPages - 1;

  const openNewDialog = () => {
    setEditingPlayerId(null);
    setFormData(defaultFormData);
    setIsDialogOpen(true);
  };

  const openEditDialog = (player: any) => {
    setEditingPlayerId(player.id);
    setFormData({
      first_name: player.first_name || "",
      last_name: player.last_name || "",
      alias: player.alias || "",
      full_name: player.full_name || "",
      date_of_birth: player.date_of_birth || "",
      current_club: player.current_club?.id
        ? String(player.current_club.id)
        : "",
      shirt_number: player.shirt_number ? String(player.shirt_number) : "",
      height_cm: player.height_cm ? String(player.height_cm) : "",
      weight_kg: player.weight_kg ? String(player.weight_kg) : "",
      preferred_foot: player.preferred_foot || "",
      status: player.status || "active",
      market_value_eur: player.market_value_eur
        ? String(player.market_value_eur)
        : "",
      photo_url: player.photo_url || "",
      external_id: player.external_id ? String(player.external_id) : "",
      position: player.position || player.positions?.[0]?.position || "",
    });
    setIsDialogOpen(true);
  };

  const handleDialogClose = () => {
    setIsDialogOpen(false);
    setEditingPlayerId(null);
    setFormData(defaultFormData);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const payload = {
      first_name: formData.first_name.trim(),
      last_name: formData.last_name.trim(),
      alias: formData.alias.trim(),
      full_name: formData.full_name.trim(),
      date_of_birth: formData.date_of_birth || null,
      current_club_id: formData.current_club
        ? Number(formData.current_club)
        : null,
      shirt_number: formData.shirt_number
        ? Number(formData.shirt_number)
        : null,
      height_cm: formData.height_cm ? Number(formData.height_cm) : null,
      weight_kg: formData.weight_kg ? Number(formData.weight_kg) : null,
      preferred_foot: formData.preferred_foot.trim(),
      status: formData.status,
      market_value_eur: formData.market_value_eur
        ? Number(formData.market_value_eur)
        : null,
      photo_url: formData.photo_url.trim(),
      external_id: formData.external_id ? Number(formData.external_id) : null,
      position_name: formData.position.trim() || undefined,
    };

    if (!payload.first_name || !payload.last_name) {
      toast.error("Nombre y apellido son obligatorios.");
      return;
    }

    if (editingPlayerId) {
      updatePlayer.mutate({ id: editingPlayerId, payload });
    } else {
      createPlayer.mutate(payload);
    }
  };

  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold">Gestión de Jugadores</h1>
          <p className="text-muted-foreground mt-1">
            Crea, edita y elimina jugadores desde el panel administrativo.
          </p>
        </div>
        <Button
          onClick={openNewDialog}
          className="bg-primary text-primary-foreground hover:bg-primary/90"
        >
          <Plus className="w-4 h-4" /> Nuevo jugador
        </Button>
      </div>

      <PlayerFilters
        searchTerm={searchTerm}
        statusFilter={statusFilter}
        clubFilter={clubFilter}
        positionFilter={positionFilter}
        clubs={clubs as any[]}
        positionOptions={positionOptions}
        onSearchTermChange={(value) => {
          setSearchTerm(value);
          setCurrentPage(0);
        }}
        onStatusFilterChange={(value) => {
          setStatusFilter(value);
          setCurrentPage(0);
        }}
        onClubFilterChange={(value) => {
          setClubFilter(value);
          setCurrentPage(0);
        }}
        onPositionFilterChange={(value) => {
          setPositionFilter(value);
          setCurrentPage(0);
        }}
      />

      <div className="overflow-hidden rounded-3xl border border-border bg-card shadow-sm">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Jugador</TableHead>
              <TableHead>Club</TableHead>
              <TableHead>Posición</TableHead>
              <TableHead>Estado</TableHead>
              <TableHead>Valor</TableHead>
              <TableHead>Acciones</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {(players as any[]).map((player: any) => (
              <TableRow key={player.id}>
                <TableCell>
                  <div className="font-semibold">
                    {player.alias || `${player.first_name} ${player.last_name}`}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {player.full_name}
                  </div>
                </TableCell>
                <TableCell>{player.current_club?.name || "Sin club"}</TableCell>
                <TableCell>
                  {player.position || player.positions?.[0]?.position || "—"}
                </TableCell>
                <TableCell>{player.status || "—"}</TableCell>
                <TableCell>
                  {player.market_value_eur
                    ? `€${Number(player.market_value_eur).toLocaleString()}`
                    : "—"}
                </TableCell>
                <TableCell className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => openEditDialog(player)}
                  >
                    <Edit2 className="w-4 h-4" /> Editar
                  </Button>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => {
                      if (window.confirm("¿Eliminar este jugador?")) {
                        deletePlayer.mutate(player.id);
                      }
                    }}
                  >
                    <Trash2 className="w-4 h-4" /> Eliminar
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <div className="flex flex-col gap-2 rounded-3xl border border-border bg-card px-4 py-4 shadow-sm md:flex-row md:items-center md:justify-between">
        <div className="text-sm text-muted-foreground">
          Mostrando página {currentPage + 1} de {totalPages} • {totalPlayers}{" "}
          jugadores
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={!canPrevious}
            onClick={() => setCurrentPage((page) => Math.max(0, page - 1))}
          >
            Anterior
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={!canNext}
            onClick={() =>
              setCurrentPage((page) => Math.min(totalPages - 1, page + 1))
            }
          >
            Siguiente
          </Button>
        </div>
      </div>

      <PlayerFormDialog
        open={isDialogOpen}
        formData={formData}
        clubs={clubs as any[]}
        editingPlayerId={editingPlayerId}
        isSubmitting={createPlayer.isPending || updatePlayer.isPending}
        loadingClubs={loadingClubs}
        onFormChange={setFormData}
        onSubmit={handleSubmit}
        onClose={handleDialogClose}
      />
    </div>
  );
};

export default PlayerManagement;
