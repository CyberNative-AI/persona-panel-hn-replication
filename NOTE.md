# Ten simulated readers or one plain question? Hacker News stories posted after a model's training cutoff

*An independent conceptual replication of arXiv:2609.25010. CyberNative AI LLC, November 2026. Status: our pipeline, with
vendor-hosted model inference; not independently reproduced.*

**In short.** A Claude model asked plainly about Hacker News stories posted after its stated training cutoff scored the
hit above its pair more often than when playing ten HN readers, in both samples (stage 1 retrospective,
stage 2 live); the stage-2 gap's interval reaches zero.

**Read this first**

1. **An easy contrast, not a headline A/B test.** Each pair sets a story that reached 50+ points against one with 3 or
   fewer posted within an hour of it, not two headlines for one story, as headline pre-testers compare. It
   shows only that our persona prompt, as written, did not help even here.
2. **Panel vs plain prompt: direction consistent, size uncertain.** Panel minus plain prompt: stage 1 −0.086 (95% CI −0.134
   to −0.038); stage 2 −0.046 (−0.091 to 0.000), not a second significant loss. This gap mixes the personas with the
   change of question (see the addendum); this item was headed "Persona cost" until November 2026.
3. **One model, one persona set, one venue.** The prompts also ask different questions (probability of reaching
   50 points vs each persona's wish to click and upvote); we did not separate role-play from question
   wording. The addendum below tests this with a matched-question control; the result is inconclusive.
4. **The 50–99-point band is not settled.** Chosen after stage 1; defined by points unknown at posting. In it the plain prompt scored 0.709 vs 0.649 for a non-LLM features baseline (stage 2,
   n=74); post hoc paired difference +0.061 (CI −0.081 to +0.203; stage 1 +0.040, CI −0.085 to +0.170, n=88).
5. **Retitles: exploratory, stage 2 only.** On the 56 pairs whose hit's title later changed, the plain prompt
   scored 0.83 on first-seen titles and 0.89 on current ones (51 pairs after tag removal: 0.83 vs 0.88); no CI.

## Why we ran it

Maiorano (arXiv:2609.25010; v1 27 July 2026, v2 3 November 2026) compares a ten-persona panel with a generic-reader LLM
baseline at ranking Upworthy headline variants. v1 reported Kendall τ 0.361 (baseline) vs 0.084 (panel), relabelled
Goodman–Kruskal γ (supplementary) in v2. v2's primary experiment (Gemini 3.1 Flash-Lite, GPT-4.1) reports
baseline-minus-panel τb gaps of +0.222 [+0.061, +0.385] and +0.257 [+0.119, +0.391], "not a held-out evaluation or
evidence of universal persona harm"; supplementary Reddit comparisons favour the panel. v2 states: "Training
contamination and generalization to current audiences or other formats are not excluded by the archive corpus."

We test both: another venue and model family (Claude Opus 5.5), on stories posted after its stated
training-data cutoff of June 2026 (https://support.claude.com/en/articles/8114494-how-up-to-date-is-claude-s-training-data).
Stage 1 was frozen after its data pull, before any model output. Stage 2 was frozen before its
stories were posted (2 of 482 items, both misses, were posted up to 36 minutes earlier).

## Method

- **Data.** Algolia HN Search API (omitted stories are absent). Stage 1: posted 1 Aug–21
  Oct 2026, titles as indexed 28 Oct, 250 seeded pairs. Stage 2: 10-minute polls 28 Oct–1 Nov (one 20-minute gap);
  paired items first seen a median 5.7 and at most 40 minutes after posting; titles as first seen; points read 4 Nov;
  241 pairs.
- **Pairs.** Hit: 50+ points. Miss: 3 or fewer, posted within 60 minutes of its hit, never at the same URL as any hit.
  "Launch HN" posts excluded; trailing tags ("(2019)", "[pdf]") removed.
- **Arms.** The model saw only title and site (shuffled batches of 100; file read/write tools only, no web or
  shell). *N:* the
  probability (0–100) of reaching 50 points; three runs averaged. *P:* ten HN-reader personas each rate 1–10 how likely
  they are to click and upvote; averaged. *F:* logistic regression on domain/title features, fitted on March–June 2026
  pairs.
- **Measure.** Pair accuracy: the share of pairs where the hit scores higher (ties 0.5). CIs: 10,000 pair-bootstrap
  resamples. Rules and forecasts were committed before any main-run output (a 20-item format pilot ran earlier).

## Results

| Pair accuracy [95% CI] | Stage 1 (n=250, titles as indexed) | Stage 2 (n=241, titles as first seen) |
|---|---|---|
| N plain prompt | 0.790 [0.740, 0.838] | 0.803 [0.753, 0.853] |
| P persona panel | 0.704 [0.648, 0.758] | 0.757 [0.703, 0.809] |
| F features baseline | 0.676 [0.616, 0.736] | 0.664 [0.602, 0.722] |
| N − F | +0.114 [+0.040, +0.188] | +0.139 [+0.064, +0.216] |
| P − N | −0.086 [−0.134, −0.038] | −0.046 [−0.091, 0.000] |

By 4 November, titles differed for 23% of stage-2 hits (21% after tag removal) and 2% of
misses. On current titles N moved +0.004 [−0.023, +0.029]. This bounds stage 2 only; stage-1 title changes
(titles 1–12 weeks old) were not measured.

Against the preprint: same direction; sizes not comparable (pair accuracy vs rank correlation). The panel still
scored above F in both stages (descriptive).

## Addendum, November 2026: matched-question control

Arm P changed two things: ten personas, and a different question (wish to click and upvote, 1–10, not N's probability
of 50 points, 0–100). After publication, Alexandre Cristovão Maiorano, the preprint's author, suggested separating them. Arm G asks P's question
verbatim of "a typical Hacker News reader", without persona or "Staying in character": ten runs per batch, averaged,
on P's batches, tools, limits and model. Prompt, job layout, scorer and reading rule were committed before any arm-G
output; all 100 jobs were valid.

| Pair accuracy [95% CI] | Stage 1 (n=250) | Stage 2 (n=241) |
|---|---|---|
| N plain prompt | 0.790 | 0.803 |
| P persona panel | 0.704 | 0.757 |
| G generic reader, P's question | 0.742 [0.688, 0.794] | 0.784 [0.732, 0.834] |
| G − P (primary) | +0.038 [−0.002, +0.078] | +0.027 [−0.006, +0.060] |
| N − G (secondary) | +0.048 [+0.012, +0.086] | +0.019 [−0.021, +0.056] |
| P − N (as published) | −0.086 [−0.134, −0.038] | −0.046 [−0.091, 0.000] |

**Reading: inconclusive.** G scored between P and N in both stages. On point estimates, about 44% (stage 1) and 59%
(stage 2) of the P − N gap lies between P and G, the rest between G and N: roughly half each, neither part
established. So P − N may mix a persona effect with a question-and-scale effect. Our frozen rule read a persona effect
only if G − P's stage-1 interval excluded zero (its lower end is −0.002). The other branch needed, in both stages,
G − P's interval to include zero and N − G's to exclude it; stage 2's N − G interval includes zero. Both missed narrowly,
in opposite places; a rule mirroring the persona branch would have read "question or scale". N − G is no clean
question test either: N asks a different question on a different scale, averages three runs, not ten, and ties
differently. Limits: one model, one generic-reader sentence (itself a light role), one venue. The headline above is
unchanged.

**Provenance.** All 245 model jobs (N, P, current-title N and G, both stages) ran `claude-opus-5-5` in Claude Code CLI
2.1.295, fast mode off, permission mode acceptEdits; every result event reports usage for that model only. The CLI
marks per-turn effort as active but does not report its level. We passed no effort flag, so it is the CLI's default
for that model, a value we do not know. `data/jobs.csv` lists every job; `data/batches.csv` gives each story's batch
and position. That layout follows from the public pair order and the shuffle seeds alone, so it reveals nothing about
which stories were used. Correction: stage 2 was shuffled with seed 174590, not 174570 as `code/PROMPTS.md` first
said.

| Protocol freeze (private workbench commit) | Commit | Time (UTC) |
|---|---|---|
| Stage 1 | 8bd2aa66 | 2026-10-28 18:53:12 |
| Stage 2 (also records stage-1 scoring) | 60630a8f | 2026-10-28 20:04:33 |
| Arm G | 18ddb328 | 2026-11-06 16:30:47 |
| Arm G amendment 1 (run plumbing only; prompt, layout, rule and limits unchanged) | e4716b27 | 2026-11-06 16:32:53 |

The first post-amendment arm-G launch began at 16:32:55 UTC on 6 November.

## Data and code

Released: per-story scores (every run and persona, arm G included) keyed by an opaque pair number and hit/miss role,
each story's batch and position, a record of every model job, features-model weights, personas, verbatim prompts, and a
scorer that rebuilds both tables, band and raw title-change figures. Capture timings and tag-removed title figures come
from unreleased evidence. The only HN-derived
fields are the hit's points band (50–99, 100+) and stage-2 title-change flags. HN item IDs, times, points, titles, URLs and
transcripts are not redistributed.

## Disclosure

AI agents at CyberNative AI LLC designed, ran, analysed and wrote this study; the company is accountable. One internal
independent review; no outside reproduction. Corrections: hello@cybernative.ai; we post them publicly, dated.
