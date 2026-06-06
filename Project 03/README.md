# Tech Stack Recommender

**Content-based career path recommender using TF-IDF + Cosine Similarity.**

---

## About

Recommends the top-3 matching tech career paths based on your current skills.
Built as Project 3 of the DecodeLabs AI training kit — no external ML libraries
used. TF-IDF and cosine similarity are implemented from scratch.

---

## Tech Stack

- Python 3.9+ (standard library only for the core engine)
- Flask (web UI — optional)
- No scikit-learn, no pandas, no numpy in the core pipeline

---

## How It Works (IPO Pipeline)

```
Step 1 — Ingestion   Load dataset from CSV. Parse + normalise user skills.
Step 2 — Scoring     TF-IDF vectorise user skills + all job roles.
                     Compute cosine similarity for every role.
Step 3 — Sorting     Sort roles by similarity score descending.
Step 4 — Filtering   Return Top-N results (minimum 3) with explanations.
```

**Why TF-IDF over binary vectors?**
Binary treats every skill as equal. TF-IDF upweights rare skills
(e.g. `solidity`, `terraform`) that are highly specific to one career path,
producing sharper, more accurate rankings.

**Why cosine similarity over Euclidean distance?**
Euclidean penalises longer skill lists. Cosine measures only the angle
between vectors — purely directional — making it length-independent.

---

## Cold Start Handling

| Scenario | Trigger | Resolution |
|---|---|---|
| User cold start | < 3 skills provided | Trending fallback or onboarding survey |
| User cold start | < 30% vocabulary coverage | Same as above |
| Item cold start | New job role added | No issue — content filtering works immediately from metadata |

```
python run.py --skills "Python"          # triggers trending fallback
python run.py --interactive              # runs onboarding survey if cold start
```

---

## Project Structure

```
tech-stack-recommender/
├── data/
│   ├── raw_skills.csv              13 job roles, 30–70 skill tags each
│   └── fallback_trending.json      Cold-start fallback configuration
├── src/
│   ├── ingestion.py                Step 1 — load + parse
│   ├── tfidf_vectorizer.py         TF-IDF from scratch (no sklearn)
│   ├── cosine_similarity.py        Cosine + Jaccard from scratch
│   ├── recommender_pipeline.py     4-step pipeline
│   └── cold_start_handler.py       Cold-start detection + fallbacks
├── tests/
│   ├── test_tfidf.py               21 unit tests
│   ├── test_cosine.py              24 unit tests
│   └── test_pipeline.py            27 integration tests
├── ui/
│   ├── cli.py                      Terminal interface with step animation
│   └── web_interface.py            Flask UI (bonus)
├── output/
│   ├── sample_results.txt          Auto-generated on first run
│   └── similarity_matrix.csv       Role × role cosine matrix
├── run.py                          Single entry point
└── requirements.txt
```

---

## Setup

```bash
git clone https://github.com/yourusername/tech-stack-recommender.git
cd tech-stack-recommender
pip install -r requirements.txt
```

No model training required — the system builds the TF-IDF index at runtime.

---

## Run

```bash
# Interactive CLI
python run.py

# Direct input
python run.py --skills "Python, Machine Learning, Docker"

# Top 5 results + Jaccard comparison
python run.py --skills "Python, SQL, Spark" --top 5 --compare

# Export similarity matrix CSV
python run.py --skills "AWS, Terraform, Kubernetes" --export-matrix

# Flask web UI (http://localhost:5000)
python run.py --web

# All unit tests (72 tests, no pytest required)
python run.py --test
```

---

## Example Output

```
Input: "Python, Spark, Kafka, SQL, Airflow"

  #1  Data Engineer          Score: 51.7%   Matches: airflow, kafka
  #2  Full Stack Developer   Score: 12.9%   Matches: python, sql
  #3  Backend Developer      Score: 12.7%   Matches: python, sql

Input: "JavaScript, React, CSS, HTML"

  #1  Full Stack Developer   Score: 55.4%   Matches: javascript, react
  #2  Frontend Developer     Score: 49.2%   Matches: javascript, react
  #3  Mobile Developer       Score: 10.9%   Matches: react
```

---

## Future Improvements

- Collaborative filtering layer (user × user similarity for hybrid recommendations)
- SHAP-style contribution scores per skill
- Skill gap analysis: what to learn to reach a target role
- Live job posting integration (Indeed / LinkedIn API)
- Persistent user profiles with session history

---

## 👨‍💻 Author

**Darshil**  
BCA Student — Artificial Intelligence Internship Project  
*"Building tomorrow's tools with today's fundamentals."*
