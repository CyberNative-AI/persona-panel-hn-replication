# Ten simulated readers or one plain question? Persona panel vs plain prompt on post-cutoff Hacker News stories

This repository holds the scores, prompts, personas and scorer for the note "Ten simulated readers or one plain question?
Hacker News stories posted after a model's training cutoff"
(https://cybernative.ai/labs/persona-panel-hn-replication/). The note is an independent conceptual replication of
arXiv:2609.25010. `NOTE.md` is the note text.

The study pairs a Hacker News story that reached 50 or more points with one that got 3 or fewer and was posted within an
hour of it. It then asks whether a model scores the hit above its pair more often when asked plainly (arm N) or when
playing ten Hacker News readers (arm P). A non-LLM features baseline (arm F) is the third arm. It is an easy contrast,
not a test of two headlines for one story. Read the note's "Read this first" list before using any number.

## Run

```sh
python3 -I rescore.py            # reads ./data; Python 3.12, standard library only, no network
```

`rescore.py` prints JSON with the note's results table (pair accuracy and 95% pair-bootstrap intervals for N, P and F,
and the N − F and P − N differences, for both stages), the 50–99-point band figures, and the raw stage-2 title-change
figures. The bootstrap seeds are fixed, so a rerun prints the same numbers.

It does not rebuild capture timings, the tag-removed title figures or the item order. Those come from evidence we do not
release.

## Files

- `NOTE.md`: the note.
- `rescore.py`: the scorer described above.
- `data/pairs.csv`: one row per pair: stage (`s1`, `s2`), pair number, the hit and miss item keys, the hit's points band
  (`50-99`, `100+`) and, for stage 2, whether the hit's or miss's title had changed by 4 November 2026.
- `data/scores.csv`: one row per item: the F score; the three N runs and their mean; the ten persona ratings and their
  mean; and, for stage 2, three N runs on current titles (`Ncur`) and their mean. Item keys are our own
  (`s1-0-hit`, `s1-0-miss`, ...).
- `data/personas.json`: the ten persona strings used in arm P.
- `data/armF-model.json`: the fitted weights of the features baseline.
- `code/PROMPTS.md`: the verbatim prompts, seeds and job layout of both model arms.
- `code/common.py`, `code/features.py`: how pairs were built and how arm F was fitted. They read Hacker News records
  that this repository does not contain, so they document the method; they do not run from this repository alone.

## What is not here

Hacker News item IDs, posting times, point counts, titles, URLs, sites, usernames and model transcripts are not
redistributed. The only fields derived from Hacker News are the hit/miss role, the hit's points band and the stage-2
title-change flags.

## Limits

- One model (Claude Opus 5.5, vendor-hosted inference), one set of ten personas, one venue.
- The two model arms ask different questions (probability of reaching 50 points vs each persona's wish to click and
  upvote). We did not separate role-play from question wording.
- Our own pipeline ran the study. It has had one internal independent review and no outside reproduction.

## Licence

- Code (`rescore.py`, `code/common.py`, `code/features.py`): MIT License.
- Our scores, personas, prompts and note text (`NOTE.md`, `code/PROMPTS.md`, `data/*`): Creative Commons Attribution 4.0
  International (CC BY 4.0).
- The hit/miss roles, points bands and title-change flags are derived from Hacker News. We grant no rights in them
  beyond our own contribution.

See `LICENSE`. Copyright 2026 CyberNative AI LLC.

## Contact

Prepared by CyberNative AI LLC, an AI-run company, using AI agents. Report errors to hello@cybernative.ai. We publish
dated public corrections.
