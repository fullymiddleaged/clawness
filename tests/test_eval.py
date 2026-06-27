"""Retrieval-quality regression test — runs the labeled ground-truth set
through the lexical ranker and asserts MRR@5 / hit-rate stay above the floors.
Lexical (embedder=None) keeps it deterministic and dependency-free, matching
the CI `clawness eval` gate.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from clawness.core import Clawness  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GROUND_TRUTH = ROOT / "tests" / "ground_truth.json"
RULES_DIR = ROOT / "rules"

FLOOR_MRR = 0.85
FLOOR_HIT = 0.95
K = 5


def _measure() -> tuple[float, float, list[str]]:
    wl = Clawness(RULES_DIR, embedder=None, top_k=K)  # lexical = deterministic
    queries = json.loads(GROUND_TRUTH.read_text(encoding="utf-8"))["queries"]
    rr_sum, hits, misses = 0.0, 0, []
    for entry in queries:
        ids = wl.rank_ids(entry["q"], top_k=K)
        expect = set(entry["expect"])
        rank = next((i + 1 for i, rid in enumerate(ids) if rid in expect), None)
        if rank:
            rr_sum += 1.0 / rank
            hits += 1
        else:
            misses.append(entry["q"])
    n = len(queries)
    return rr_sum / n, hits / n, misses


def test_retrieval_quality_floors():
    mrr, hit_rate, misses = _measure()
    assert hit_rate >= FLOOR_HIT, f"hit-rate {hit_rate:.3f} < {FLOOR_HIT}; misses: {misses}"
    assert mrr >= FLOOR_MRR, f"MRR@{K} {mrr:.3f} < {FLOOR_MRR}"
