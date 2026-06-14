"""
src/recommender_pipeline.py
============================
The 4-Step IPO Pipeline

  INPUT  → Step 1: Ingestion   — load dataset + parse user skills
         → Step 2: Scoring     — TF-IDF vectorise + cosine similarity
         → Step 3: Sorting     — rank by score descending
         → Step 4: Filtering   — return Top-N (min 3) with explanations
  OUTPUT → ranked recommendations with scores + why-it-matches

This is the only file your application needs to call directly.
All other modules are internal helpers.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field

from src.ingestion          import load_dataset, parse_user_input
from src.tfidf_vectorizer   import TFIDFVectorizer
from src.cosine_similarity  import (
    cosine_similarity,
    cosine_similarity_matrix,
    top_overlapping_skills,
    compare_metrics,
)
from src.cold_start_handler import ColdStartHandler


# ── Result dataclass ──────────────────────────────────────────────────────────

@dataclass
class Recommendation:
    rank:       int
    role:       str
    score:      float
    score_pct:  str
    why_match:  list[str]
    source:     str = "pipeline"     # "pipeline" | "trending_fallback" | "onboarding_survey"

    def to_dict(self) -> dict:
        return {
            "rank":      self.rank,
            "role":      self.role,
            "score":     self.score,
            "score_pct": self.score_pct,
            "why_match": self.why_match,
            "source":    self.source,
        }


# ── Pipeline ──────────────────────────────────────────────────────────────────

class RecommenderPipeline:
    """
    Full TF-IDF + cosine similarity recommendation pipeline.

    Typical usage:
        pipeline = RecommenderPipeline()
        pipeline.load()
        results  = pipeline.recommend(["Python", "Machine Learning", "Docker"])
    """

    def __init__(
        self,
        top_n: int = 3,
        dataset_path: str | None = None,
    ):
        self.top_n            = max(top_n, 3)     # minimum enforced = 3
        self._dataset_path    = dataset_path
        self._dataset: list[dict] = []
        self._vectorizer      = TFIDFVectorizer()
        self._role_vectors:   list[dict[str, float]] = []
        self._cold_start      = ColdStartHandler()
        self._loaded          = False

    # ── Step 1: Ingestion ─────────────────────────────────────────────────────

    def load(self) -> "RecommenderPipeline":
        """
        STEP 1 — INGESTION
        Load the job-role dataset and fit the TF-IDF vectorizer.
        Must be called once before recommend().
        """
        self._dataset = (
            load_dataset(self._dataset_path)
            if self._dataset_path
            else load_dataset()
        )

        if not self._dataset:
            raise ValueError("Dataset loaded but is empty.")

        # Fit vectorizer on all role skill lists
        corpus = [role["skills"] for role in self._dataset]
        self._vectorizer.fit(corpus)

        # Pre-compute and cache TF-IDF vectors for every role
        self._role_vectors = [
            self._vectorizer.transform(role["skills"])
            for role in self._dataset
        ]

        self._loaded = True
        return self

    # ── Full pipeline ─────────────────────────────────────────────────────────

    def recommend(
        self,
        raw_user_input,
        interactive_cold_start: bool = False,
    ) -> list[Recommendation]:
        """
        Run the full 4-step recommendation pipeline.

        Args:
            raw_user_input:           str or list[str] of skills/interests.
            interactive_cold_start:   If True and cold start is detected,
                                      run the CLI onboarding survey.
                                      If False, use trending fallback silently.

        Returns:
            List of Recommendation objects, length = self.top_n.
        """
        if not self._loaded:
            raise RuntimeError("Call .load() before .recommend().")

        # ── Parse user input ─────────────────────────────────────────────────
        user_skills = parse_user_input(raw_user_input)

        # ── Cold-start check ─────────────────────────────────────────────────
        coverage = self._vectorizer.coverage(user_skills)

        if self._cold_start.is_user_cold_start(user_skills, coverage):
            reason = self._cold_start.cold_start_reason(user_skills, coverage)
            if interactive_cold_start:
                raw_results = self._cold_start.run_onboarding_survey()
            else:
                raw_results = self._cold_start.trending_fallback(self.top_n)

            return [
                Recommendation(
                    rank      = i + 1,
                    role      = r["role"],
                    score     = r["score"] or 0.0,
                    score_pct = r["score_pct"],
                    why_match = r["why_match"],
                    source    = r["source"],
                )
                for i, r in enumerate(raw_results)
            ]

        # ── Step 2: Scoring ──────────────────────────────────────────────────
        # Vectorise user skills in the same TF-IDF space as the roles
        user_vector = self._vectorizer.transform(user_skills)

        if not user_vector:
            # All user skills were OOV — double fallback to trending
            return [
                Recommendation(
                    rank      = i + 1,
                    role      = r["role"],
                    score     = r["score"] or 0.0,
                    score_pct = r["score_pct"],
                    why_match = r["why_match"],
                    source    = r["source"],
                )
                for i, r in enumerate(self._cold_start.trending_fallback(self.top_n))
            ]

        scored = []
        for i, role in enumerate(self._dataset):
            score = cosine_similarity(user_vector, self._role_vectors[i])
            scored.append((role, score))

        # ── Step 3: Sorting ──────────────────────────────────────────────────
        scored.sort(key=lambda x: x[1], reverse=True)

        # ── Step 4: Filtering — Top-N ────────────────────────────────────────
        top = scored[: self.top_n]

        results = []
        for rank, (role, score) in enumerate(top, 1):
            overlap = top_overlapping_skills(user_skills, role["skills"], n=2)
            results.append(
                Recommendation(
                    rank      = rank,
                    role      = role["role"],
                    score     = round(score, 4),
                    score_pct = f"{score * 100:.1f}%",
                    why_match = overlap if overlap else ["General skill alignment"],
                    source    = "pipeline",
                )
            )

        return results

    # ── Extras ────────────────────────────────────────────────────────────────

    def similarity_matrix(self) -> tuple[list[str], list[list[float]]]:
        """
        Return pairwise cosine similarity matrix for all job roles.
        Used for similarity_matrix.csv generation and Flask analytics view.

        Returns:
            (role_names, matrix)
        """
        if not self._loaded:
            raise RuntimeError("Call .load() first.")
        roles  = [r["role"] for r in self._dataset]
        matrix = cosine_similarity_matrix(self._role_vectors)
        return roles, matrix

    def jaccard_comparison(
        self,
        raw_user_input,
        top_n: int = 3,
    ) -> list[dict]:
        """
        Return TF-IDF cosine vs Jaccard side-by-side for top-N roles.
        Bonus feature: shows why TF-IDF + cosine outperforms Jaccard.
        """
        if not self._loaded:
            raise RuntimeError("Call .load() first.")

        user_skills = parse_user_input(raw_user_input)
        user_vector = self._vectorizer.transform(user_skills)

        comparisons = []
        for i, role in enumerate(self._dataset):
            tfidf_score = cosine_similarity(user_vector, self._role_vectors[i])
            comp = compare_metrics(user_skills, role["skills"], tfidf_score)
            comp["role"] = role["role"]
            comparisons.append(comp)

        comparisons.sort(key=lambda x: x["tfidf_cosine"], reverse=True)
        return comparisons[:top_n]

    def export_similarity_matrix_csv(self, output_path: str) -> None:
        """Write the role × role similarity matrix to a CSV file."""
        roles, matrix = self.similarity_matrix()
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([""] + roles)
            for i, row in enumerate(matrix):
                writer.writerow([roles[i]] + [f"{v:.4f}" for v in row])

    @property
    def dataset(self) -> list[dict]:
        return self._dataset

    @property
    def vectorizer(self) -> TFIDFVectorizer:
        return self._vectorizer
