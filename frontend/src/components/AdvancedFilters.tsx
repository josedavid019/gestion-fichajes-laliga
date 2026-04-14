import { Filter } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface AdvancedFiltersProps {
  clubs: string[];
  selectedClub: string;
  setSelectedClub: (club: string) => void;
  selectedAgeRange: string;
  setSelectedAgeRange: (range: string) => void;
  selectedStatus: string;
  setSelectedStatus: (status: string) => void;
  onReset: () => void;
}

const ageRanges = [
  { value: "", label: "Todas las edades" },
  { value: "16-18", label: "16-18 años" },
  { value: "19-22", label: "19-22 años" },
  { value: "23-27", label: "23-27 años" },
  { value: "28-32", label: "28-32 años" },
  { value: "33-40", label: "33+ años" },
];

const statusOptions = [
  { value: "", label: "Todos los estados" },
  { value: "active", label: "Activo" },
  { value: "injured", label: "Lesionado" },
  { value: "suspended", label: "Sancionado" },
  { value: "retired", label: "Retirado" },
  { value: "free_agent", label: "Libre" },
];

export default function AdvancedFilters({
  clubs,
  selectedClub,
  setSelectedClub,
  selectedAgeRange,
  setSelectedAgeRange,
  selectedStatus,
  setSelectedStatus,
  onReset,
}: AdvancedFiltersProps) {
  return (
    <div className="glass-card p-4 space-y-4">
      <div className="flex items-center gap-2 mb-3">
        <Filter className="w-4 h-4 text-primary" />
        <h3 className="font-semibold text-sm">Filtros Avanzados</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {/* Club Filter */}
        <div>
          <label className="text-xs font-semibold text-muted-foreground mb-2 block">
            Club
          </label>
          <Select value={selectedClub} onValueChange={setSelectedClub}>
            <SelectTrigger className="bg-muted/30 border-border/50 h-9">
              <SelectValue placeholder="Todos los clubs" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">Todos los clubs</SelectItem>
              {clubs.map((club) => (
                <SelectItem key={club} value={club}>
                  {club}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Age Range Filter */}
        <div>
          <label className="text-xs font-semibold text-muted-foreground mb-2 block">
            Edad
          </label>
          <Select value={selectedAgeRange} onValueChange={setSelectedAgeRange}>
            <SelectTrigger className="bg-muted/30 border-border/50 h-9">
              <SelectValue placeholder="Todas las edades" />
            </SelectTrigger>
            <SelectContent>
              {ageRanges.map((range) => (
                <SelectItem key={range.value} value={range.value}>
                  {range.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Status Filter */}
        <div>
          <label className="text-xs font-semibold text-muted-foreground mb-2 block">
            Estado
          </label>
          <Select value={selectedStatus} onValueChange={setSelectedStatus}>
            <SelectTrigger className="bg-muted/30 border-border/50 h-9">
              <SelectValue placeholder="Todos los estados" />
            </SelectTrigger>
            <SelectContent>
              {statusOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <Button
        variant="outline"
        size="sm"
        onClick={onReset}
        className="w-full text-xs"
      >
        Limpiar Filtros
      </Button>
    </div>
  );
}
