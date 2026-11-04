import json, re, urllib.parse, pathlib
HIT, MISS = 50, 3          # points >= HIT is a hit; points <= MISS is a miss
WINDOW = 3600              # miss must be posted within +-60 min of its hit
def load(path):
    rows = []
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if not r.get("title"):
            continue
        if r["title"].lower().startswith("launch hn"):
            continue      # YC launches get boosted placement
        r["points"] = r.get("points") or 0
        r["domain"] = domain(r.get("url"))
        r["nurl"] = norm_url(r.get("url"))
        rows.append(r)
    rows.sort(key=lambda r: (r["created_at_i"], r["objectID"]))
    return rows
def domain(url):
    if not url:
        return ""
    h = urllib.parse.urlsplit(url).hostname or ""
    return h[4:] if h.startswith("www.") else h
def norm_url(url):
    if not url:
        return None
    u = urllib.parse.urlsplit(url)
    return (domain(url) + u.path.rstrip("/")).lower()
def make_pairs(rows, n, rng):
    """Seeded case-control pairs: hit + a random miss posted within +-WINDOW s.
    Misses that share a normalized URL with any hit are excluded (same story resubmitted)."""
    hit_urls = {r["nurl"] for r in rows if r["points"] >= HIT and r["nurl"]}
    hits = [r for r in rows if r["points"] >= HIT]
    misses = [r for r in rows if r["points"] <= MISS and r["nurl"] not in hit_urls]
    rng.shuffle(hits)
    used, pairs, skipped = set(), [], 0
    import bisect
    mt = [m["created_at_i"] for m in misses]
    for h in hits:
        if len(pairs) == n:
            break
        lo = bisect.bisect_left(mt, h["created_at_i"] - WINDOW)
        hi = bisect.bisect_right(mt, h["created_at_i"] + WINDOW)
        cand = [m for m in misses[lo:hi] if m["objectID"] not in used]
        if not cand:
            skipped += 1
            continue
        m = rng.choice(cand)
        used.add(m["objectID"]); used.add(h["objectID"])
        pairs.append((h, m))
    return pairs, skipped
TAG = re.compile(r"(\s*(\((19|20)\d\d\)|\[(pdf|video)\]))+\s*$", re.I)
def clean(title):
    """Strip trailing moderator tags ((2015), [pdf], [video]) that HN adds mostly to front-page stories
    after posting; they leak the outcome (pre-freeze critique, flaw 1)."""
    return TAG.sub("", title).strip()
def shown(r):
    """What an HN reader sees on /newest: title (tags stripped) and (domain)."""
    return {"title": clean(r["title"]), "site": r["domain"] or "(text post on news.ycombinator.com)"}
