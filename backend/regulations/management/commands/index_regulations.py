import os
import numpy as np
from django.core.management.base import BaseCommand
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from regulations.models import RegulationDocument, RegulationChunk

CHUNK_SIZE = 450
CHUNK_OVERLAP = 60
RUIDO_KEYWORDS = [
    "apuestas deportivas",
    "máquinas recreativas",
    "casinos",
    "regulación del juego",
    "dopaje",
    "sustancias prohibidas",
    "irpf",
    "declaración de la renta",
    "agencia tributaria",
    "boletín oficial del estado",
    "boe núm",
]


def chunk_es_util(texto):
    t = texto.lower()
    return sum(1 for k in RUIDO_KEYWORDS if k in t) < 2


class Command(BaseCommand):
    help = "Indexa PDFs de reglamentos en pgvector"

    def add_arguments(self, parser):
        parser.add_argument("pdf_dir", type=str, help="Carpeta con los PDFs")

    def handle(self, *args, **options):
        model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        pdf_dir = options["pdf_dir"]

        for filename in os.listdir(pdf_dir):
            if not filename.lower().endswith(".pdf"):
                continue
            path = os.path.join(pdf_dir, filename)
            doc_title = filename.replace(".pdf", "").replace("_", " ").title()

            doc, created = RegulationDocument.objects.get_or_create(
                title=doc_title,
                defaults={
                    "doc_type": (
                        "fifa_regulation"
                        if "fifa" in filename.lower()
                        else "laliga_regulation"
                    ),
                    "language": "es",
                    "version": "v1",
                },
            )
            if not created:
                self.stdout.write(f"  ⏭  {filename} ya indexado")
                continue

            # Extraer páginas
            reader = PdfReader(path)
            pages = []
            for i, page in enumerate(reader.pages, start=1):
                text = " ".join((page.extract_text() or "").split())
                if len(text) > 80:
                    pages.append({"page": i, "text": text})

            # Hacer chunks
            all_words, word_pages = [], []
            for p in pages:
                w = p["text"].split()
                all_words.extend(w)
                word_pages.extend([p["page"]] * len(w))

            chunks_data, start = [], 0
            while start < len(all_words):
                end = min(start + CHUNK_SIZE, len(all_words))
                text = " ".join(all_words[start:end]).strip()
                if len(text) > 40 and chunk_es_util(text):
                    chunks_data.append(
                        {
                            "content": text,
                            "page": word_pages[start],
                            "index": len(chunks_data),
                        }
                    )
                start += CHUNK_SIZE - CHUNK_OVERLAP

            # Generar embeddings en batch
            texts = [c["content"] for c in chunks_data]
            embeddings = model.encode(texts, batch_size=64, show_progress_bar=True)

            # Guardar en BD
            objs = [
                RegulationChunk(
                    document=doc,
                    chunk_index=c["index"],
                    page=c["page"],
                    content=c["content"],
                    embedding=embeddings[i].tolist(),
                    is_useful=True,
                )
                for i, c in enumerate(chunks_data)
            ]
            RegulationChunk.objects.bulk_create(objs, batch_size=200)
            self.stdout.write(f"  ✅ {filename} → {len(objs)} chunks")
