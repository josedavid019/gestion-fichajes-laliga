import { Send, Clock, BookOpen, FileText } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const mockHistory = [
  "¿Cuál es el límite salarial según el FFP?",
  "¿Qué dice el artículo 72 sobre traspasos?",
  "Requisitos de homologación de clubes",
];

const mockResponse = {
  answer: "Según el Reglamento de Fair Play Financiero de la UEFA (Artículo 61), los clubes participantes no podrán reportar un déficit agregado superior a **€30 millones** durante un período de evaluación de tres años. Este umbral puede elevarse a **€60 millones** si el excedente está cubierto por aportes directos de los propietarios del club.",
  sources: [
    { doc: "UEFA FFP Regulations 2024", section: "Art. 61 - Break-even requirement", page: 34 },
    { doc: "CAS Jurisprudence Digest", section: "Case 2023/A/9876", page: 12 },
  ],
  quotes: [
    '"The acceptable deviation shall not exceed EUR 30 million over a monitoring period..."',
    '"Contributions from equity participants may cover an additional EUR 30 million..."',
  ],
};

export default function AIQuery() {
  const [query, setQuery] = useState("");
  const [hasResult, setHasResult] = useState(false);

  const handleSubmit = () => {
    if (query.trim()) setHasResult(true);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-heading font-bold">Consulta IA / RAG</h1>
        <p className="text-sm text-muted-foreground mt-1">Buscador inteligente sobre reglamentación deportiva</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Search + Result */}
        <div className="lg:col-span-3 space-y-4">
          {/* Search Bar */}
          <div className="glass-card p-4">
            <div className="flex gap-2">
              <Input
                placeholder="Escribe tu pregunta sobre el reglamento..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
                className="bg-muted/50 border-border/50"
              />
              <Button onClick={handleSubmit} className="gap-2 shrink-0">
                <Send className="w-4 h-4" /> Consultar
              </Button>
            </div>
          </div>

          {/* Response */}
          {hasResult && (
            <div className="glass-card p-6 animate-slide-up">
              <div className="flex items-center gap-2 mb-4">
                <BookOpen className="w-4 h-4 text-primary" />
                <h3 className="font-heading font-semibold text-sm">Respuesta Generada</h3>
              </div>
              <div className="prose prose-sm prose-invert max-w-none mb-6">
                <p className="text-sm text-foreground/90 leading-relaxed">{mockResponse.answer}</p>
              </div>

              {/* Sources */}
              <div className="mb-4">
                <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Fuentes Documentales</h4>
                <div className="space-y-2">
                  {mockResponse.sources.map((s, i) => (
                    <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-muted/30 border border-border/30">
                      <FileText className="w-4 h-4 text-accent mt-0.5 shrink-0" />
                      <div>
                        <p className="text-xs font-medium text-foreground">{s.doc}</p>
                        <p className="text-[10px] text-muted-foreground">{s.section} · Pág. {s.page}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Quotes */}
              <div>
                <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Citas Relevantes</h4>
                <div className="space-y-2">
                  {mockResponse.quotes.map((q, i) => (
                    <blockquote key={i} className="border-l-2 border-primary/50 pl-4 py-1">
                      <p className="text-xs text-foreground/80 italic">{q}</p>
                    </blockquote>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* History */}
        <div className="glass-card p-5 h-fit">
          <div className="flex items-center gap-2 mb-4">
            <Clock className="w-4 h-4 text-muted-foreground" />
            <h3 className="font-heading font-semibold text-sm">Historial</h3>
          </div>
          <div className="space-y-2">
            {mockHistory.map((q, i) => (
              <button
                key={i}
                className="w-full text-left p-3 rounded-lg bg-muted/30 hover:bg-muted/60 transition-colors"
                onClick={() => { setQuery(q); setHasResult(true); }}
              >
                <p className="text-[11px] text-foreground/80 line-clamp-2">{q}</p>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
