"""
tests/test_tfidf.py
====================
Unit tests for TFIDFVectorizer.
Run: python -m pytest tests/ -v
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tfidf_vectorizer import TFIDFVectorizer


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_vectorizer():
    corpus = [
        ["python", "sql", "machine learning"],
        ["javascript", "react", "css"],
        ["python", "docker", "kubernetes"],
        ["sql", "spark", "hadoop"],
    ]
    v = TFIDFVectorizer()
    v.fit(corpus)
    return v, corpus


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestFit:
    def test_vocabulary_built(self):
        v, corpus = make_vectorizer()
        assert len(v.vocabulary) > 0

    def test_vocabulary_is_sorted(self):
        v, _ = make_vectorizer()
        assert v.vocabulary == sorted(v.vocabulary)

    def test_all_terms_in_vocab(self):
        v, corpus = make_vectorizer()
        for doc in corpus:
            for term in doc:
                assert term in v._vocab_index

    def test_idf_computed_for_all_terms(self):
        v, _ = make_vectorizer()
        for term in v.vocabulary:
            assert term in v._idf
            assert v._idf[term] > 0

    def test_rare_term_has_higher_idf(self):
        """'python' appears in 2/4 docs; 'spark' appears in 1/4. spark should score higher IDF."""
        v, _ = make_vectorizer()
        assert v._idf["spark"] > v._idf["python"]

    def test_empty_corpus_raises(self):
        v = TFIDFVectorizer()
        try:
            v.fit([])
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_vocab_size(self):
        v, corpus = make_vectorizer()
        all_terms = set(t for doc in corpus for t in doc)
        assert v.vocab_size() == len(all_terms)


class TestTransform:
    def test_output_is_dict(self):
        v, corpus = make_vectorizer()
        result = v.transform(corpus[0])
        assert isinstance(result, dict)

    def test_output_keys_are_in_vocab(self):
        v, corpus = make_vectorizer()
        result = v.transform(corpus[0])
        for term in result:
            assert term in v._vocab_index

    def test_oov_terms_excluded(self):
        v, _ = make_vectorizer()
        result = v.transform(["completelymadeupterm12345"])
        assert result == {}

    def test_empty_doc_returns_empty(self):
        v, _ = make_vectorizer()
        assert v.transform([]) == {}

    def test_l2_normalised_magnitude_is_one(self):
        v, corpus = make_vectorizer()
        result = v.transform(corpus[0], normalise=True)
        magnitude = math.sqrt(sum(x ** 2 for x in result.values()))
        assert abs(magnitude - 1.0) < 1e-6, f"Expected ~1.0, got {magnitude}"

    def test_no_normalise_flag(self):
        v, corpus = make_vectorizer()
        result = v.transform(corpus[0], normalise=False)
        magnitude = math.sqrt(sum(x ** 2 for x in result.values()))
        # Without normalisation, magnitude can be anything > 0
        assert magnitude > 0

    def test_weights_are_positive(self):
        v, corpus = make_vectorizer()
        result = v.transform(corpus[0])
        assert all(w > 0 for w in result.values())

    def test_transform_before_fit_raises(self):
        v = TFIDFVectorizer()
        try:
            v.transform(["python"])
            assert False, "Should have raised RuntimeError"
        except RuntimeError:
            pass


class TestCoverage:
    def test_full_coverage(self):
        v, corpus = make_vectorizer()
        assert v.coverage(corpus[0]) == 1.0

    def test_zero_coverage_oov(self):
        v, _ = make_vectorizer()
        assert v.coverage(["unknownterm1", "unknownterm2"]) == 0.0

    def test_partial_coverage(self):
        v, _ = make_vectorizer()
        skills = ["python", "unknownterm"]   # 1 known / 2 total = 0.5
        assert abs(v.coverage(skills) - 0.5) < 1e-9

    def test_empty_skills_zero_coverage(self):
        v, _ = make_vectorizer()
        assert v.coverage([]) == 0.0


class TestFitTransform:
    def test_returns_list_same_length_as_corpus(self):
        corpus = [["a", "b"], ["c", "d"], ["a", "c"]]
        v = TFIDFVectorizer()
        results = v.fit_transform(corpus)
        assert len(results) == len(corpus)

    def test_each_result_is_dict(self):
        corpus = [["python", "sql"], ["react", "css"]]
        v = TFIDFVectorizer()
        results = v.fit_transform(corpus)
        assert all(isinstance(r, dict) for r in results)


# ── Run directly ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import traceback

    test_classes = [TestFit, TestTransform, TestCoverage, TestFitTransform]
    passed = failed = 0

    for cls in test_classes:
        obj = cls()
        for name in [m for m in dir(cls) if m.startswith("test_")]:
            try:
                getattr(obj, name)()
                print(f"  ✅  {cls.__name__}.{name}")
                passed += 1
            except Exception as e:
                print(f"  ❌  {cls.__name__}.{name}  →  {e}")
                failed += 1

    print(f"\n  {passed} passed  |  {failed} failed")
