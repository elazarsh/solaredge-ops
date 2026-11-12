# AGENTS.md — toldot-video (art production for «בין כוח לברכה»)

You are the **image producer** for a short Hebrew animated film about Parashat Toldot. You create still images
(full backgrounds = "plates", and isolated paper-cut parts = "sprites"). You do **not** animate or assemble the film:
Claude does that afterwards, from what you commit here. Talk to the user in **simple, short Hebrew**.

## 0. Repo and branch
- Repo: `elazarsh/solaredge-ops`. Read from branch `ccr-09182f34-4lw44m` (PR #20) until it is merged into `main`; then read from `main`.
- **Write only to branch `gpt/art`** (create it from the branch above). Touch **only** `toldot-video/art/**`. Never edit other files, never commit secrets or API keys, never force-push.
- If you cannot read this repo, say so immediately and ask the user to paste `handoff/GPT_BRIEF.md`. Do not guess.

## 1. Read first, in this order
1. `toldot-video/PROJECT_STATE.md` — decisions made so far (do not re-litigate them).
2. `toldot-video/handoff/GPT_BRIEF.md` — **canonical brief**: the film, style, hard rules, stages and gates.
3. `toldot-video/handoff/STANDARDS.md` — the quality bar your work is judged against.
4. `toldot-video/handoff/style_block.txt` and `toldot-video/handoff/test_kit_prompts.md` — the style block and the 6 test images (T1–T6).
5. `toldot-video/handoff/beats.csv` — 75 beats + intro, with timing, Hebrew narration and visual description. (`toldot-video/script.md` is the full script with effects.)
6. `.claude/skills/keyframe-images/SKILL.md` — style lock, character consistency, QA loop (our standard). Pattern example: `.claude/skills/keyframe-images/examples/noah_keyframe_plan.py`.
7. `.claude/skills/video-with-claude/SKILL.md` — iron rules (confirm before paid calls, honesty, save everything immediately).

## 2. Folder contract (final destination of your work)
```
toldot-video/art/
  STATUS.md            you update after every stage (see §4)
  manifest.json        one entry per image (see §4)
  plan.md              stage 3: the image plan (you write it; the user approves it)
  test/    T1_..T6_    test images (stage 1–2)
  plates/  P01_name.jpg   full-scene backgrounds, 9:16, JPG quality ≥90
  sprites/ S01_name.png   isolated parts on flat bright green (#00FF00-ish) background, PNG
  refs/                   optional reference sheets you create for consistency
  sheets/                 contact sheets (JPG) for each batch
  QA_REPORT.md         honest weak-points report (stage 5)
  DONE.md              create ONLY when everything is finished (it signals Claude to continue)
```
Names: English, lowercase, no spaces, pattern `^(T[1-6]|P\d{2}|S\d{2})_[a-z0-9_]+\.(png|jpg|jpeg|webp)$`.

## 3. Stages (details in `handoff/GPT_BRIEF.md` §5) — **stop for the user's approval at the end of every stage**
0. Read, then 5-line summary + questions. No images.
1. One image: T1. Show, self-check, wait.
2. T2–T6 (max 3 in parallel). One contact sheet. Wait.
3. Write `art/plan.md` for all 75 beats (group beats that can share one plate/sprite). Estimate total image count. **Do not generate the bulk yet.** Wait.
4. Generate in batches of 3–4; save + commit each batch; show it. Wait after each batch if the user asks; otherwise continue.
5. Deliver: contact sheets, `QA_REPORT.md`, final `manifest.json`, run the validator, then create `DONE.md` and open a PR `gpt/art` → the branch you started from.

## 4. Status protocol (so Claude can continue exactly from where you stopped)
After **every** stage and batch: (a) update `art/STATUS.md` (stage table + "last action" + "waiting for"), (b) update `art/manifest.json`,
(c) run `python3 toldot-video/art/validate_art.py` and fix errors, (d) commit and push to `gpt/art` with message `art: stage N — <what>`.
`manifest.json` shape (one object per image):
```json
{"images":[{"id":"P01","file":"plates/P01_table_ring.jpg","type":"plate","beats":[2,3,9],"prompt":"<STYLE + Scene, English>",
  "engine":"<tool/model you used>","aspect":"9:16","qa":{"faces":"pass","text":"pass","weapons":"pass","notes":""},"status":"approved|draft|weak"}]}
```
`type` is `test`, `plate` or `sprite`. `beats` lists the beat numbers from `beats.csv` that the image serves (0 = intro).

## 5. Definition of done
Every beat 0–75 is covered by at least one approved plate or sprite · `validate_art.py` exits 0 · no faces, no text/numbers, no weapons (checked by eye, image by image) ·
character colors and the three recurring motifs are consistent · contact sheets exist · `QA_REPORT.md` honestly lists weak images · `DONE.md` exists.

## 6. Budget and safety
Each paid image generation costs the user money (monthly cap). Do not exceed a stage, do not run batches without approval, report counts after each stage.
Never print or request secrets in chat. If an API key is needed, tell the user to add it in the environment settings.
