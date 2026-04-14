import {
  AlertCircle,
  CheckCircle2,
  ImageIcon,
  Loader2,
  ScanSearch,
  Upload,
  X,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type DetectionResponse = {
  meta: {
    request_id: string;
    processed_at: string;
    pipeline: string[];
    enrichment_errors?: string[];
  };
  player_profile: {
    identified_name: string;
    first_name: string | null;
    last_name: string | null;
    age: number | null;
    nationality: string | null;
    birth_date: string | null;
    height: string | null;
    height_cm: number | null;
    weight: string | null;
    weight_kg: number | null;
    position: string | null;
    status: string | null;
    jersey_number: string | null;
    current_club: string | null;
    photo_url: string | null;
  };
  statistics: {
    appearances: number | null;
    goals: number | null;
    assists: number | null;
    rating: string | null;
  };
  vision_analysis: {
    yolo: {
      player_detected: boolean;
      confidence: number | null;
      bounding_box: [number, number, number, number] | null;
      total_persons_detected: number;
      error: string | null;
    };
    ocr: {
      jersey_number: string | null;
      player_name_raw: string | null;
      team_name_raw: string | null;
      extra_tokens: string[];
      raw_text_preview: string | null;
    };
  };
};

export default function Detection() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<DetectionResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [imageSize, setImageSize] = useState({ width: 1, height: 1 });

  useEffect(() => {
    if (!selectedFile) {
      setPreviewUrl(null);
      return;
    }

    const objectUrl = URL.createObjectURL(selectedFile);
    setPreviewUrl(objectUrl);
    return () => URL.revokeObjectURL(objectUrl);
  }, [selectedFile]);

  const bboxStyle = useMemo(() => {
    const bbox = result?.vision_analysis.yolo.bounding_box;
    if (!bbox) {
      return null;
    }

    const [x1, y1, x2, y2] = bbox;
    return {
      left: `${(x1 / imageSize.width) * 100}%`,
      top: `${(y1 / imageSize.height) * 100}%`,
      width: `${((x2 - x1) / imageSize.width) * 100}%`,
      height: `${((y2 - y1) / imageSize.height) * 100}%`,
    };
  }, [
    imageSize.height,
    imageSize.width,
    result?.vision_analysis.yolo.bounding_box,
  ]);

  const handleFileChange = (file: File | null) => {
    setSelectedFile(file);
    setResult(null);
    setError(null);
    setImageSize({ width: 1, height: 1 });
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError("Selecciona una imagen antes de analizar.");
      return;
    }

    const formData = new FormData();
    formData.append("image", selectedFile);

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch("/api/vision/analyze-player/", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "No se pudo analizar la imagen.");
      }

      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Error inesperado analizando la imagen.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setResult(null);
    setError(null);
    setImageSize({ width: 1, height: 1 });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-heading font-bold">Detección YOLO</h1>
      </div>

      <div className="glass-card p-8">
        {!selectedFile ? (
          <div className="border-2 border-dashed border-border/60 rounded-xl p-12 text-center hover:border-primary/40 transition-colors">
            <Upload className="w-10 h-10 text-muted-foreground mx-auto mb-4" />
            <p className="text-sm font-medium text-foreground mb-2">
              Selecciona una imagen del jugador
            </p>
            <p className="text-xs text-muted-foreground mb-6">
              JPG o PNG. Cuanto más limpia y frontal sea la imagen, mejor
              responderán YOLO y OCR.
            </p>
            <div className="mx-auto max-w-sm">
              <Input
                type="file"
                accept="image/png,image/jpeg,image/jpg"
                onChange={(event) =>
                  handleFileChange(event.target.files?.[0] || null)
                }
                className="cursor-pointer"
              />
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-heading font-semibold text-sm">
                  Resultado de Detección
                </h3>
                <p className="text-xs text-muted-foreground mt-1">
                  {selectedFile.name}
                </p>
              </div>
              <Button variant="ghost" size="sm" onClick={handleReset}>
                <X className="w-4 h-4 mr-1" /> Reiniciar
              </Button>
            </div>

            <div className="flex flex-wrap gap-3">
              <Button
                onClick={handleAnalyze}
                disabled={isLoading}
                className="gap-2"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <ScanSearch className="w-4 h-4" />
                )}
                Analizar Imagen
              </Button>
              <Button variant="outline" className="gap-2" asChild>
                <label>
                  <ImageIcon className="w-4 h-4" />
                  Cambiar Imagen
                  <input
                    type="file"
                    accept="image/png,image/jpeg,image/jpg"
                    className="hidden"
                    onChange={(event) =>
                      handleFileChange(event.target.files?.[0] || null)
                    }
                  />
                </label>
              </Button>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1.1fr)_minmax(320px,0.9fr)] gap-6">
              <div className="rounded-xl bg-muted/20 border border-border/50 overflow-hidden">
                {previewUrl && (
                  <div className="relative">
                    <img
                      src={previewUrl}
                      alt="Vista previa"
                      className="w-full max-h-[560px] object-contain bg-black/30"
                      onLoad={(event) => {
                        setImageSize({
                          width: event.currentTarget.naturalWidth,
                          height: event.currentTarget.naturalHeight,
                        });
                      }}
                    />
                    {bboxStyle &&
                      result?.vision_analysis.yolo.player_detected && (
                        <div
                          className="absolute border-2 border-primary shadow-[0_0_0_1px_rgba(0,0,0,0.35)]"
                          style={bboxStyle}
                        >
                          <span className="absolute -top-7 left-0 rounded-sm bg-primary px-2 py-1 text-[10px] font-semibold text-primary-foreground">
                            Jugador{" "}
                            {result.vision_analysis.yolo.confidence
                              ? `${(
                                  result.vision_analysis.yolo.confidence * 100
                                ).toFixed(1)}%`
                              : ""}
                          </span>
                        </div>
                      )}
                  </div>
                )}
              </div>

              <div className="space-y-4">
                {error && (
                  <div className="rounded-xl border border-destructive/40 bg-destructive/10 p-4 text-sm text-destructive">
                    <div className="flex items-start gap-2">
                      <AlertCircle className="mt-0.5 h-4 w-4" />
                      <span>{error}</span>
                    </div>
                  </div>
                )}

                {result && (
                  <div className="space-y-4">
                    <div className="stat-card">
                      <div className="mb-3 flex items-center gap-2">
                        {result.vision_analysis.yolo.player_detected ? (
                          <CheckCircle2 className="h-4 w-4 text-primary" />
                        ) : (
                          <AlertCircle className="h-4 w-4 text-warning" />
                        )}
                        <p className="text-sm font-semibold">
                          Resumen del análisis
                        </p>
                      </div>
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div>
                          <p className="text-muted-foreground">Nombre</p>
                          <p className="font-medium">
                            {result.player_profile.identified_name ||
                              "Desconocido"}
                          </p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Dorsal</p>
                          <p className="font-medium">
                            {result.player_profile.jersey_number ||
                              "No detectado"}
                          </p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Posición</p>
                          <p className="font-medium">
                            {result.player_profile.position || "No detectado"}
                          </p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Club</p>
                          <p className="font-medium">
                            {result.player_profile.current_club ||
                              "No detectado"}
                          </p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Nacionalidad</p>
                          <p className="font-medium">
                            {result.player_profile.nationality ||
                              "No disponible"}
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="stat-card">
                      <p className="mb-3 text-sm font-semibold">Visión</p>
                      <div className="space-y-2 text-sm">
                        <p>
                          <span className="text-muted-foreground">
                            Jugador detectado:
                          </span>{" "}
                          {result.vision_analysis.yolo.player_detected
                            ? "Sí"
                            : "No"}
                        </p>
                        <p>
                          <span className="text-muted-foreground">
                            Confianza YOLO:
                          </span>{" "}
                          {result.vision_analysis.yolo.confidence
                            ? `${(
                                result.vision_analysis.yolo.confidence * 100
                              ).toFixed(2)}%`
                            : "N/A"}
                        </p>
                        <p>
                          <span className="text-muted-foreground">
                            Personas detectadas:
                          </span>{" "}
                          {result.vision_analysis.yolo.total_persons_detected}
                        </p>
                      </div>
                    </div>

                    {!!result.meta.enrichment_errors?.length && (
                      <div className="rounded-xl border border-warning/40 bg-warning/10 p-4 text-sm text-foreground">
                        <p className="mb-2 font-semibold text-warning">
                          Avisos del backend
                        </p>
                        <div className="space-y-1 text-xs">
                          {result.meta.enrichment_errors.map((message) => (
                            <p key={message}>{message}</p>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
