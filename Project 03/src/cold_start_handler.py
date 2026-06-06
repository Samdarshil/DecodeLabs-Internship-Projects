"""
src/cold_start_handler.py
==========================
Cold Start Handler

What is cold start?
  A recommendation system "cold starts" when it lacks enough signal
  to produce meaningful personalised results.

Two types handled:
  1. USER cold start  — user provides < 3 skills, or all skills are OOV
                        (Out Of Vocabulary — never seen during training).
     Fallbacks:
       a) Onboarding survey: map broad topic preference → curated role list
       b) Trending fallback: return globally popular roles by industry rank

  2. ITEM cold start — a new job role is added to the dataset with no
                        interaction history.
     Resolution: content-based filtering solves this automatically.
     A new role's skill metadata is vectorised immediately → no cold start.
     This is one of content filtering's key advantages over collaborative.
"""

from __future__ import annotations
from src.ingestion import load_fallback


# ── Thresholds ────────────────────────────────────────────────────────────────
MIN_SKILLS_REQUIRED   = 3     # fewer than this triggers cold-start check
MIN_VOCAB_COVERAGE    = 0.30  # if <30% of user skills are in vocab → cold start


class ColdStartHandler:
    """
    Detect cold-start conditions and supply fallback recommendations.
    """

    def __init__(self, fallback_path: str | None = None):
        self._fallback = load_fallback(fallback_path) if fallback_path else load_fallback()

    # ── Detection ─────────────────────────────────────────────────────────────

    def is_user_cold_start(
        self,
        user_skills: list[str],
        vocab_coverage: float,
    ) -> bool:
        """
        Return True when the pipeline cannot produce reliable results.

        Triggers:
          - Fewer than MIN_SKILLS_REQUIRED skills provided, OR
          - Vocabulary coverage below MIN_VOCAB_COVERAGE threshold
        """
        too_few   = len(user_skills) < MIN_SKILLS_REQUIRED
        oov_heavy = vocab_coverage < MIN_VOCAB_COVERAGE
        return too_few or oov_heavy

    def cold_start_reason(
        self,
        user_skills: list[str],
        vocab_coverage: float,
    ) -> str:
        """Human-readable explanation of why cold start was triggered."""
        reasons = []
        if len(user_skills) < MIN_SKILLS_REQUIRED:
            reasons.append(
                f"Only {len(user_skills)} skill(s) provided "
                f"(minimum required: {MIN_SKILLS_REQUIRED})"
            )
        if vocab_coverage < MIN_VOCAB_COVERAGE:
            reasons.append(
                f"Only {vocab_coverage:.0%} of your skills are recognised "
                f"(threshold: {MIN_VOCAB_COVERAGE:.0%})"
            )
        return " | ".join(reasons) if reasons else "Unknown cold-start trigger"

    # ── Fallback A: Trending ──────────────────────────────────────────────────

    def trending_fallback(self, top_n: int = 3) -> list[dict]:
        """
        Return top-N globally trending roles with popularity scores.
        Used when user provides no usable input.

        Returns:
            [{"role": str, "score": float, "reason": str, "why_match": [...]}]
        """
        trending = self._fallback.get("trending", [])[:top_n]
        return [
            {
                "role":       item["role"],
                "score":      item["popularity_score"],
                "score_pct":  f"{item['popularity_score'] * 100:.1f}%",
                "why_match":  ["Industry trending role"],
                "reason":     item["reason"],
                "source":     "trending_fallback",
            }
            for item in trending
        ]

    # ── Fallback B: Onboarding survey ─────────────────────────────────────────

    def onboarding_topics(self) -> list[str]:
        """Return the list of broad topic areas for the onboarding survey."""
        return self._fallback.get("onboarding_topics", [])

    def recommend_from_topic(self, topic: str, top_n: int = 3) -> list[dict]:
        """
        Map a broad topic (e.g. 'artificial intelligence') to curated roles.

        Args:
            topic:  One of the strings returned by onboarding_topics().
            top_n:  How many roles to return.

        Returns:
            List of recommendation dicts (same shape as trending_fallback).
        """
        mapping = self._fallback.get("topic_to_roles", {})
        roles   = mapping.get(topic.lower(), [])[:top_n]

        if not roles:
            return self.trending_fallback(top_n)   # double fallback

        return [
            {
                "role":      role,
                "score":     None,
                "score_pct": "N/A (topic match)",
                "why_match": [f"Matched topic: {topic}"],
                "reason":    f"Curated path for '{topic}' interest",
                "source":    "onboarding_survey",
            }
            for role in roles
        ]

    def run_onboarding_survey(self) -> list[dict]:
        """
        CLI-interactive onboarding survey.
        Prompts user to pick a broad topic and returns curated roles.
        """
        topics = self.onboarding_topics()

        print("\n  Cold start detected — let's narrow things down.")
        print("  Which area interests you most?\n")
        for i, topic in enumerate(topics, 1):
            print(f"    {i}. {topic}")

        while True:
            raw = input("\n  Enter number (1–{}): ".format(len(topics))).strip()
            if raw.isdigit() and 1 <= int(raw) <= len(topics):
                chosen = topics[int(raw) - 1]
                return self.recommend_from_topic(chosen)
            print("  Invalid choice. Please enter a number from the list.")

    # ── Item cold start note ──────────────────────────────────────────────────

    @staticmethod
    def item_cold_start_note() -> str:
        """
        Explains why item cold start is not a problem for this system.
        Shown in CLI help and Flask UI analytics page.
        """
        return (
            "Item cold start is inherently solved by content-based filtering. "
            "New job roles are recommended immediately from their skill metadata — "
            "no interaction history or user ratings are required. "
            "This is the primary advantage of TF-IDF content filtering over "
            "collaborative filtering for structured domain knowledge."
        )
