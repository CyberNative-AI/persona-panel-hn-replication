# Prompts and job layout (verbatim from the frozen runner)

The frozen runner script is not published because it calls our internal container tooling; its prompts, seeds and
job layout are reproduced here exactly. `{n}` is the batch size (100); `{persona}` is one string from `../data/personas.json`.

## Arm N (no persona), 3 independent runs per batch, scores averaged

```text
Read /work/items.json. It lists {n} submissions to Hacker News; each has an id, its title, and the site shown next to the title on the /newest page. For each submission, estimate the probability (0-100) that it went on to receive 50 or more points. Use only your own judgment: do not look anything up. Write /work/scores.json: one JSON object mapping every id (string) to an integer from 0 to 100. Include all {n} ids. Write nothing else.
```

## Arm P (10 personas), one run per persona per batch, scores averaged over personas

```text
You are {persona}. Read /work/items.json. It lists {n} submissions you see on the Hacker News /newest page; each has an id, its title, and the site shown next to the title. Staying in character, rate from 1 to 10 how likely you personally would be to click the submission and upvote it. Use only your own judgment: do not look anything up. Write /work/scores.json: one JSON object mapping every id (string) to an integer from 1 to 10. Include all {n} ids. Write nothing else.
```

## Layout

- Items: stage 1 = 500 items, stage 2 = 482 items, shuffled once with seed 174570 before any run and cut into batches
  of 100 in that order. The item order and batch assignment are not part of this release (they would identify HN
  items), so the job layout cannot be rebuilt from the released files; the scores are released per run and persona.
- Each job got one batch as `/work/items.json`: a JSON list of `{"id", "title", "site"}`, reshuffled per job with
  `random.Random(f"{tag}/{job}").shuffle(order)` where tag is `main` (stage 1), `s2` (stage 2 first-seen titles)
  or `s2cur` (stage 2 current titles) and job is e.g. `N-r1-b3` or `P-p7-b3`.
- Each job was one non-interactive model session with only file Read and Write tools (no shell, no web search);
  inference ran on the vendor's hosted service, 900 s timeout. Output had to be a JSON object with every id mapped to an integer in range;
  up to 3 attempts per job, otherwise missing. All 65 (stage 1) and 80 (stage 2) jobs were valid; none missing.
- Title and site are built by `common.py` `shown()`: trailing "(2019)", "[pdf]", "[video]" tags removed; site = URL host
  without "www.", or "(text post on news.ycombinator.com)".
- Arm F: `features.py` (fit on 1,500 pre-period pairs, 2026-03-01..06-15, seed 17458); weights in `../data/armF-model.json`.
  Refitting it needs the pre-period Algolia pull, which we do not redistribute.
