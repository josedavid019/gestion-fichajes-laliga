import {
  Send,
  Clock,
  BookOpen,
  FileText,
  Wifi,
  WifiOff,
  Loader2,
} from "lucide-react";
import { Trash2 } from "lucide-react";
import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { fetchWithAuth } from "@/lib/fetchWithAuth";

const BASE = import.meta.env.VITE_DJANGO_URL ?? "http://localhost:8000";
const RAG = `${BASE}/api/rag`;

const QUICK_CHIPS = [
  "¿Cómo se calcula el límite salarial o tope de gasto de un club en LaLiga?",
  "¿Qué requisitos debe cumplir un jugador sub-23 para ser inscrito en la plantilla de un club de LaLiga?",
  "¿Qué documentos exige la FIFA para completar una transferencia internacional de un jugador profesional?",
  "¿Qué sanciones puede imponer LaLiga a un club que incumpla el control económico o supere su límite de gasto?",
  "¿Cuánto tiempo dura máximo un contrato de jugador profesional?",
];

export default function AIQuery() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null); // { answer, chunks }
  const [error, setError] = useState(null);
  const [history, setHistory] = useState<any[]>([]);
  const [serverOk, setServerOk] = useState(null); // null | true | false

  const fetchHistory = useCallback(async () => {
    try {
      const res = await fetchWithAuth(`${RAG}/history/`, {
        method: "GET",
      });
      if (!res.ok) {
        if (res.status === 401 || res.status === 403) {
          setHistory([]);
          return;
        }
        throw new Error(`Error ${res.status}`);
      }
      const data = await res.json();
      // Keep full objects (question + answer) so clicking shows stored answer
      setHistory(data);
    } catch {
      setHistory([]);
    }
  }, []);
  const deleteHistoryItem = useCallback(
    async (id) => {
      if (!window.confirm("¿Borrar esta entrada del historial?")) return;
      try {
        const res = await fetchWithAuth(`${RAG}/history/${id}/`, {
          method: "DELETE",
        });
        if (!res.ok) throw new Error("No se pudo borrar");
        setHistory((h) => h.filter((it) => it.id !== id));
        // If currently showing that result, clear it
        if (result && result.query_id === id) setResult(null);
      } catch (e) {
        console.error(e);
        alert("Error al borrar la entrada");
      }
    },
    [result],
  );

  const clearAllHistory = useCallback(async () => {
    if (
      !window.confirm(
        "¿Borrar todo el historial? Esta acción no se puede deshacer.",
      )
    )
      return;
    try {
      const res = await fetchWithAuth(`${RAG}/history/clear/`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("No se pudo borrar todo");
      setHistory([]);
      setResult(null);
    } catch (e) {
      console.error(e);
      alert("Error al borrar todo el historial");
    }
  }, []);

  // ── health check ────────────────────────────────────────────────
  useEffect(() => {
    fetchWithAuth(`${RAG}/health/`)
      .then((r) => setServerOk(r.ok))
      .catch(() => setServerOk(false));
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  // ── consulta al RAG ─────────────────────────────────────────────
  const handleSubmit = useCallback(
    async (question = undefined) => {
      const q = (question ?? query).trim();
      if (!q || loading) return;

      setLoading(true);
      setError(null);
      setResult(null);

      try {
        const res = await fetchWithAuth(`${RAG}/ask/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: q, top_k: 5 }),
          signal: AbortSignal.timeout(40_000),
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.error ?? `Error ${res.status}`);

        setResult(data);
        fetchHistory();
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

  function useHistoryItem(item) {
    // When clicking history, show stored question + answer without requerying
    setQuery(item.question || "");
    if (item.answer) {
      setResult({
        answer: item.answer.answer_text,
        chunks: item.answer.sources,
      });
    } else {
      setResult(null);
    }
  }

  // ── render ──────────────────────────────────────────────────────
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-heading font-bold">
          Consulta de reglamento
        </h1>
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
            {!result && (
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
            )}
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
          <div className="flex items-center justify-between gap-2 mb-4">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-muted-foreground" />
              <h3 className="font-heading font-semibold text-sm">Historial</h3>
            </div>
            {history.length > 0 && (
              <Button size="sm" variant="ghost" onClick={clearAllHistory}>
                <Trash2 className="w-4 h-4 mr-2" />
                Borrar todo
              </Button>
            )}
          </div>

          {history.length === 0 ? (
            <p className="text-[11px] text-muted-foreground">
              Tus consultas aparecerán aquí
            </p>
          ) : (
            <div className="space-y-2">
              {history.map((item, i) => (
                <div
                  key={i}
                  className="w-full flex items-start justify-between p-3 rounded-lg bg-muted/30 hover:bg-muted/60 transition-colors"
                >
                  <button
                    className="text-left flex-1"
                    onClick={() => useHistoryItem(item)}
                  >
                    <p className="text-[11px] text-foreground/80 line-clamp-2">
                      {item.question}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      {item.answer?.answer_text && (
                        <p className="text-[11px] text-muted-foreground line-clamp-2">
                          {item.answer.answer_text}
                        </p>
                      )}
                      <span className="text-[10px] text-muted-foreground ml-2">
                        {item.created_at
                          ? new Date(item.created_at).toLocaleString()
                          : ""}
                      </span>
                    </div>
                  </button>

                  <button
                    className="ml-3 text-red-500 hover:text-red-700"
                    onClick={() => deleteHistoryItem(item.id)}
                    aria-label="Borrar historial"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
