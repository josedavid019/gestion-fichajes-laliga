import {
  Send,
  Clock,
  BookOpen,
  FileText,
  Wifi,
  WifiOff,
  Loader2,
} from "lucide-react";
import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const BASE = import.meta.env.VITE_DJANGO_URL ?? "http://localhost:8000";
const RAG = `${BASE}/api/rag`;

const QUICK_CHIPS = [
  "¿Cuál es el límite salarial según el control económico de LaLiga?",
  "¿Qué dice el reglamento sobre traspasos internacionales?",
  "Requisitos de inscripción de jugadores sub-23",
  "Duración máxima de un contrato profesional",
  "Sanciones por incumplir el fair play financiero",
];

export default function AIQuery() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null); // { answer, chunks }
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const [serverOk, setServerOk] = useState(null); // null | true | false

  // ── health check ────────────────────────────────────────────────
  useEffect(() => {
    fetch(`${RAG}/health/`, { credentials: "include" })
      .then((r) => setServerOk(r.ok))
      .catch(() => setServerOk(false));
  }, []);

  // ── consulta al RAG ─────────────────────────────────────────────
  const handleSubmit = useCallback(
    async (question = undefined) => {
      const q = (question ?? query).trim();
      if (!q || loading) return;

      setLoading(true);
      setError(null);
      setResult(null);

      try {
        const res = await fetch(`${RAG}/ask/`, {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: q, top_k: 5 }),
          signal: AbortSignal.timeout(40_000),
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.error ?? `Error ${res.status}`);

        setResult(data);

        // guardar en historial (máx 10, sin duplicados)
        setHistory((prev) => [q, ...prev.filter((h) => h !== q)].slice(0, 10));
      } catch (e) {
        setError(
          e.name === "TimeoutError"
            ? "El servidor tardó demasiado. ¿Está Colab corriendo?"
            : e.message,
        );
      } finally {
        setLoading(false);
      }
    },
    [query, loading],
  );

  function handleKeyDown(e) {
    if (e.key === "Enter") handleSubmit();
  }

  function useHistoryItem(q) {
    setQuery(q);
    handleSubmit(q);
  }

  // ── render ──────────────────────────────────────────────────────
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-heading font-bold">Consulta IA / RAG</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Buscador inteligente sobre reglamentación FIFA y LaLiga
        </p>
      </div>

      {/* Status del servidor */}
      <div className="flex items-center gap-2 text-xs">
        {serverOk === null && (
          <Loader2 className="w-3 h-3 animate-spin text-muted-foreground" />
        )}
        {serverOk === true && <Wifi className="w-3 h-3 text-green-500" />}
        {serverOk === false && <WifiOff className="w-3 h-3 text-red-500" />}
        <span
          className={
            serverOk === true
              ? "text-green-500"
              : serverOk === false
                ? "text-red-500"
                : "text-muted-foreground"
          }
        >
          {serverOk === null && "Verificando conexión..."}
          {serverOk === true &&
            "Servidor RAG conectado · 3028 chunks · llama-3.1-8b"}
          {serverOk === false &&
            "Sin conexión — actualiza RAG_API_URL en settings.py"}
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* ── Panel principal ── */}
        <div className="lg:col-span-3 space-y-4">
          {/* Barra de búsqueda */}
          <div className="glass-card p-4">
            <div className="flex gap-2">
              <Input
                placeholder="Escribe tu pregunta sobre el reglamento..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={loading}
                className="bg-muted/50 border-border/50"
              />
              <Button
                onClick={() => handleSubmit()}
                disabled={loading || !query.trim()}
                className="gap-2 shrink-0"
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
                {loading ? "Consultando..." : "Consultar"}
              </Button>
            </div>

            {/* Chips de preguntas rápidas */}
            <div className="flex flex-wrap gap-2 mt-3">
              {QUICK_CHIPS.map((c) => (
                <button
                  key={c}
                  onClick={() => {
                    setQuery(c);
                    handleSubmit(c);
                  }}
                  disabled={loading}
                  className="text-[11px] px-3 py-1 rounded-full border border-border/40
                             text-muted-foreground hover:border-primary/50 hover:text-foreground
                             transition-colors disabled:opacity-40"
                >
                  {c}
                </button>
              ))}
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="glass-card p-4 border border-red-500/30 text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Respuesta */}
          {result && (
            <div className="glass-card p-6 animate-slide-up">
              <div className="flex items-center gap-2 mb-4">
                <BookOpen className="w-4 h-4 text-primary" />
                <h3 className="font-heading font-semibold text-sm">
                  Respuesta Generada
                </h3>
              </div>

              <p className="text-sm text-foreground/90 leading-relaxed whitespace-pre-wrap mb-6">
                {result.answer}
              </p>

              {/* Fuentes */}
              {result.chunks?.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                    Fuentes Documentales
                  </h4>
                  <div className="space-y-2">
                    {result.chunks.map((c, i) => (
                      <div
                        key={i}
                        className="flex items-start gap-3 p-3 rounded-lg bg-muted/30 border border-border/30"
                      >
                        <FileText className="w-4 h-4 text-accent mt-0.5 shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between gap-2">
                            <p className="text-xs font-medium text-foreground truncate">
                              {c.doc_name ?? c.doc}
                            </p>
                            <span className="text-[10px] font-mono text-primary shrink-0">
                              {Math.round((c.score ?? 0) * 100)}%
                            </span>
                          </div>
                          {c.page != null && (
                            <p className="text-[10px] text-muted-foreground">
                              Pág. {c.page}
                            </p>
                          )}
                          {c.content && (
                            <p className="text-[11px] text-muted-foreground mt-1 line-clamp-2">
                              {c.content}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Fuentes desde "sources" (formato alternativo del RAG) */}
              {!result.chunks?.length && result.sources?.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                    Fuentes Documentales
                  </h4>
                  <div className="space-y-2">
                    {result.sources.map((s, i) => (
                      <div
                        key={i}
                        className="flex items-start gap-3 p-3 rounded-lg bg-muted/30 border border-border/30"
                      >
                        <FileText className="w-4 h-4 text-accent mt-0.5 shrink-0" />
                        <div>
                          <p className="text-xs font-medium text-foreground">
                            {s.doc}
                          </p>
                          <p className="text-[10px] text-muted-foreground">
                            Pág. {s.page} · score:{" "}
                            {Math.round((s.score ?? 0) * 100)}%
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* ── Historial ── */}
        <div className="glass-card p-5 h-fit">
          <div className="flex items-center gap-2 mb-4">
            <Clock className="w-4 h-4 text-muted-foreground" />
            <h3 className="font-heading font-semibold text-sm">Historial</h3>
          </div>

          {history.length === 0 ? (
            <p className="text-[11px] text-muted-foreground">
              Tus consultas aparecerán aquí
            </p>
          ) : (
            <div className="space-y-2">
              {history.map((q, i) => (
                <button
                  key={i}
                  className="w-full text-left p-3 rounded-lg bg-muted/30 hover:bg-muted/60 transition-colors"
                  onClick={() => useHistoryItem(q)}
                >
                  <p className="text-[11px] text-foreground/80 line-clamp-2">
                    {q}
                  </p>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
