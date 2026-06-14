"""
src/cosine_similarity.py
=========================
Similarity metrics — implemented from scratch.

Two metrics provided:
  1. Cosine Similarity  — primary metric (used in production pipeline)
  2. Jaccard Similarity — bonus comparison (shows why cosine is better)

Why cosine over Euclidean distance?
  - Euclidean penalises document length. A role with 10 skills scores worse
    than one with 3 even if the overlap is identical.
  - Cosine measures the *angle* between vectors — purely directional.
  - After L2 normalisation, cosine(a, b) = dot(a, b), which is O(overlap)
    and very fast on sparse dicts.

Why cosine over Jaccard?
  - Jaccard treats all overlapping skills as equal weight.
  - Cosine + TF-IDF gives rare skills (e.g. "solidity", "terraform")
    higher weight than universal ones ("python"), producing better ranking.
"""

import math


# ── Cosine Similarity ─────────────────────────────────────────────────────────

def cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    """
    Compute cosine similarity between two sparse TF-IDF vectors.

    Formula:
        cos(θ) = (A · B) / (||A|| × ||B||)

    Because the vectorizer already L2-normalises its output, ||A|| = ||B|| = 1
    and this reduces to the plain dot product — making it very fast.

    Args:
        vec_a: Sparse TF-IDF dict {term: weight}
        vec_b: Sparse TF-IDF dict {term: weight}

    Returns:
        Float in [0.0, 1.0]. Returns 0.0 for empty or orthogonal vectors.
    """
    if not vec_a or not vec_b:
        return 0.0

    # Dot product — iterate the shorter vector for efficiency
    if len(vec_a) > len(vec_b):
        vec_a, vec_b = vec_b, vec_a

    dot_product = sum(
        weight * vec_b.get(term, 0.0)
        for term, weight in vec_a.items()
    )

    # If vectors are already L2-normalised, magnitudes = 1.0
    # We still compute them here so this function works on raw (unnormalised) input too.
    mag_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
    mag_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))

    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0

    return dot_product / (mag_a * mag_b)


def cosine_similarity_matrix(vectors: list[dict[str, float]]) -> list[list[float]]:
    """
    Compute pairwise cosine similarity for a list of vectors.

    Returns:
        N×N matrix where matrix[i][j] = cosine(vectors[i], vectors[j]).
    """
    n = len(vectors)
    matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        matrix[i][i] = 1.0   # self-similarity always 1
        for j in range(i + 1, n):
            score = cosine_similarity(vectors[i], vectors[j])
            matrix[i][j] = score
            matrix[j][i] = score   # symmetric
    return matrix


# ── Jaccard Similarity (bonus comparison) ────────────────────────────────────

def jaccard_similarity(skills_a: list[str], skills_b: list[str]) -> float:
    """
    Compute Jaccard similarity between two skill sets.

    Formula:
        J(A, B) = |A ∩ B| / |A ∪ B|

    No weighting — every skill counts equally regardless of rarity.
    This is why Jaccard is typically inferior to TF-IDF + cosine for
    nuanced recommendation tasks.

    Returns:
        Float in [0.0, 1.0].
    """
    set_a = set(s.lower().strip() for s in skills_a)
    set_b = set(s.lower().strip() for s in skills_b)

    if not set_a and not set_b:
        return 0.0

    intersection = len(set_a & set_b)
    union        = len(set_a | set_b)

    return intersection / union if union > 0 else 0.0


def compare_metrics(
    user_skills: list[str],
    role_skills: list[str],
    tfidf_score: float,
) -> dict:
    """
    Return a side-by-side comparison of cosine (TF-IDF) vs Jaccard scores.
    Used in the Flask UI's comparison view.
    """
    jaccard = jaccard_similarity(user_skills, role_skills)
    return {
        "tfidf_cosine": round(tfidf_score, 4),
        "jaccard":      round(jaccard, 4),
        "overlap":      sorted(set(s.lower() for s in user_skills)
                               & set(s.lower() for s in role_skills)),
        "note": (
            "TF-IDF cosine weights rare skills higher. "
            "Jaccard treats all skills equally."
        ),
    }


# ── Overlap utilities ─────────────────────────────────────────────────────────

def top_overlapping_skills(
    user_skills: list[str],
    role_skills: list[str],
    n: int = 2,
) -> list[str]:
    """
    Return the top-N overlapping skills between user and role,
    sorted by descending specificity (length of skill string as a simple proxy).

    Used to generate "Why it matches" explanations in the output.
    """
    user_set = set(s.lower().strip() for s in user_skills)
    role_set = set(s.lower().strip() for s in role_skills)
    overlap  = sorted(user_set & role_set, key=len, reverse=True)
    return overlap[:n]
