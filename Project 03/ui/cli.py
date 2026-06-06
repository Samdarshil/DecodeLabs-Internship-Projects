"""
ui/cli.py
==========
Command-line interface for the Tech Stack Recommender.

Usage:
    python ui/cli.py
    python ui/cli.py --skills "Python, Machine Learning, Docker"
    python ui/cli.py --skills "Python, ML, Docker" --top 5 --compare
    python ui/cli.py --export-matrix
"""

import sys
import os
import argparse
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.recommender_pipeline import RecommenderPipeline
from src.ingestion import parse_user_input


# ── ANSI colour helpers (degrade gracefully on Windows CMD) ───────────────────
def _supports_colour() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

C = {
    "reset":   "\033[0m"  if _supports_colour() else "",
    "bold":    "\033[1m"  if _supports_colour() else "",
    "cyan":    "\033[96m" if _supports_colour() else "",
    "green":   "\033[92m" if _supports_colour() else "",
    "yellow":  "\033[93m" if _supports_colour() else "",
    "red":     "\033[91m" if _supports_colour() else "",
    "dim":     "\033[2m"  if _supports_colour() else "",
}


def clr(text: str, *codes: str) -> str:
    if not codes:
        return text
    prefix = "".join(C.get(c, "") for c in codes)
    return f"{prefix}{text}{C['reset']}"


# ── Display helpers ───────────────────────────────────────────────────────────

def print_header():
    print()
    print(clr("  ╔══════════════════════════════════════════════╗", "cyan"))
    print(clr("  ║   Tech Stack Recommender  ·  TF-IDF Engine  ║", "cyan", "bold"))
    print(clr("  ╚══════════════════════════════════════════════╝", "cyan"))
    print()


def print_step(step_num: int, title: str):
    print(clr(f"\n  ── Step {step_num}: {title} ", "yellow", "bold") + clr("─" * (44 - len(title)), "dim"))


def print_results(results, user_skills: list[str]):
    print(clr("\n  ╔══════════════════════════════════════════════╗", "green"))
    print(clr("  ║           Top Career Path Matches            ║", "green", "bold"))
    print(clr("  ╚══════════════════════════════════════════════╝", "green"))

    for r in results:
        bar_len = int(r.score * 30) if r.score else 8
        bar     = "█" * bar_len + "░" * (30 - bar_len)
        src_tag = f"  [{r.source}]" if r.source != "pipeline" else ""

        print()
        print(clr(f"  #{r.rank}  {r.role}", "bold"))
        print(f"       Score  : {clr(r.score_pct, 'green')}  {clr(bar, 'green')}{src_tag}")
        print(f"       Match  : {', '.join(r.why_match)}")

    print()
    print(clr("  ─" * 24, "dim"))


def print_comparison(comparisons):
    print(clr("\n  ── TF-IDF cosine  vs  Jaccard (bonus) " + "─" * 10, "yellow"))
    print(f"  {'Role':<35} {'TF-IDF':>10}  {'Jaccard':>10}  Δ")
    print("  " + "─" * 65)
    for c in comparisons:
        delta = c["tfidf_cosine"] - c["jaccard"]
        sign  = "+" if delta >= 0 else ""
        print(
            f"  {c['role']:<35} "
            f"{c['tfidf_cosine']*100:>8.1f}%  "
            f"{c['jaccard']*100:>8.1f}%  "
            f"{sign}{delta*100:.1f}%"
        )
    print()
    print(clr("  Positive Δ = TF-IDF ranks higher than Jaccard for this role.", "dim"))
    print(clr("  TF-IDF upweights rare/specific skills; Jaccard treats all equally.", "dim"))


# ── Main CLI ──────────────────────────────────────────────────────────────────

def get_user_skills_interactive() -> list[str]:
    """Prompt the user for skills interactively."""
    print(clr("  Enter at least 3 skills or interests (comma-separated):", "cyan"))
    print(clr("  Example: Python, Cloud Computing, Automation\n", "dim"))
    raw = input("  Your skills: ").strip()
    return parse_user_input(raw)


