import React from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface PlayerFiltersProps {
  searchTerm: string;
  statusFilter: string;
  clubFilter: string;
  positionFilter: string;
  clubs: any[];
  positionOptions: string[];
  onSearchTermChange: (value: string) => void;
  onStatusFilterChange: (value: string) => void;
  onClubFilterChange: (value: string) => void;
  onPositionFilterChange: (value: string) => void;
}

const PlayerFilters: React.FC<PlayerFiltersProps> = ({
  searchTerm,
  statusFilter,
  clubFilter,
  positionFilter,
  clubs,
  positionOptions,
  onSearchTermChange,
  onStatusFilterChange,
  onClubFilterChange,
  onPositionFilterChange,
}) => {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-[1fr_200px_200px_200px] items-end">
      <div>
        <Label htmlFor="player-search">Buscar jugadores</Label>
        <Input
          id="player-search"
          placeholder="Nombre, club o estado..."
          value={searchTerm}
          onChange={(event) => onSearchTermChange(event.target.value)}
        />
      </div>

      <div>
        <Label htmlFor="status-filter">Estado</Label>
        <Select
          value={statusFilter}
          onValueChange={(value) =>
            onStatusFilterChange(value === "none" ? "" : value)
          }
        >
          <SelectTrigger id="status-filter">
            <SelectValue placeholder="Todos" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">Todos</SelectItem>
            <SelectItem value="active">Activo</SelectItem>
            <SelectItem value="inactive">Inactivo</SelectItem>
            <SelectItem value="injured">Lesionado</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div>
        <Label htmlFor="club-filter">Club</Label>
        <Select
          value={clubFilter}
          onValueChange={(value) =>
            onClubFilterChange(value === "none" ? "" : value)
          }
        >
          <SelectTrigger id="club-filter">
            <SelectValue placeholder="Todos" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">Todos</SelectItem>
            {clubs.map((club: any) => (
              <SelectItem key={club.id} value={String(club.id)}>
                {club.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div>
        <Label htmlFor="position-filter">Posición</Label>
        <Select
          value={positionFilter}
          onValueChange={(value) =>
            onPositionFilterChange(value === "none" ? "" : value)
          }
        >
          <SelectTrigger id="position-filter">
            <SelectValue placeholder="Todos" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">Todos</SelectItem>
            {positionOptions.map((position) => (
              <SelectItem key={position} value={position}>
                {position}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
};

export default PlayerFilters;
