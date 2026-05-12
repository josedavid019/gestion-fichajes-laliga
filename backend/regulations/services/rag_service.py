import numpy as np
from sentence_transformers import SentenceTransformer
from groq import Groq
from django.conf import settings
from ..models import RegulationChunk

# ── Modelo singleton (se carga una sola vez) ──────────────────────
_embed_model = None


def get_embed_model():
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return _embed_model


SYSTEM_PROMPT = """Eres un asistente jurídico-deportivo especializado en reglamentos de fútbol profesional.
Respondes preguntas sobre fichajes, contratos, control económico, inscripción de jugadores,
normativas de FIFA y LaLiga.

REGLAS:
- Usa TODA la información disponible en los fragmentos para construir una respuesta completa.
- Si un fragmento contiene datos relacionados con la pregunta, úsalos aunque no sean la respuesta exacta.
- Sintetiza la información de varios fragmentos cuando sea necesario.
- Sé directo y concreto — responde la pregunta primero, luego cita las fuentes.
- Cita siempre el documento y la página de cada afirmación importante.
- Responde en español con precisión jurídica.
- Solo di "Esta información no figura en los documentos disponibles" si los fragmentos son completamente irrelevantes."""


def search_chunks(query: str, top_k: int = 5, min_score: float = 0.30) -> list[dict]:
    """Búsqueda semántica contra pgvector en Neon."""
    model = get_embed_model()
    q_vec = model.encode(query)
    q_norm = q_vec / (np.linalg.norm(q_vec) + 1e-10)

    # pgvector con cosine distance — traemos más y filtramos
    from pgvector.django import CosineDistance

    chunks_qs = (
        RegulationChunk.objects.filter(is_useful=True, embedding__isnull=False)
        .annotate(score=1 - CosineDistance("embedding", q_norm.tolist()))
        .filter(score__gte=min_score)
        .select_related("document")
        .order_by("-score")[: top_k * 2]  # traer más para deduplicar
    )

    results, seen = [], {}
    for chunk in chunks_qs:
        if len(results) >= top_k:
            break
        key = f"{chunk.document_id}_p{chunk.page}"
        if seen.get(key, 0) >= 2:
            continue
        seen[key] = seen.get(key, 0) + 1
        results.append(
            {
                "chunk_id": chunk.id,
                "doc_id": chunk.document_id,
                "doc_name": chunk.document.title,
                "page": chunk.page,
                "content": chunk.content,
                "score": round(float(chunk.score), 4),
            }
        )
    return results


def build_prompt(question: str, chunks: list[dict]) -> str:
    ctx = ""
    for i, c in enumerate(chunks, 1):
        ctx += f'\n[Fragmento {i} — {c["doc_name"]} pág. {c["page"]}]\n{c["content"]}\n'
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"=== FRAGMENTOS DE REGLAMENTO ==={ctx}"
        f"=== FIN FRAGMENTOS ===\n\n"
        f"PREGUNTA: {question}\n\nRESPUESTA:"
    )


def rag_query(question: str, top_k: int = 3) -> dict:
    """Pipeline RAG completo. Devuelve answer + chunks usados."""
    chunks = search_chunks(question, top_k=top_k)

    if not chunks:
        return {
            "answer": "Esta información no figura en los documentos disponibles.",
            "chunks": [],
            "model": "llama-3.1-8b-instant",
        }

    client = Groq(api_key=settings.GROQ_API_KEY)
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": build_prompt(question, chunks)}],
        max_tokens=1200,
        temperature=0.1,
    )

    return {
        "answer": resp.choices[0].message.content.strip(),
        "chunks": chunks,
        "model": "llama-3.1-8b-instant",
    }