def run_cli(args):
    print_header()

    # ── Step 1: Ingestion ─────────────────────────────────────────────────────
    print_step(1, "Ingestion — loading dataset")
    pipeline = RecommenderPipeline(top_n=args.top)

    t0 = time.perf_counter()
    pipeline.load()
    load_ms = (time.perf_counter() - t0) * 1000

    print(f"  ✓  {len(pipeline.dataset)} job roles loaded")
    print(f"  ✓  Vocabulary: {pipeline.vectorizer.vocab_size()} unique terms")
    print(f"  ✓  TF-IDF fitted  ({load_ms:.0f} ms)")

    # ── Collect user input ────────────────────────────────────────────────────
    if args.skills:
        user_skills = parse_user_input(args.skills)
    else:
        user_skills = get_user_skills_interactive()

    print(f"\n  Input skills: {clr(', '.join(user_skills), 'cyan')}")
    coverage = pipeline.vectorizer.coverage(user_skills)
    print(f"  Vocabulary coverage: {coverage:.0%}")

    # ── Step 2: Scoring ───────────────────────────────────────────────────────
    print_step(2, "Scoring — TF-IDF + cosine similarity")
    print("  Computing cosine similarity against all roles...")

    # ── Step 3 & 4: Sort + Filter ─────────────────────────────────────────────
    print_step(3, "Sorting — ranking by score")
    print_step(4, "Filtering — selecting Top-{}".format(args.top))

    t1 = time.perf_counter()
    results = pipeline.recommend(
        user_skills,
        interactive_cold_start=args.interactive,
    )
    infer_ms = (time.perf_counter() - t1) * 1000
    print(f"  ✓  Completed in {infer_ms:.1f} ms")

    # ── Output ────────────────────────────────────────────────────────────────
    print_results(results, user_skills)

    # ── Jaccard comparison ────────────────────────────────────────────────────
    if args.compare and len(user_skills) >= 3:
        comparisons = pipeline.jaccard_comparison(user_skills, top_n=args.top)
        print_comparison(comparisons)

    # ── Export similarity matrix ──────────────────────────────────────────────
    if args.export_matrix:
        out_path = os.path.join(
            os.path.dirname(__file__), "..", "output", "similarity_matrix.csv"
        )
        pipeline.export_similarity_matrix_csv(out_path)
        print(clr(f"  ✓  Similarity matrix exported → {out_path}", "green"))

    # ── Save sample output ────────────────────────────────────────────────────
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)
    sample_path = os.path.join(output_dir, "sample_results.txt")
    with open(sample_path, "w", encoding="utf-8") as f:
        f.write(f"Input skills: {', '.join(user_skills)}\n\n")
        for r in results:
            f.write(f"#{r.rank}  {r.role}\n")
            f.write(f"    Score     : {r.score_pct}\n")
            f.write(f"    Why match : {', '.join(r.why_match)}\n")
            f.write(f"    Source    : {r.source}\n\n")

    print(clr(f"  Results saved → output/sample_results.txt", "dim"))


def main():
    parser = argparse.ArgumentParser(
        description="Tech Stack Recommender — TF-IDF + Cosine Similarity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ui/cli.py
  python ui/cli.py --skills "Python, SQL, Spark, Kafka"
  python ui/cli.py --skills "JavaScript, React, Node" --top 5
  python ui/cli.py --skills "Python, ML, Docker" --compare
  python ui/cli.py --export-matrix
        """,
    )
    parser.add_argument("--skills",        type=str,  default="",    help="Comma-separated skills")
    parser.add_argument("--top",           type=int,  default=3,     help="Number of results (min 3)")
    parser.add_argument("--compare",       action="store_true",       help="Show TF-IDF vs Jaccard")
    parser.add_argument("--interactive",   action="store_true",       help="Run onboarding survey on cold start")
    parser.add_argument("--export-matrix", action="store_true",       help="Export similarity matrix CSV")
    args = parser.parse_args()

    try:
        run_cli(args)
    except KeyboardInterrupt:
        print("\n  Interrupted.")
        sys.exit(0)
    except Exception as e:
        print(clr(f"\n  Error: {e}", "red"))
        sys.exit(1)


if __name__ == "__main__":
    main()
