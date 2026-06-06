"""
src/tfidf_vectorizer.py
========================
TF-IDF Vectorizer — implemented from scratch.

Why TF-IDF instead of binary vectors?
  Binary: "python" present → 1. Treats every skill equally regardless of rarity.
  TF-IDF: "python" present and rare across roles → higher weight.
          This lets uncommon skills (e.g. "solidity") carry more signal
          than universal ones (e.g. "python" which appears in 9/13 roles).

Formulae used:
  TF(t, d)  = count(t in d) / len(d)          raw term frequency
  IDF(t)    = log((1 + N) / (1 + df(t))) + 1  smoothed IDF (avoids zero division)
  TF-IDF    = TF * IDF
  L2-norm   = vector / ||vector||              normalise to unit length

No sklearn.feature_extraction.text is used here.
math.log and basic Python arithmetic only.
"""

import math
from collections import Counter
from typing import Optional


class TFIDFVectorizer:
    """
    Fit a TF-IDF model on a corpus, then transform any document into a vector.

    Usage:
        vectorizer = TFIDFVectorizer()
        vectorizer.fit(corpus)          # list[list[str]]
        vec = vectorizer.transform(doc) # list[str] → dict[str, float]
    """

    def __init__(self):
        self.vocabulary: list[str] = []        # sorted list of all unique terms
        self._vocab_index: dict[str, int] = {} # term → column index
        self._idf: dict[str, float] = {}       # term → IDF weight
        self._n_docs: int = 0
        self._fitted: bool = False

    # ── Fit ───────────────────────────────────────────────────────────────────

    def fit(self, corpus: list[list[str]]) -> "TFIDFVectorizer":
        """
        Build vocabulary and compute IDF weights from the corpus.

        Args:
            corpus: List of documents, each a list of term strings.
                    e.g. [["python", "sql", "spark"], ["javascript", "react"], ...]

        Returns:
            self (for chaining: vectorizer.fit(corpus).transform(doc))
        """
        if not corpus:
            raise ValueError("Cannot fit on an empty corpus.")

        self._n_docs = len(corpus)

        # ── Step 1: Build vocabulary ─────────────────────────────────────────
        all_terms: set[str] = set()
        for doc in corpus:
            all_terms.update(doc)

        self.vocabulary      = sorted(all_terms)
        self._vocab_index    = {term: i for i, term in enumerate(self.vocabulary)}

        # ── Step 2: Compute document frequency ───────────────────────────────
        # df[term] = number of documents that contain term at least once
        df: dict[str, int] = {term: 0 for term in self.vocabulary}
        for doc in corpus:
            unique_in_doc = set(doc)
            for term in unique_in_doc:
                if term in df:
                    df[term] += 1

        # ── Step 3: Compute IDF (smoothed to prevent zero-division) ──────────
        # Formula: log((1 + N) / (1 + df(t))) + 1
        # The +1 outside log keeps IDF ≥ 1 even for terms in every document.
        n = self._n_docs
        for term in self.vocabulary:
            self._idf[term] = math.log((1 + n) / (1 + df[term])) + 1.0

        self._fitted = True
        return self

    # ── Transform ─────────────────────────────────────────────────────────────

    def transform(self, document: list[str], normalise: bool = True) -> dict[str, float]:
        """
        Convert a document into a TF-IDF vector (sparse dict representation).

        Args:
            document:  List of terms (e.g. user skills or a job role's skill list).
            normalise: If True, L2-normalise the output vector.
                       Required for cosine similarity to work on raw dot product.

        Returns:
            dict mapping each vocabulary term to its TF-IDF weight.
            Terms not in vocabulary get weight 0 (omitted from dict for efficiency).
        """
        if not self._fitted:
            raise RuntimeError("Call .fit() before .transform().")

        if not document:
            # Return zero vector — caller should handle this as cold-start signal
            return {}

        # ── TF ────────────────────────────────────────────────────────────────
        term_count = Counter(document)
        doc_len    = len(document)

        tfidf: dict[str, float] = {}
        for term, count in term_count.items():
            if term not in self._vocab_index:
                # OOV term: skip (item cold-start: IDF = 0 for unseen terms)
                continue
            tf = count / doc_len
            tfidf[term] = tf * self._idf[term]

        if not tfidf:
            return {}   # all OOV — cold-start signal

        # ── L2 normalisation ─────────────────────────────────────────────────
        if normalise:
            magnitude = math.sqrt(sum(v ** 2 for v in tfidf.values()))
            if magnitude > 0:
                tfidf = {t: v / magnitude for t, v in tfidf.items()}

        return tfidf

    def fit_transform(self, corpus: list[list[str]]) -> list[dict[str, float]]:
        """Convenience: fit on corpus then transform each document."""
        self.fit(corpus)
        return [self.transform(doc) for doc in corpus]

    # ── Utilities ─────────────────────────────────────────────────────────────

    def get_idf(self) -> dict[str, float]:
        """Return IDF weights for every vocabulary term."""
        return dict(self._idf)

    def vocab_size(self) -> int:
        return len(self.vocabulary)

    def is_oov(self, term: str) -> bool:
        """Return True if the term was never seen during fit."""
        return term not in self._vocab_index

    def coverage(self, user_skills: list[str]) -> float:
        """
        Fraction of user skills that exist in the vocabulary.
        Used by cold-start handler to decide whether to fall back.
        """
        if not user_skills:
            return 0.0
        known = sum(1 for s in user_skills if not self.is_oov(s))
        return known / len(user_skills)
