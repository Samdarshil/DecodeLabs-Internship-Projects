"""
src/ingestion.py
================
Step 1 of the IPO Pipeline: INGESTION
--------------------------------------
Responsibilities:
  - Load job-role dataset from CSV
  - Parse and normalise user skill inputs
  - Return clean data structures for downstream processing

No ML logic here — pure data loading and cleaning.
"""

import csv
import json
import os
import re
from typing import Optional

# ── Paths ─────────────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(_HERE, "..", "data")
RAW_SKILLS_CSV = os.path.join(DATA_DIR, "raw_skills.csv")
FALLBACK_JSON  = os.path.join(DATA_DIR, "fallback_trending.json")


def _normalise_skill(skill: str) -> str:
    """Lowercase, strip, collapse whitespace."""
    return re.sub(r"\s+", " ", skill.strip().lower())


def load_dataset(csv_path: str = RAW_SKILLS_CSV) -> list[dict]:
    """
    Load job roles from CSV.

    Returns:
        List of dicts: [{"role": str, "skills": [str, ...]}, ...]

    Raises:
        FileNotFoundError if the CSV does not exist.
        ValueError if the CSV has wrong columns or is empty.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found: {csv_path}")

    dataset: list[dict] = []

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None or not {"role", "skills"}.issubset(reader.fieldnames):
            raise ValueError("CSV must have 'role' and 'skills' columns.")

        for row in reader:
            role   = row["role"].strip()
            skills = [_normalise_skill(s) for s in row["skills"].split() if s.strip()]
            if role and skills:
                dataset.append({"role": role, "skills": skills})

    if not dataset:
        raise ValueError("Dataset is empty after parsing.")

    return dataset


def parse_user_input(raw_input) -> list[str]:
    """
    Accept user skills as a string, list, or comma-separated string.

    Examples:
        "Python, Cloud Computing, Automation"
        ["Python", "Cloud Computing"]
        "python cloud automation"

    Returns:
        Normalised list of skill strings.
    """
    if isinstance(raw_input, list):
        skills = [_normalise_skill(s) for s in raw_input if isinstance(s, str)]
    elif isinstance(raw_input, str):
        # Split on comma or space — handle both "a, b, c" and "a b c"
        if "," in raw_input:
            skills = [_normalise_skill(s) for s in raw_input.split(",")]
        else:
            skills = [_normalise_skill(raw_input)]
    else:
        raise TypeError(f"User input must be str or list, got {type(raw_input)}")

    return [s for s in skills if s]   # drop empties


def load_fallback(json_path: str = FALLBACK_JSON) -> dict:
    """Load the cold-start fallback configuration."""
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Fallback data not found: {json_path}")
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)
