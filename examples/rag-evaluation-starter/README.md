# RAG Evaluation Starter

A **deterministic, dependency-free Python example** for evaluating the retrieval stage of a RAG workflow. It does not make LLM calls, generate answers, or pretend lexical search is production RAG. Its value is the transparent, testable evaluation harness.

## What it demonstrates

- Basic IDF-weighted lexical ranking over an in-memory document corpus
- Explicit query relevance judgments
- Precision@k, recall@k and mean reciprocal rank (MRR)
- Repeatable evaluation via a CLI and unit tests

## Run

From this directory:

```bash
python3 rag_eval.py
python3 -m unittest discover -s tests -v
```

No installation, external API keys or network access required.

## Next steps for production

Swap the lexical retriever for an embedding + vector database retriever, add reranking, document access controls, evaluation datasets derived from real user needs, observability, latency/cost benchmarks, and answer-grounding checks. Keep evaluation separate from retrieval infrastructure so it remains comparable across changes.

**Note:** Original learning/demo code — not extracted from any client project.
