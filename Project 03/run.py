"""
run.py — Entry point for the Tech Stack Recommender.

Quick start:
    python run.py                              # interactive CLI
    python run.py --skills "Python, SQL, Spark"
    python run.py --skills "Python, ML, Docker" --compare --export-matrix
    python run.py --web                        # launch Flask UI on port 5000
    python run.py --test                       # run all unit tests
"""

import sys
import os
import argparse

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_tests():
    """Run all unit tests without pytest dependency."""
    print("\n  Running test suite...\n")
    modules = [
        ("tests.test_tfidf",   "TF-IDF Vectorizer"),
        ("tests.test_cosine",  "Cosine & Jaccard Similarity"),
        ("tests.test_pipeline","Full Pipeline"),
    ]
    total_passed = total_failed = 0

    for mod_name, label in modules:
        print(f"  ─── {label} {'─' * (40 - len(label))}")
        import importlib
        mod = importlib.import_module(mod_name)

        test_classes = [
            getattr(mod, name)
            for name in dir(mod)
            if name.startswith("Test")
        ]

        for cls in test_classes:
            obj = cls()
            for method_name in sorted(m for m in dir(cls) if m.startswith("test_")):
                try:
                    getattr(obj, method_name)()
                    print(f"  ✅  {cls.__name__}.{method_name}")
                    total_passed += 1
                except Exception as e:
                    print(f"  ❌  {cls.__name__}.{method_name}  →  {e}")
                    total_failed += 1
        print()

    status = "✅ All passed" if total_failed == 0 else f"❌ {total_failed} failed"
    print(f"  {status}  |  {total_passed} passed  {total_failed} failed\n")
    sys.exit(0 if total_failed == 0 else 1)


def run_web():
    """Launch the Flask web interface."""
    from ui.web_interface import app, _pipeline
    print(f"\n  Tech Stack Recommender — Web UI")
    print(f"  Roles loaded : {len(_pipeline.dataset)}")
    print(f"  Open: http://localhost:5000\n")
    app.run(debug=False, port=5000)


def run_cli(args):
    """Pass through to cli.py."""
    from ui.cli import run_cli as _run, get_user_skills_interactive
    run_cli(args)


def main():
    parser = argparse.ArgumentParser(
        description="Tech Stack Recommender — TF-IDF + Cosine Similarity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py
  python run.py --skills "Python, SQL, Spark, Kafka"
  python run.py --skills "JavaScript, React, Node" --top 5 --compare
  python run.py --web
  python run.py --test
        """,
    )
    parser.add_argument("--skills",        type=str,  default="")
    parser.add_argument("--top",           type=int,  default=3)
    parser.add_argument("--compare",       action="store_true")
    parser.add_argument("--interactive",   action="store_true")
    parser.add_argument("--export-matrix", action="store_true")
    parser.add_argument("--web",           action="store_true", help="Launch Flask UI")
    parser.add_argument("--test",          action="store_true", help="Run all unit tests")
    args = parser.parse_args()

    if args.test:
        run_tests()
    elif args.web:
        run_web()
    else:
        from ui.cli import run_cli as cli_run
        cli_run(args)


if __name__ == "__main__":
    main()
