"""Recompute the NOTE.md table, the 50-99 band figures and the raw stage-2 title-change figures from the scores-only CSVs
(stdlib, no network; no HN IDs, times, points or titles). Capture timings and tag-removed title figures are not
reproducible from this release.

usage: python3 -I rescore.py [DATA_DIR=./data]
Mirrors the frozen scorers (src/score.py for stage 1, stage2/kit/s2_score.py for stage 2): pair accuracy with tie 0.5,
10,000 pair-bootstrap resamples, seed 17457 (band CI: separate stream, seed 174571). Prints JSON; exit 1 if a
value differs from the frozen result files when they are present alongside (../runs, ../stage2/s2).
"""
import csv, json, pathlib, random, statistics, sys

D = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent / "data"
def rows(name): return list(csv.DictReader(open(D / name, encoding="utf-8")))
pairs_all, scores_all = rows("pairs.csv"), rows("scores.csv")

def arm_scores(stage, col):
    return {r["item"]: float(r[col]) for r in scores_all if r["stage"] == stage and r[col] != ""}
def wins(pairs, s):
    return [None if p["hit_item"] not in s or p["miss_item"] not in s else
            (1.0 if s[p["hit_item"]] > s[p["miss_item"]] else 0.5 if s[p["hit_item"]] == s[p["miss_item"]] else 0.0)
            for p in pairs]
def acc(w): v = [x for x in w if x is not None]; return sum(v) / len(v) if v else None
def ci(x): x = sorted(v for v in x if v is not None); return [x[int(0.025 * len(x))], x[int(0.975 * len(x)) - 1]]

def score(stage, arms, diffs):
    pairs = [p for p in pairs_all if p["stage"] == stage]
    W = {a: wins(pairs, arm_scores(stage, col)) for a, col in arms.items()}
    def mdiff(a, b, idx):
        v = [W[a][i] - W[b][i] for i in idx if W[a][i] is not None and W[b][i] is not None]
        return sum(v) / len(v)
    n = len(pairs); rng = random.Random(17457); rng_band = random.Random(174571)
    band = [i for i, p in enumerate(pairs) if p["hit_band"] == "50-99"]
    boot = {k: [] for k in list(W) + list(diffs) + ["N_band5099"]}
    for _ in range(10000):
        idx = [rng.randrange(n) for _ in range(n)]
        for a in W: boot[a].append(acc([W[a][i] for i in idx]))
        for d, (a, b) in diffs.items(): boot[d].append(mdiff(a, b, idx))
        if stage == "s2": boot["N_band5099"].append(acc([W["N"][i] for i in (rng_band.choice(band) for _ in band)]))
    res = {"pairs": n}
    for a in W: res[a] = {"acc": acc(W[a]), "ci95": ci(boot[a])}
    for d, (a, b) in diffs.items(): res[d] = {"diff": mdiff(a, b, range(n)), "ci95": ci(boot[d])}
    res["N_band5099"] = {"n_pairs": len(band), "acc": acc([W["N"][i] for i in band]),
                         "F_acc": acc([W["F"][i] for i in band])}
    # Post hoc for the note (not in either frozen rule): paired N-F inside the 50-99 band, own stream, seed 174572.
    rb = random.Random(174572); bd = []
    for _ in range(10000):
        idx = [rb.choice(band) for _ in band]; bd.append(mdiff("N", "F", idx))
    res["N-F_band5099_posthoc"] = {"diff": mdiff("N", "F", band), "ci95": ci(bd)}
    if stage == "s2":
        res["N_band5099"]["ci95"] = ci(boot["N_band5099"])
        ret = [i for i, p in enumerate(pairs) if p["hit_retitled"] == "True"]
        res["hit_retitled_exploratory"] = {"n_pairs": len(ret), "N_first": acc([W["N"][i] for i in ret]),
                                           "N_cur": acc([W["Ncur"][i] for i in ret]), "ci95": "not computed"}
        res["retitle_share"] = {"hits": sum(p["hit_retitled"] == "True" for p in pairs) / n,
                                "misses": sum(p["miss_retitled"] == "True" for p in pairs) / n}
    return res

out = {"s1": score("s1", {"N": "N_mean", "P": "P_mean", "F": "F"}, {"N-F": ("N", "F"), "P-N": ("P", "N")}),
       "s2": score("s2", {"N": "N_mean", "P": "P_mean", "F": "F", "Ncur": "Ncur_mean"},
                   {"N-F": ("N", "F"), "P-N": ("P", "N"), "Ncur-N": ("Ncur", "N")})}
print(json.dumps(out, indent=1))

# Cross-check against the frozen result files when run inside the workbench.
ROOT = pathlib.Path(__file__).resolve().parent.parent
frozen = {"s1": ROOT / "runs/main-result.json", "s2": ROOT / "stage2/s2/result.json"}
bad = 0
for st, f in frozen.items():
    if not f.exists(): continue
    ref = json.loads(f.read_text())
    for k, v in out[st].items():
        if k not in ref or not isinstance(v, dict): continue
        for m in ("acc", "diff", "ci95", "F_acc", "n_pairs"):
            if m in v and m in ref[k] and json.dumps(v[m]) != json.dumps(ref[k][m]):
                bad += 1; print(f"MISMATCH {st} {k} {m}: {v[m]} vs frozen {ref[k][m]}", file=sys.stderr)
    print(f"{st}: compared with {f.name}", file=sys.stderr)
sys.exit(1 if bad else 0)
