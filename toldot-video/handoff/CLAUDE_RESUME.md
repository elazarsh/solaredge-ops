# For Claude: how to continue when the user says "GPT סיים" (GPT finished)

1. `git fetch origin gpt/art` (and read the PR). **Do not merge anything into `main` unless the user asks.**
2. Bring the art into the working branch: `git checkout origin/gpt/art -- toldot-video/art` (commit on the dev branch).
3. Read `art/STATUS.md`, `art/QA_REPORT.md`, `art/manifest.json`. Run `python3 toldot-video/art/validate_art.py --strict-coverage`.
4. Review with your own eyes (Read tool): every contact sheet, then every sprite/plate flagged `weak` and a sample of the rest. Check **faces, text, weapons, 9:16, motif consistency**. Do not trust the manifest's QA claims blindly.
5. Report to the user in simple Hebrew: what is ready, what is weak, what must be redone (and how many images that is = cost).
6. Then continue with the pipeline in `PROJECT_STATE.md` (keying, composition, intro/outro, typography, music, render, QA).
