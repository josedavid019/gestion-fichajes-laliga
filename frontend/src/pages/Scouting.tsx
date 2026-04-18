import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PlayerComparator } from "@/components/PlayerComparator";
import { ContractAlerts } from "@/components/ContractAlerts";
import { ScoutingReportExport } from "@/components/ScoutingReportExport";
import { Users, Clock, FileText } from "lucide-react";

const Scouting = () => {
  const [activeTab, setActiveTab] = useState("comparator");

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold">Gestión de Jugadores</h1>
        <p className="text-muted-foreground">
          Herramientas avanzadas para análisis, comparación y seguimiento de jugadores
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="comparator" className="flex items-center gap-2">
            <Users className="w-4 h-4" />
            <span>Comparador</span>
          </TabsTrigger>
          <TabsTrigger value="alerts" className="flex items-center gap-2">
            <Clock className="w-4 h-4" />
            <span>Alertas</span>
          </TabsTrigger>
          <TabsTrigger value="reports" className="flex items-center gap-2">
            <FileText className="w-4 h-4" />
            <span>Reportes</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="comparator" className="space-y-4">
          <PlayerComparator />
        </TabsContent>

        <TabsContent value="alerts" className="space-y-4">
          <ContractAlerts />
        </TabsContent>

        <TabsContent value="reports" className="space-y-4">
          <ScoutingReportExport />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Scouting;
