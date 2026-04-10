import { Upload, Camera, Video, ImageIcon, X } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";

const mockResults = [
  { name: "Lamine Yamal", confidence: 96.8, position: "Extremo Derecho", age: 17, attributes: ["Velocidad: 92", "Regate: 89", "Pase: 78"] },
  { name: "Gavi", confidence: 91.2, position: "Centrocampista", age: 20, attributes: ["Pase: 86", "Visión: 88", "Resistencia: 84"] },
];

export default function Detection() {
  const [uploaded, setUploaded] = useState(false);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-heading font-bold">Detección YOLO</h1>
        <p className="text-sm text-muted-foreground mt-1">Carga imágenes o video para detectar jugadores</p>
      </div>

      {/* Upload Zone */}
      <div className="glass-card p-8">
        {!uploaded ? (
          <div
            className="border-2 border-dashed border-border/60 rounded-xl p-12 text-center cursor-pointer hover:border-primary/40 transition-colors"
            onClick={() => setUploaded(true)}
          >
            <Upload className="w-10 h-10 text-muted-foreground mx-auto mb-4" />
            <p className="text-sm font-medium text-foreground mb-2">Arrastra tu archivo aquí o haz clic</p>
            <p className="text-xs text-muted-foreground mb-6">Soporta imágenes (JPG, PNG) y video (MP4, AVI)</p>
            <div className="flex justify-center gap-3">
              <Button variant="outline" size="sm" className="gap-2">
                <ImageIcon className="w-3.5 h-3.5" /> Imagen
              </Button>
              <Button variant="outline" size="sm" className="gap-2">
                <Video className="w-3.5 h-3.5" /> Video
              </Button>
              <Button variant="outline" size="sm" className="gap-2">
                <Camera className="w-3.5 h-3.5" /> Cámara
              </Button>
            </div>
          </div>
        ) : (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-heading font-semibold text-sm">Resultado de Detección</h3>
              <Button variant="ghost" size="sm" onClick={() => setUploaded(false)}>
                <X className="w-4 h-4 mr-1" /> Reiniciar
              </Button>
            </div>
            {/* Mock detection preview */}
            <div className="rounded-xl bg-muted/30 h-64 flex items-center justify-center mb-6 relative overflow-hidden border border-border/50">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent/5" />
              <div className="text-center relative z-10">
                <Camera className="w-12 h-12 text-primary/40 mx-auto mb-2" />
                <p className="text-xs text-muted-foreground">Vista previa con bounding boxes</p>
                <p className="text-[10px] text-primary mt-1">2 jugadores detectados</p>
              </div>
              {/* Mock bounding boxes */}
              <div className="absolute top-8 left-16 w-24 h-40 border-2 border-primary rounded-md">
                <span className="absolute -top-5 left-0 text-[9px] bg-primary text-primary-foreground px-1.5 py-0.5 rounded-sm font-medium">
                  Yamal 96.8%
                </span>
              </div>
              <div className="absolute top-12 right-20 w-20 h-36 border-2 border-accent rounded-md">
                <span className="absolute -top-5 left-0 text-[9px] bg-accent text-accent-foreground px-1.5 py-0.5 rounded-sm font-medium">
                  Gavi 91.2%
                </span>
              </div>
            </div>

            {/* Results */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {mockResults.map((r) => (
                <div key={r.name} className="stat-card">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-full bg-primary/15 flex items-center justify-center font-heading font-bold text-sm text-primary">
                      {r.name.split(" ")[1]?.[0] || r.name[0]}
                    </div>
                    <div>
                      <p className="font-semibold text-sm">{r.name}</p>
                      <p className="text-[10px] text-muted-foreground">{r.position} · {r.age} años</p>
                    </div>
                    <span className="ml-auto text-xs font-bold text-primary">{r.confidence}%</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {r.attributes.map((attr) => (
                      <span key={attr} className="text-[10px] bg-muted px-2 py-1 rounded-md text-muted-foreground">
                        {attr}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
