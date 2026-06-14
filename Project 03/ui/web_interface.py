"""
ui/web_interface.py
====================
Flask web UI — visualises all 4 pipeline steps.

Run: python ui/web_interface.py
Then open: http://localhost:5000
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from flask import Flask, request, jsonify, render_template_string
except ImportError:
    print("Flask not installed. Run: pip install flask")
    sys.exit(1)

from src.recommender_pipeline import RecommenderPipeline
from src.ingestion import parse_user_input
from src.cold_start_handler import ColdStartHandler, MIN_SKILLS_REQUIRED, MIN_VOCAB_COVERAGE

# ── App setup ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
_pipeline = RecommenderPipeline(top_n=3)
_pipeline.load()

# ── HTML template ─────────────────────────────────────────────────────────────
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Tech Stack Recommender</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
           background: #0f1117; color: #e2e8f0; min-height: 100vh; }
    .container { max-width: 900px; margin: 0 auto; padding: 2rem 1.5rem; }
    h1 { font-size: 1.6rem; font-weight: 700; color: #fff; margin-bottom: .25rem; }
    .sub { color: #64748b; font-size: .875rem; margin-bottom: 2rem; }

    /* Input */
    .input-row { display: flex; gap: .75rem; flex-wrap: wrap; margin-bottom: 1rem; }
    input[type=text] {
      flex: 1; min-width: 260px; padding: .6rem 1rem;
      background: #1e2533; border: 1px solid #334155; border-radius: 8px;
      color: #e2e8f0; font-size: .9rem; outline: none;
    }
    input[type=text]:focus { border-color: #3b82f6; }
    button {
      padding: .6rem 1.4rem; background: #3b82f6; color: #fff;
      border: none; border-radius: 8px; font-size: .9rem; cursor: pointer;
      font-weight: 600; transition: background .15s;
    }
    button:hover { background: #2563eb; }
    .hint { font-size: .78rem; color: #475569; margin-bottom: 1.75rem; }

    /* Pipeline steps */
    .steps { display: grid; grid-template-columns: repeat(4, 1fr); gap: .75rem; margin-bottom: 2rem; }
    .step { background: #1e2533; border: 1px solid #1e3a5f; border-radius: 10px;
            padding: 1rem; text-align: center; transition: border-color .3s, opacity .3s; opacity: .45; }
    .step.active { border-color: #3b82f6; opacity: 1; }
    .step.done   { border-color: #22c55e; opacity: 1; }
    .step-num { font-size: 1.4rem; font-weight: 700; color: #3b82f6; }
    .step.done .step-num { color: #22c55e; }
    .step-label { font-size: .75rem; font-weight: 600; color: #94a3b8;
                  text-transform: uppercase; letter-spacing: .05em; margin-top: .3rem; }
    .step-desc { font-size: .72rem; color: #475569; margin-top: .3rem; }

    /* Cards */
    .results { display: flex; flex-direction: column; gap: .75rem; margin-bottom: 2rem; }
    .card { background: #1e2533; border: 1px solid #334155; border-radius: 12px; padding: 1.25rem 1.5rem; }
    .card-rank { font-size: .75rem; color: #64748b; font-weight: 600; text-transform: uppercase;
                  letter-spacing: .05em; margin-bottom: .3rem; }
    .card-role { font-size: 1.1rem; font-weight: 700; color: #fff; margin-bottom: .75rem; }
    .bar-row { display: flex; align-items: center; gap: .75rem; margin-bottom: .5rem; }
    .bar-track { flex: 1; height: 8px; background: #334155; border-radius: 4px; overflow: hidden; }
    .bar-fill { height: 100%; border-radius: 4px; background: #3b82f6;
                transition: width .8s cubic-bezier(.34,1.56,.64,1); }
    .bar-fill.cold { background: #f59e0b; }
    .bar-pct { font-size: .8rem; font-weight: 700; color: #3b82f6; min-width: 42px; text-align: right; }
    .bar-pct.cold { color: #f59e0b; }
    .match-label { font-size: .8rem; color: #64748b; }
    .match-tags  { display: inline-flex; gap: .4rem; flex-wrap: wrap; }
    .tag { padding: .2rem .6rem; background: #1e3a5f; color: #93c5fd;
           border-radius: 99px; font-size: .72rem; font-weight: 500; }
    .source-badge { display: inline-block; padding: .15rem .5rem; border-radius: 4px;
                     font-size: .68rem; font-weight: 600; margin-left: .5rem; }
    .source-pipeline  { background: #14532d; color: #86efac; }
    .source-cold      { background: #78350f; color: #fcd34d; }

    /* Cold start notice */
    .cold-notice { background: #1c1a0d; border: 1px solid #78350f; border-radius: 10px;
                    padding: .875rem 1.25rem; margin-bottom: 1.25rem; font-size: .82rem; color: #fcd34d; }

    /* Comparison table */
    .comparison { background: #1e2533; border: 1px solid #334155; border-radius: 12px;
                   padding: 1.25rem 1.5rem; margin-bottom: 2rem; }
    .comparison h3 { font-size: .9rem; font-weight: 700; margin-bottom: .85rem; color: #94a3b8; }
    table { width: 100%; border-collapse: collapse; font-size: .8rem; }
    th { text-align: left; color: #64748b; font-weight: 600;
          border-bottom: 1px solid #334155; padding: .4rem .5rem; }
    td { padding: .45rem .5rem; border-bottom: 1px solid #1e293b; }
    .positive { color: #4ade80; }
    .negative { color: #f87171; }

    /* Misc */
    .hidden { display: none !important; }
    .spinner { display: inline-block; width: 16px; height: 16px;
               border: 2px solid #334155; border-top-color: #3b82f6;
               border-radius: 50%; animation: spin .6s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }
    @media (max-width: 600px) { .steps { grid-template-columns: repeat(2, 1fr); } }
  </style>
</head>
<body>
<div class="container">
  <h1>🧬 Tech Stack Recommender</h1>
  <p class="sub">TF-IDF + Cosine Similarity · Content-Based Filtering · 4-Step IPO Pipeline</p>

  <div class="input-row">
    <input type="text" id="skills-input"
           placeholder="Enter 3+ skills, e.g. Python, Machine Learning, Docker"
           value="Python, Machine Learning, Docker" />
    <button onclick="runRecommender()">Recommend</button>
  </div>
  <p class="hint">Comma-separated. At least 3 skills for best results. Type any tech skills or interests.</p>

  <!-- 4-step pipeline visualisation -->
  <div class="steps" id="steps">
    <div class="step" id="step1"><div class="step-num">1</div><div class="step-label">Ingestion</div><div class="step-desc">Load dataset + parse user skills</div></div>
    <div class="step" id="step2"><div class="step-num">2</div><div class="step-label">Scoring</div><div class="step-desc">TF-IDF vectorise + cosine similarity</div></div>
    <div class="step" id="step3"><div class="step-num">3</div><div class="step-label">Sorting</div><div class="step-desc">Rank by score descending</div></div>
    <div class="step" id="step4"><div class="step-num">4</div><div class="step-label">Filtering</div><div class="step-desc">Return Top-N results</div></div>
  </div>

  <div id="cold-notice" class="cold-notice hidden"></div>
  <div id="results-section" class="results"></div>
  <div id="comparison-section" class="comparison hidden">
    <h3>TF-IDF Cosine vs Jaccard Similarity — Why TF-IDF wins</h3>
    <table id="compare-table">
      <thead><tr><th>Role</th><th>TF-IDF Cosine</th><th>Jaccard</th><th>Δ Difference</th><th>Shared Skills</th></tr></thead>
      <tbody></tbody>
    </table>
  </div>
</div>

<script>
async function runRecommender() {
  const raw = document.getElementById('skills-input').value.trim();
  if (!raw) { alert('Please enter at least one skill.'); return; }

  // Animate steps
  ['step1','step2','step3','step4'].forEach(id => {
    const el = document.getElementById(id);
    el.className = 'step';
  });

  document.getElementById('results-section').innerHTML =
    '<div style="color:#64748b;padding:1rem 0">  <span class="spinner"></span>  Analysing…</div>';
  document.getElementById('cold-notice').classList.add('hidden');
  document.getElementById('comparison-section').classList.add('hidden');

  // Simulate step animation
  const steps = ['step1','step2','step3','step4'];
  for (let i = 0; i < steps.length; i++) {
    document.getElementById(steps[i]).classList.add('active');
    await sleep(220);
  }

  try {
    const resp = await fetch('/api/recommend', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ skills: raw })
    });
    const data = await resp.json();

    // Mark all steps done
    steps.forEach(id => {
      const el = document.getElementById(id);
      el.classList.remove('active');
      el.classList.add('done');
    });

    renderResults(data);
  } catch (e) {
    document.getElementById('results-section').innerHTML =
      '<div style="color:#f87171;padding:1rem 0">Error: ' + e.message + '</div>';
  }
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function renderResults(data) {
  // Cold start notice
  const notice = document.getElementById('cold-notice');
  if (data.cold_start) {
    notice.textContent = '⚠  Cold start detected: ' + data.cold_start_reason +
      '. Showing trending fallback instead.';
    notice.classList.remove('hidden');
  }

  // Result cards
  const section = document.getElementById('results-section');
  section.innerHTML = data.results.map(r => {
    const pct = r.score ? (r.score * 100).toFixed(1) + '%' : r.score_pct;
    const width = r.score ? (r.score * 100).toFixed(1) : '40';
    const isCold = r.source !== 'pipeline';
    const fillClass = isCold ? 'bar-fill cold' : 'bar-fill';
    const pctClass  = isCold ? 'bar-pct cold' : 'bar-pct';
    const srcBadge  = isCold
      ? '<span class="source-badge source-cold">' + r.source.replace('_', ' ') + '</span>'
      : '<span class="source-badge source-pipeline">pipeline</span>';
    const tags = r.why_match.map(t => '<span class="tag">' + t + '</span>').join('');
    return \`
      <div class="card">
        <div class="card-rank">#\${r.rank} match \${srcBadge}</div>
        <div class="card-role">\${r.role}</div>
        <div class="bar-row">
          <div class="bar-track"><div class="\${fillClass}" style="width:\${width}%"></div></div>
          <div class="\${pctClass}">\${pct}</div>
        </div>
        <div class="match-label">Top matching skills: <span class="match-tags">\${tags}</span></div>
      </div>
    \`;
  }).join('');

  // Comparison table
  if (data.comparison && data.comparison.length) {
    const tbody = document.querySelector('#compare-table tbody');
    tbody.innerHTML = data.comparison.map(c => {
      const delta = (c.tfidf_cosine - c.jaccard) * 100;
      const dClass = delta >= 0 ? 'positive' : 'negative';
      const sign   = delta >= 0 ? '+' : '';
      return \`<tr>
        <td>\${c.role}</td>
        <td>\${(c.tfidf_cosine*100).toFixed(1)}%</td>
        <td>\${(c.jaccard*100).toFixed(1)}%</td>
        <td class="\${dClass}">\${sign}\${delta.toFixed(1)}%</td>
        <td>\${c.overlap.join(', ') || '—'}</td>
      </tr>\`;
    }).join('');
    document.getElementById('comparison-section').classList.remove('hidden');
  }
}

document.getElementById('skills-input').addEventListener('keydown', e => {
  if (e.key === 'Enter') runRecommender();
});
</script>
</body>
</html>
"""


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    body   = request.get_json(force=True, silent=True) or {}
    raw    = body.get("skills", "")
    top_n  = int(body.get("top_n", 3))

    user_skills = parse_user_input(raw)
    coverage    = _pipeline.vectorizer.coverage(user_skills)
    handler     = ColdStartHandler()
    is_cold     = handler.is_user_cold_start(user_skills, coverage)

    results = _pipeline.recommend(user_skills, interactive_cold_start=False)
    comparison = []
    if not is_cold and len(user_skills) >= 3:
        comparison = _pipeline.jaccard_comparison(user_skills, top_n=top_n)

    return jsonify({
        "results":           [r.to_dict() for r in results],
        "cold_start":        is_cold,
        "cold_start_reason": handler.cold_start_reason(user_skills, coverage) if is_cold else "",
        "vocab_coverage":    round(coverage, 3),
        "comparison":        comparison,
    })


@app.route("/api/matrix")
def api_matrix():
    roles, matrix = _pipeline.similarity_matrix()
    return jsonify({"roles": roles, "matrix": matrix})


@app.route("/api/health")
def api_health():
    return jsonify({
        "status":      "ok",
        "roles_loaded": len(_pipeline.dataset),
        "vocab_size":   _pipeline.vectorizer.vocab_size(),
    })


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  Tech Stack Recommender — Web UI")
    print(f"  Roles loaded : {len(_pipeline.dataset)}")
    print(f"  Vocabulary   : {_pipeline.vectorizer.vocab_size()} terms")
    print("\n  Open: http://localhost:5000\n")
    app.run(debug=True, port=5000)
