import requests
from django.conf import settings

_TIMEOUT = 35  # segundos — Groq puede tardar en cargas altas


def _url(path: str) -> str:
    return f"{settings.RAG_API_URL.rstrip('/')}{path}"


def rag_query(question: str, top_k: int = 5) -> dict:
    """
    Llama a POST /rag en Colab.
    Retorna algo como:
        {
            "answer": "...",
            "chunks": [
                {"score": 0.87, "doc_name": "FIFA_reglamento.pdf",
                 "page": 12, "content": "..."},
                ...
            ]
        }
    """
    resp = requests.post(
        _url("/rag"),
        json={"question": question, "top_k": top_k},
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def rag_health() -> dict:
    resp = requests.get(_url("/health"), timeout=8)
    resp.raise_for_status()
    return resp.json()
