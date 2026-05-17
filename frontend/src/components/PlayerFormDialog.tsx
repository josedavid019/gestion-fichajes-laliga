import React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export interface PlayerFormData {
  first_name: string;
  last_name: string;
  alias: string;
  full_name: string;
  date_of_birth: string;
  current_club: string;
  shirt_number: string;
  height_cm: string;
  weight_kg: string;
  preferred_foot: string;
  status: string;
  market_value_eur: string;
  photo_url: string;
  external_id: string;
  position: string;
}

export const defaultFormData: PlayerFormData = {
  first_name: "",
  last_name: "",
  alias: "",
  full_name: "",
  date_of_birth: "",
  current_club: "",
  shirt_number: "",
  height_cm: "",
  weight_kg: "",
  preferred_foot: "",
  status: "active",
  market_value_eur: "",
  photo_url: "",
  external_id: "",
  position: "",
};

interface PlayerFormDialogProps {
  open: boolean;
  formData: PlayerFormData;
  clubs: any[];
  editingPlayerId: number | null;
  isSubmitting: boolean;
  loadingClubs: boolean;
  onFormChange: (data: PlayerFormData) => void;
  onSubmit: (event: React.FormEvent<HTMLFormElement>) => void;
  onClose: () => void;
}

const PlayerFormDialog: React.FC<PlayerFormDialogProps> = ({
  open,
  formData,
  clubs,
  editingPlayerId,
  isSubmitting,
  loadingClubs,
  onFormChange,
  onSubmit,
  onClose,
}) => {
  const handleChange = (field: keyof PlayerFormData, value: string) => {
    onFormChange({ ...formData, [field]: value });
  };

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>
            {editingPlayerId ? "Editar jugador" : "Nuevo jugador"}
          </DialogTitle>
          <DialogDescription>
            {editingPlayerId
              ? "Actualiza la información del jugador"
              : "Crea un nuevo jugador en la base de datos"}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={onSubmit} className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label htmlFor="first-name">Nombre</Label>
              <Input
                id="first-name"
                value={formData.first_name}
                onChange={(event) =>
                  handleChange("first_name", event.target.value)
                }
              />
            </div>
            <div>
              <Label htmlFor="last-name">Apellido</Label>
              <Input
                id="last-name"
                value={formData.last_name}
                onChange={(event) =>
                  handleChange("last_name", event.target.value)
                }
              />
            </div>
            <div>
              <Label htmlFor="alias">Alias</Label>
              <Input
                id="alias"
                value={formData.alias}
                onChange={(event) => handleChange("alias", event.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="external-id">ID externo</Label>
              <Input
                id="external-id"
                type="number"
                min="0"
                value={formData.external_id}
                onChange={(event) =>
                  handleChange("external_id", event.target.value)
                }
              />
            </div>
            <div>
              <Label htmlFor="full-name">Nombre completo</Label>
              <Input
                id="full-name"
                value={formData.full_name}
                onChange={(event) =>
                  handleChange("full_name", event.target.value)
                }
              />
            </div>
            <div>
              <Label htmlFor="position">Posición</Label>
              <Input
                id="position"
                value={formData.position}
                onChange={(event) =>
                  handleChange("position", event.target.value)
                }
              />
            </div>
            <div>
              <Label htmlFor="date-of-birth">Fecha de nacimiento</Label>
              <Input
                id="date-of-birth"
                type="date"
                value={formData.date_of_birth}
                onChange={(event) =>
                  handleChange("date_of_birth", event.target.value)
                }
              />
            </div>
            <div>
              <Label htmlFor="status">Estado</Label>
              <Select
                value={formData.status}
                onValueChange={(value) => handleChange("status", value)}
              >
                <SelectTrigger id="status">
                  <SelectValue placeholder="Selecciona estado" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="active">Activo</SelectItem>
                  <SelectItem value="injured">Lesionado</SelectItem>
                  <SelectItem value="suspended">Suspendido</SelectItem>
                  <SelectItem value="inactive">Inactivo</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="club">Club actual</Label>
              <Select
                value={formData.current_club}
                onValueChange={(value) =>
                  handleChange("current_club", value === "none" ? "" : value)
                }
              >
                <SelectTrigger id="club">
                  <SelectValue placeholder="Selecciona club" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Sin club</SelectItem>
                  {clubs.map((club: any) => (
                    <SelectItem key={club.id} value={String(club.id)}>
                      {club.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="shirt-number">Dorsal</Label>
              <Input
                id="shirt-number"
                type="number"
                min="1"
                value={formData.shirt_number}
                onChange={(event) =>
                  handleChange("shirt_number", event.target.value)
                }
              />
            </div>
            <div>
              <Label htmlFor="height-cm">Altura (cm)</Label>
              <Input
                id="height-cm"
                type="number"
                min="0"
                value={formData.height_cm}
                onChange={(event) =>
                  handleChange("height_cm", event.target.value)
                }
              />
            </div>
            <div>
              <Label htmlFor="weight-kg">Peso (kg)</Label>
              <Input
                id="weight-kg"
                type="number"
                min="0"
                value={formData.weight_kg}
                onChange={(event) =>
                  handleChange("weight_kg", event.target.value)
                }
              />
            </div>
            <div>
              <Label htmlFor="preferred-foot">Pie preferido</Label>
              <Input
                id="preferred-foot"
                value={formData.preferred_foot}
                onChange={(event) =>
                  handleChange("preferred_foot", event.target.value)
                }
              />
            </div>
            <div>
              <Label htmlFor="market-value">Valor de mercado (€)</Label>
              <Input
                id="market-value"
                type="number"
                min="0"
                step="0.01"
                value={formData.market_value_eur}
                onChange={(event) =>
                  handleChange("market_value_eur", event.target.value)
                }
              />
            </div>
            <div className="md:col-span-2">
              <Label htmlFor="photo-url">URL de imagen</Label>
              <Input
                id="photo-url"
                value={formData.photo_url}
                onChange={(event) =>
                  handleChange("photo_url", event.target.value)
                }
              />
            </div>
          </div>

          <DialogFooter className="flex flex-col gap-2 sm:flex-row sm:justify-end">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancelar
            </Button>
            <Button type="submit" disabled={isSubmitting || loadingClubs}>
              {editingPlayerId ? "Guardar cambios" : "Crear jugador"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default PlayerFormDialog;
