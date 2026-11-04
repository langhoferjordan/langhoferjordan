"""A small, deterministic retrieval-evaluation reference implementation.

No external packages, no network requests, no model calls.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import log, sqrt
import re


STOP_WORDS = frozenset({"a", "an", "and", "are", "for", "how", "in", "is", "of", "on", "the", "to", "what", "with"})


def tokens(text: str) -> list[str]:
    """Normalize content to simple alphanumeric terms."""
    return [word for word in re.findall(r"[a-z0-9]+", text.lower()) if word not in STOP_WORDS]


@dataclass(frozen=True)
class Document:
    doc_id: str
    text: str


@dataclass(frozen=True)
class QueryCase:
    query: str
    relevant_ids: frozenset[str]


def retrieve(query: str, documents: list[Document], k: int = 3) -> list[str]:
    """Rank documents by a transparent normalized TF-IDF-style cosine score."""
    if k < 1:
        raise ValueError("k must be at least 1")
    if len({doc.doc_id for doc in documents}) != len(documents):
        raise ValueError("document IDs must be unique")
    if not documents:
        return []

    doc_terms = [Counter(tokens(doc.text)) for doc in documents]
    frequency = Counter(term for counts in doc_terms for term in counts)
    n = len(documents)
    idf = {term: log((n + 1) / (freq + 1)) + 1 for term, freq in frequency.items()}

    def weighted(counts: Counter[str]) -> dict[str, float]:
        return {term: (1 + log(count)) * idf.get(term, 0.0) for term, count in counts.items() if term in idf}

    q_vec = weighted(Counter(tokens(query)))
    q_norm = sqrt(sum(value * value for value in q_vec.values()))
    if q_norm == 0:
        return []

    matches = []
    for doc, counts in zip(documents, doc_terms):
        d_vec = weighted(counts)
        d_norm = sqrt(sum(value * value for value in d_vec.values()))
        dot = sum(value * d_vec.get(term, 0.0) for term, value in q_vec.items())
        similarity = dot / (q_norm * d_norm) if d_norm else 0.0
        if similarity > 0:
            matches.append((doc.doc_id, similarity))
    return [doc_id for doc_id, _ in sorted(matches, key=lambda pair: (-pair[1], pair[0]))[:k]]


def evaluate_ranking(retrieved_ids: list[str], relevant_ids: frozenset[str], k: int) -> dict[str, float]:
    if k < 1:
        raise ValueError("k must be at least 1")
    top_ids = retrieved_ids[:k]
    hits = sum(doc_id in relevant_ids for doc_id in top_ids)
    reciprocal_rank = next((1 / rank for rank, doc_id in enumerate(top_ids, start=1) if doc_id in relevant_ids), 0.0)
    return {
        "precision_at_k": hits / k,
        "recall_at_k": hits / len(relevant_ids) if relevant_ids else 0.0,
        "reciprocal_rank": reciprocal_rank,
    }


def evaluate(cases: list[QueryCase], documents: list[Document], k: int = 2) -> dict[str, float]:
    if not cases:
        raise ValueError("evaluation needs at least one query case")
    results = [evaluate_ranking(retrieve(case.query, documents, k), case.relevant_ids, k) for case in cases]
    return {
        "mean_precision_at_k": sum(row["precision_at_k"] for row in results) / len(results),
        "mean_recall_at_k": sum(row["recall_at_k"] for row in results) / len(results),
        "mrr_at_k": sum(row["reciprocal_rank"] for row in results) / len(results),
        "queries": float(len(cases)),
    }


if __name__ == "__main__":
    corpus = [
        Document("rag", "Retrieval augmented generation grounds model answers using relevant documents and citations."),
        Document("approval", "Human approval gates are useful before agents execute consequential actions or tool calls."),
        Document("monitoring", "Production AI observability tracks model errors latency token costs and reliability."),
        Document("vector", "Vector databases and embeddings enable semantic retrieval for knowledge search."),
    ]
    tests = [
        QueryCase("How do documents and citations ground RAG answers?", frozenset({"rag"})),
        QueryCase("Human approval before tool calls", frozenset({"approval"})),
        QueryCase("Monitor AI latency and model errors", frozenset({"monitoring"})),
    ]
    for key, value in evaluate(tests, corpus, k=2).items():
        print(f"{key}: {value:.3f}")
