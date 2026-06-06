"""
tests/test_cosine.py
=====================
Unit tests for cosine_similarity, jaccard_similarity, and helpers.
Run: python -m pytest tests/ -v
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.cosine_similarity import (
    cosine_similarity,
    cosine_similarity_matrix,
    jaccard_similarity,
    top_overlapping_skills,
    compare_metrics,
)


class TestCosineSimilarity:
    def test_identical_vectors_score_one(self):
        v = {"python": 0.6, "sql": 0.8}
        assert abs(cosine_similarity(v, v) - 1.0) < 1e-9

    def test_orthogonal_vectors_score_zero(self):
        a = {"python": 1.0}
        b = {"javascript": 1.0}
        assert cosine_similarity(a, b) == 0.0

    def test_empty_vector_returns_zero(self):
        a = {"python": 0.5}
        assert cosine_similarity(a, {}) == 0.0
        assert cosine_similarity({}, a) == 0.0
        assert cosine_similarity({}, {}) == 0.0

    def test_score_in_valid_range(self):
        a = {"python": 0.4, "sql": 0.3, "ml": 0.5}
        b = {"python": 0.6, "react": 0.4}
        score = cosine_similarity(a, b)
        assert 0.0 <= score <= 1.0

    def test_partial_overlap_between_zero_and_one(self):
        a = {"python": 1.0, "sql": 0.0}
        b = {"python": 0.0, "sql": 1.0}
        score = cosine_similarity(a, b)
        assert 0.0 <= score <= 1.0

    def test_symmetry(self):
        """cosine(a, b) must equal cosine(b, a)."""
        a = {"python": 0.5, "docker": 0.3}
        b = {"python": 0.4, "sql": 0.6}
        assert abs(cosine_similarity(a, b) - cosine_similarity(b, a)) < 1e-9

    def test_l2_normalised_vectors_dot_product_equals_cosine(self):
        """After L2 normalisation, cos(a,b) == a·b."""
        a = {"x": 3.0, "y": 4.0}
        # Normalise manually
        mag_a = math.sqrt(3**2 + 4**2)
        na = {k: v / mag_a for k, v in a.items()}

        b = {"x": 4.0, "y": 3.0}
        mag_b = math.sqrt(4**2 + 3**2)
        nb = {k: v / mag_b for k, v in b.items()}

        dot = na["x"] * nb["x"] + na["y"] * nb["y"]
        cos = cosine_similarity(na, nb)
        assert abs(dot - cos) < 1e-9

    def test_zero_magnitude_returns_zero(self):
        a = {"python": 0.0}
        b = {"python": 0.5}
        # 0-magnitude vector — must not raise ZeroDivisionError
        assert cosine_similarity(a, b) == 0.0


class TestCosineSimilarityMatrix:
    def test_diagonal_is_one(self):
        vecs = [{"a": 1.0}, {"b": 1.0}, {"c": 1.0}]
        matrix = cosine_similarity_matrix(vecs)
        for i in range(len(vecs)):
            assert matrix[i][i] == 1.0

    def test_matrix_is_symmetric(self):
        vecs = [{"a": 0.5, "b": 0.5}, {"a": 0.3, "c": 0.7}, {"b": 0.6, "d": 0.4}]
        matrix = cosine_similarity_matrix(vecs)
        n = len(vecs)
        for i in range(n):
            for j in range(n):
                assert abs(matrix[i][j] - matrix[j][i]) < 1e-9

    def test_correct_dimensions(self):
        vecs = [{"a": 1.0}] * 5
        matrix = cosine_similarity_matrix(vecs)
        assert len(matrix) == 5
        assert all(len(row) == 5 for row in matrix)

    def test_orthogonal_vectors_off_diagonal_zero(self):
        vecs = [{"a": 1.0}, {"b": 1.0}, {"c": 1.0}]
        matrix = cosine_similarity_matrix(vecs)
        assert matrix[0][1] == 0.0
        assert matrix[1][2] == 0.0


class TestJaccardSimilarity:
    def test_identical_sets_score_one(self):
        a = ["python", "sql"]
        assert abs(jaccard_similarity(a, a) - 1.0) < 1e-9

    def test_disjoint_sets_score_zero(self):
        assert jaccard_similarity(["python"], ["javascript"]) == 0.0

    def test_empty_both_returns_zero(self):
        assert jaccard_similarity([], []) == 0.0

    def test_partial_overlap(self):
        # overlap = {python}, union = {python, sql, react} → 1/3
        score = jaccard_similarity(["python", "sql"], ["python", "react"])
        assert abs(score - 1 / 3) < 1e-9

    def test_case_insensitive(self):
        a = ["Python", "SQL"]
        b = ["python", "sql"]
        assert abs(jaccard_similarity(a, b) - 1.0) < 1e-9

    def test_score_in_valid_range(self):
        score = jaccard_similarity(["python", "ml", "docker"], ["docker", "kubernetes"])
        assert 0.0 <= score <= 1.0


class TestTopOverlappingSkills:
    def test_returns_correct_overlap(self):
        user  = ["python", "docker", "sql"]
        role  = ["python", "docker", "react"]
        result = top_overlapping_skills(user, role, n=2)
        assert set(result).issubset({"python", "docker"})

    def test_respects_n_limit(self):
        user  = ["python", "sql", "docker", "linux"]
        role  = ["python", "sql", "docker", "linux", "react"]
        assert len(top_overlapping_skills(user, role, n=2)) <= 2

    def test_no_overlap_returns_empty(self):
        result = top_overlapping_skills(["python"], ["javascript"])
        assert result == []

    def test_case_insensitive(self):
        result = top_overlapping_skills(["Python", "SQL"], ["python", "sql"])
        assert len(result) >= 1


class TestCompareMetrics:
    def test_returns_expected_keys(self):
        result = compare_metrics(["python", "sql"], ["python", "docker"], 0.75)
        assert "tfidf_cosine" in result
        assert "jaccard" in result
        assert "overlap" in result
        assert "note" in result

    def test_tfidf_score_preserved(self):
        result = compare_metrics(["python"], ["python", "sql"], 0.842)
        assert result["tfidf_cosine"] == 0.842


# ── Run directly ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    classes = [
        TestCosineSimilarity,
        TestCosineSimilarityMatrix,
        TestJaccardSimilarity,
        TestTopOverlappingSkills,
        TestCompareMetrics,
    ]
    passed = failed = 0
    for cls in classes:
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
