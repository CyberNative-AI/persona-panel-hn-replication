"""Arm F: frozen non-LLM baseline. Logistic regression (L2, standardized) fit on 1,500 pre-cutoff
hit/miss pairs built exactly like the test pairs (2026-03-01..2026-06-15, seed 17458).
Domain stats come from all pre-period stories; training items use leave-one-out domain stats."""
import json, math, random, re, sys, pathlib, collections
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import load, make_pairs, HIT, clean
pre = load("data/pre-window.jsonl")
dn = collections.Counter(r["domain"] for r in pre)
dh = collections.Counter(r["domain"] for r in pre if r["points"] >= HIT)
def feats(r, loo=False):
    d = r["domain"]; n = dn[d]; h = dh[d]
    if loo:
        n -= 1; h -= 1 if r["points"] >= HIT else 0
    t = clean(r["title"])
    return [math.log((h + 0.5) / (n + 10)) if d else math.log(0.5 / 10),  # smoothed domain hit rate
            math.log1p(max(n, 0)),
            1.0 if t.lower().startswith("show hn") else 0.0,
            1.0 if not d else 0.0,
            len(t) / 80, len(t.split()) / 12,
            1.0 if re.search(r"\d", t) else 0.0,
            1.0 if "?" in t else 0.0,
            1.0 if d == "github.com" else 0.0,
            1.0 if d in ("youtube.com", "youtu.be") else 0.0,
            sum(c.isupper() for c in t) / max(len(t), 1)]
pairs, _ = make_pairs(pre, 1500, random.Random(17458))
X, y = [], []
for h, m in pairs:
    X += [feats(h, True), feats(m, True)]; y += [1, 0]
k = len(X[0])
mu = [sum(x[j] for x in X) / len(X) for j in range(k)]
sd = [max(1e-9, math.sqrt(sum((x[j] - mu[j]) ** 2 for x in X) / len(X))) for j in range(k)]
Z = [[(x[j] - mu[j]) / sd[j] for j in range(k)] for x in X]
w = [0.0] * (k + 1)
for it in range(3000):                      # gradient descent, L2 1e-3, fixed steps (deterministic)
    g = [0.0] * (k + 1)
    for z, t in zip(Z, y):
        p = 1 / (1 + math.exp(-(w[0] + sum(a * b for a, b in zip(w[1:], z)))))
        g[0] += p - t
        for j in range(k):
            g[j + 1] += (p - t) * z[j]
    for j in range(k + 1):
        w[j] -= 0.5 * (g[j] / len(Z) + (1e-3 * w[j] if j else 0))
test = {r["objectID"]: r for r in load("data/test-window.jsonl")}
items = json.loads(pathlib.Path("data/test-items.json").read_text(encoding="utf-8"))
out = {}
for it in items:
    z = [(a - mu[j]) / sd[j] for j, a in enumerate(feats(test[it["id"]]))]
    out[it["id"]] = w[0] + sum(a * b for a, b in zip(w[1:], z))
pathlib.Path("runs/armF-scores.json").write_text(json.dumps(out, indent=1, sort_keys=True), encoding="utf-8")
train_acc = sum((w[0] + sum(a*b for a, b in zip(w[1:], Z[2*i]))) > (w[0] + sum(a*b for a, b in zip(w[1:], Z[2*i+1]))) for i in range(len(pairs))) / len(pairs)
pathlib.Path("runs/armF-model.json").write_text(json.dumps({"weights": w, "mu": mu, "sd": sd, "train_pairs": len(pairs), "train_pair_acc": train_acc}, indent=1), encoding="utf-8")
print("armF fit on", len(pairs), "pre pairs; train pair acc", round(train_acc, 3))
