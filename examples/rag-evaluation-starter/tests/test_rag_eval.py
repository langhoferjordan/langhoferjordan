from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rag_eval import Document, QueryCase, evaluate, evaluate_ranking, retrieve, tokens


class RetrievalEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.docs = [
            Document("a", "RAG answers use retrieved documents and citations"),
            Document("b", "Agents require approval before running tools"),
            Document("c", "Production systems monitor latency and costs"),
        ]

    def test_tokenization(self):
        self.assertEqual(tokens("The RAG, and APIs!"), ["rag", "apis"])

    def test_expected_document_ranks_first(self):
        self.assertEqual(retrieve("approval agents tools", self.docs, k=2)[0], "b")

    def test_zero_overlap_returns_no_documents(self):
        self.assertEqual(retrieve("unicorn elephants", self.docs), [])

    def test_duplicate_document_ids_rejected(self):
        with self.assertRaises(ValueError):
            retrieve("test", [Document("x", "test"), Document("x", "again")])

    def test_metrics_are_explicit(self):
        result = evaluate_ranking(["bad", "good"], frozenset({"good"}), k=2)
        self.assertEqual(result, {"precision_at_k": 0.5, "recall_at_k": 1.0, "reciprocal_rank": 0.5})

    def test_evaluation_output(self):
        result = evaluate([QueryCase("agents approval tools", frozenset({"b"}))], self.docs, k=2)
        self.assertEqual(result["queries"], 1)
        self.assertEqual(result["mrr_at_k"], 1)

    def test_invalid_k(self):
        with self.assertRaises(ValueError):
            retrieve("x", self.docs, k=0)


if __name__ == "__main__":
    unittest.main()
