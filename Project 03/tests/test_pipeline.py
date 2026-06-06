"""
tests/test_pipeline.py
=======================
Integration tests for RecommenderPipeline (all 4 steps).
Run: python -m pytest tests/ -v
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.recommender_pipeline import RecommenderPipeline, Recommendation


def make_pipeline() -> RecommenderPipeline:
    p = RecommenderPipeline(top_n=3)
    p.load()
    return p


class TestPipelineLoad:
    def test_load_succeeds(self):
        p = make_pipeline()
        assert p._loaded is True

    def test_dataset_not_empty(self):
        p = make_pipeline()
        assert len(p.dataset) >= 10

    def test_role_vectors_match_dataset(self):
        p = make_pipeline()
        assert len(p._role_vectors) == len(p.dataset)

    def test_recommend_before_load_raises(self):
        p = RecommenderPipeline()
        try:
            p.recommend(["python"])
            assert False, "Should have raised RuntimeError"
        except RuntimeError:
            pass


class TestRecommendPipeline:
    def test_returns_list(self):
        p = make_pipeline()
        results = p.recommend(["Python", "Machine Learning", "Docker"])
        assert isinstance(results, list)

    def test_returns_top_n_results(self):
        p = make_pipeline()
        results = p.recommend(["Python", "Machine Learning", "Docker"])
        assert len(results) == 3

    def test_result_type_is_recommendation(self):
        p = make_pipeline()
        results = p.recommend(["Python", "SQL", "Spark"])
        assert all(isinstance(r, Recommendation) for r in results)

    def test_ranks_are_sequential(self):
        p = make_pipeline()
        results = p.recommend(["JavaScript", "React", "CSS"])
        assert [r.rank for r in results] == [1, 2, 3]

    def test_scores_are_descending(self):
        p = make_pipeline()
        results = p.recommend(["Python", "TensorFlow", "Deep Learning"])
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_scores_in_valid_range(self):
        p = make_pipeline()
        results = p.recommend(["Docker", "Kubernetes", "CI CD"])
        for r in results:
            assert 0.0 <= r.score <= 1.0, f"Score {r.score} out of range for {r.role}"

    def test_why_match_not_empty(self):
        p = make_pipeline()
        results = p.recommend(["Python", "SQL", "Spark"])
        for r in results:
            assert len(r.why_match) >= 1

    def test_roles_are_strings(self):
        p = make_pipeline()
        results = p.recommend(["Python", "Machine Learning", "Statistics"])
        for r in results:
            assert isinstance(r.role, str) and r.role

    def test_score_pct_format(self):
        p = make_pipeline()
        results = p.recommend(["Python", "Docker", "Linux"])
        for r in results:
            assert r.score_pct.endswith("%")

    def test_data_engineer_match(self):
        """Skills strongly matching Data Engineer should rank it highly."""
        p = make_pipeline()
        results = p.recommend(["python", "spark", "kafka", "sql", "airflow"])
        top_roles = [r.role for r in results]
        assert "Data Engineer" in top_roles

    def test_frontend_match(self):
        """Frontend-specific skills should surface Frontend Developer."""
        p = make_pipeline()
        results = p.recommend(["javascript", "react", "css", "html"])
        top_roles = [r.role for r in results]
        assert "Frontend Developer" in top_roles

    def test_string_input(self):
        """Pipeline should accept comma-separated string input."""
        p = make_pipeline()
        results = p.recommend("Python, Machine Learning, Docker")
        assert len(results) == 3

    def test_top_n_respected(self):
        p = RecommenderPipeline(top_n=5)
        p.load()
        results = p.recommend(["Python", "SQL", "Docker", "Linux"])
        assert len(results) == 5


class TestColdStart:
    def test_too_few_skills_triggers_fallback(self):
        p = make_pipeline()
        results = p.recommend(["Python"])     # < 3 skills
        assert len(results) >= 3
        # All come from the trending fallback
        assert all(r.source in ("trending_fallback", "onboarding_survey") for r in results)

    def test_empty_input_triggers_fallback(self):
        p = make_pipeline()
        results = p.recommend([])
        assert len(results) >= 3

    def test_all_oov_triggers_fallback(self):
        p = make_pipeline()
        results = p.recommend(["xylophoneengineer", "bananascript", "coffeeos"])
        assert len(results) >= 3

    def test_minimum_top_n_is_three(self):
        """Even if caller sets top_n=1, minimum returned is 3."""
        p = RecommenderPipeline(top_n=1)
        p.load()
        results = p.recommend(["Python", "SQL", "Docker"])
        assert len(results) >= 3


class TestSimilarityMatrix:
    def test_matrix_dimensions(self):
        p = make_pipeline()
        roles, matrix = p.similarity_matrix()
        n = len(roles)
        assert len(matrix) == n
        assert all(len(row) == n for row in matrix)

    def test_diagonal_is_one(self):
        p = make_pipeline()
        _, matrix = p.similarity_matrix()
        for i in range(len(matrix)):
            assert abs(matrix[i][i] - 1.0) < 1e-6


class TestJaccardComparison:
    def test_returns_list(self):
        p = make_pipeline()
        result = p.jaccard_comparison(["Python", "SQL", "Spark"])
        assert isinstance(result, list)

    def test_contains_both_scores(self):
        p = make_pipeline()
        result = p.jaccard_comparison(["Python", "SQL", "Spark"], top_n=3)
        for item in result:
            assert "tfidf_cosine" in item
            assert "jaccard" in item
            assert "role" in item

    def test_tfidf_often_differs_from_jaccard(self):
        """
        For skill sets with rare terms, TF-IDF cosine should differ from Jaccard,
        demonstrating the added value of weighting.
        """
        p = make_pipeline()
        results = p.jaccard_comparison(["solidity", "ethereum", "smart contracts"], top_n=3)
        # At least one result should show different scores
        diffs = [abs(r["tfidf_cosine"] - r["jaccard"]) for r in results]
        assert max(diffs) > 0.0


class TestToDict:
    def test_to_dict_has_expected_keys(self):
        p = make_pipeline()
        r = p.recommend(["Python", "SQL", "Docker"])[0]
        d = r.to_dict()
        assert "rank" in d
        assert "role" in d
        assert "score" in d
        assert "score_pct" in d
        assert "why_match" in d
        assert "source" in d


# ── Run directly ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    classes = [
        TestPipelineLoad,
        TestRecommendPipeline,
        TestColdStart,
        TestSimilarityMatrix,
        TestJaccardComparison,
        TestToDict,
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
