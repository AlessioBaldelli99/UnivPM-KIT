# Plan: CAMEL [[257,121,10]] from `QD-LDPC-Alessio/PCMs` → `.npz` → submission-ready branch (stop before push)

## Context

The user wants to submit CSS qLDPC codes from the collaborators' repo `QD-LDPC-Alessio` (public GitHub
`AlessioBaldelli99/UnivPM-KIT`, HEAD `886501f` = origin/main) to the qldpc-challenge leaderboard. The codes are
from the ISIT 2026 work *"Quantum CSS LDPC Codes based on Dyadic Matrices for Belief Propagation-based Decoding"*
(A. Baldelli, M. Battaglioni, J. Mandelbaum, S. Miao, L. Schmalen). CAMEL builds binary dyadic H1, H2 with
H1·H2ᵀ = J (all-ones) and appends an all-one column so the pair commutes. Matrices are dense 0/1 CSVs (rows =
checks). `qldpc submit` reads only `.npz` (`hx`/`hz`) or a submission JSON, so conversion is needed ("`.npm`" read
as `.npz`).

## Exploration results (read-only analysis already done)

| Code | Valid CSS | k | w | d evidence | Board (`research/does_it_advance.py`) | Decision |
|---|---|---|---|---|---|---|
| **CAMEL [[257,121]]** (all-one col) | yes, connected | 121 | **17** | all 3205/3186 weight-10 words in the group's `.CW` lists are nontrivial logicals; none listed < 10 | **board-advancing** in `weight-9plus × unrestricted` for d ≥ 9 (beats `[[281,121,4]]` w21 on n,d,w; no d-only gain). d = 8 → dominated by QD `[[256,130,8]]`, `[[256,150,8]]` w16 | **package** |
| QD [[64,18,8]] | yes | 18 | 8 | weight-8 logicals | ties `codes/64-18-8.json` (held back earlier as possibly WL-equivalent) | not packaged (user) |
| CAMEL [[65,27,4]] | yes | 27 | 9 | weight-4 logicals | dominated by `[[64,34,4]]` w8 | not packaged |
| QD [[128,36,8]] | disconnected | 36 | 8 | — | direct sum of two [[64,18]] → verifier refuses | exclude |
| CAMEL [[1025,583]] | yes | 583 | 33 | — | over caps (w ≤ 32; n ≤ 700 for w > 8) | exclude |
| `without-all-one-col/*`, `H_*_wt*.csv` | **no** (H1·H2ᵀ = J) | — | — | — | not CSS | exclude |
| `Codes_for_comparisons/*`, DLR [[512,174,8]] | third-party | | | | | exclude |

Board has 8 affine-Frobenius QD entries (arXiv:2609.24201, @MathysRennela, n = 64/256); no CAMEL code, nothing at
n = 257.

## Decisions (user)

- Package **only CAMEL [[257,121,10]]**.
- `provenance.authors` = `["@AlessioBaldelli99", "@sisimiao", "Massimo Battaglioni", "@JonathanMandelbaum", "@lschmalen"]`
  (user's list; `@@lschmalen` read as `@lschmalen`; all four handles verified to exist on GitHub).
  Consequence: `verify/check_authorship.py:908-936` binds a new entry to the PR opener, so **the PR must be opened
  by one of @AlessioBaldelli99 / @sisimiao / @JonathanMandelbaum / @lschmalen** — not by LeaCat.
  **@AlessioBaldelli99 will open it** (user).
- @LeaCat appears only as the preparer: `witness_provenance.found_by = ["@LeaCat"]` (the RIS run that produced the
  recorded witnesses; my call) and one sentence in `provenance.notes` ("prepared by @LeaCat: conversion,
  re-verification, packaging; no role in the construction").
- `provenance.model` = `"human"`; no `harness`. Claude Code (Claude Opus 5.5) use is described in notes/Tools.
- Cite the ISIT 2026 paper (title, authors) + pin `github.com/AlessioBaldelli99/UnivPM-KIT @ 886501f`.
- Consent from constructors **pending** → do everything locally through the pre-push checks, then **stop**:
  no fork, no push, no PR.

## Approach

**Environment: WSL2 Ubuntu** (has git, uv, make, g++, 12 cores). Reason: the `--reuse-witnesses` submit route
*requires* the `gf2_fast` accelerator (`cli/qldpc.py:333-351`, ≥ 1M trials), and `verify/gf2_fast.cpp` uses
GCC builtins with no MSVC guards; research extras (pynauty, pycryptosat) also want Linux wheels. **No new clone
or worktree** (user: avoid copies): reuse the existing WSL clone `/home/lialiu/qldpc-challenge` (full checkout,
`origin` = canonical HTTPS, `main` behind origin, no `.venv`, accelerator unbuilt, hooks off, one untracked
user file `qechallenge-wsl.code-workspace` that must never be staged). The Windows checkout is left untouched.
Source matrices are read from the Windows UnivPM-KIT clone at `886501f` via `/mnt/c/...` (the WSL UnivPM-KIT
clone is at older `b5c549b`). New artifacts go to `C:\Users\Liu\Documents\2026-quantum-code\qldpc-submission-work\`;
the only file written into the collaborators' repo is this plan (requested), left untracked.

### Step 0 — save this plan (first action after approval)
Write the finalized plan to
`C:\Users\Liu\Documents\2026-quantum-code\QD-LDPC-Alessio\PCMs\CAMEL_codes\Camel_257_121_10_submission_plan.md`
(untracked in UnivPM-KIT; not committed).

### Step 0b — prepare the existing WSL clone (`/home/lialiu/qldpc-challenge`)
1. `git fetch origin`; `git switch -c submit-257-121-10 origin/main` (local `main` untouched; untracked
   workspace file carries over harmlessly). `origin` = canonical, which `verify/prepush_prose_check.sh` accepts.
2. `git config core.hooksPath .githooks`; `uv sync --extra research` (`.venv`, gitignored); `make fast` (builds
   `verify/gf2_fast*.so`, gitignored). Confirm `import gf2_fast` and run `verify/test_gf2_fast.py`.

### Step 1 — CSV → `.npz` (the requested deliverable)
Script `qldpc-submission-work/convert_pcms.py` (kept outside the repo; method described in the note):
- read `PCMs/CAMEL_codes/QD-LDPC [[257,121]]/QD_CAMEL_[[257,121]]_H_X.csv` and `_H_Z.csv` (`np.loadtxt`, uint8);
- cross-check against the `n257_k121_d10_Hx.alist`/`_Hz.alist` copies; record SHA-256 of the source files;
- assert: shape (112, 257), binary, `css.verify_css`, `css.compute_k == 121`, max row weight 17, Tanner graph
  connected, column 256 all-ones;
- write `camel_257_121.npz` via `np.savez(path, hx=HX, hz=HZ)` (dense uint8, rows = checks) + a JSON manifest.

### Step 2 — stage with witnesses (reuse `research/kit`)
`stage_257.py`, run from `/home/lialiu/qldpc-challenge` with `uv run --extra research python ...`:
- `submit.make_submission(HX, HZ, name="[[257,121,10]] dyadic CAMEL QD-LDPC code (all-one column)",
  construction=<CAMEL description + repo pin>, authors=<5 above>, found_by=["@LeaCat"], family="other",
  references=[<ISIT 2026 paper>, "github.com/AlessioBaldelli99/UnivPM-KIT @ 886501f"],
  notes=<submitter role + "checked, not equivalent" statement>, trials=20000, seed=1)` — numpy per-side witnesses.
- `submit.save_submission(doc, coordination.unique_path(f"{coordination.staging_dir()}/257-121-{d}.json", doc))`;
  a save failure after a witness is found is a hard stop. Expected d = 10.

### Step 3 — gate
`uv run --extra research python research/kit/coordination.py gate <staged.json>` → `<staged>.verdict.json`.
Required: `passed: true`, `gates.novelty.board_advancing: true`, `d_only_gain: false`; record any WL flag.

### Step 4 — deep re-verification (accelerator)
`uv run --frozen --extra research python research/audits/leader_audit.py ladder <staged.json> --ladder 200000:101,102 1000000:201,202 2000000:301,302 --threads 12 --pair-depth 64 --witness-out <work>/257-ladder-witness.json`
(log to `<work>/257-ladder.log`). Must stay flat at 10 on every rung (exit 2 = refuted). The group's codeword
lists (no word of weight < 10 in ker H_X / ker H_Z) are cited as independent corroboration, not certification.

### Step 5 — package with the CLI import route
`./qldpc submit <staged.json> --reuse-witnesses --authors @AlessioBaldelli99 @sisimiao "Massimo Battaglioni" @JonathanMandelbaum @lschmalen --model human --family other --name "[[257,121,10]] dyadic CAMEL QD-LDPC code (all-one column)" --note-file <work>/257-121-10.md --no-circuit`
(default `--fast-trials 2000000` refutation pass; no `--open-pr`). It keeps the draft's construction/notes/
references, records `novelty: known_parameters` (`cli/qldpc.py:413-434`), runs the verifier and frontier check,
writes `codes/257-121-10.json` + `notes/257-121-10.md`, and prints the drafted PR-body path.

### Step 6 — note and PR body
- Note `<work>/257-121-10.md` from `notes/TEMPLATE.md` (≤ 10 KiB), titled `# [[257,121,10]] — dyadic CAMEL
  QD-LDPC code (w = 17)`: Direction (imported ISIT 2026 construction), What was searched (no search; conversion
  recipe), Evidence trail (k, commutation, w, gate verdict, ladder table, `.CW` corroboration with pinned source),
  Dead ends (other PCMs as in the table), Tools (model: human; conversion/verification by Claude Code with Claude
  Opus 5.5 on behalf of @LeaCat), Reproduction (repo pin + commands), Benchmark comparison
  (`[[281,121,4]]` w21, `[[254,126,14]]` w30, QD `[[256,130,8]]` w16).
- PR body → `<work>/pr-body-257-121-10.md`: replace every parenthetical prompt, tick only true boxes (equivalence
  box backed by the `provenance.notes` statement), no HTML comments/local paths/`research/candidates/`; end with
  the Claude Code attribution line.

### Step 7 — checks and local commit (no push)
1. `uv run python verify/check_prose.py --body-file <work>/pr-body-257-121-10.md --files notes/257-121-10.md` → 0
   (if the pinned external CSV path is flagged, cite the folder without a file token).
2. On branch `submit-257-121-10`: `git add codes/257-121-10.json notes/257-121-10.md` (explicit paths only —
   never `git add -A`, the workspace file must stay untracked); commit with the
   `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` trailer (venv activated so the hooks' `python3`
   resolves to it).
3. `uv run python verify/check_authorship.py --author AlessioBaldelli99 --base origin/main` → ok (simulates
   the actual opener; `--author LeaCat` is expected to fail, confirming LeaCat must not open the PR);
   `uv run python verify/check_submission_scope.py --classify --base origin/main` → tier 0.
4. `QLDPC_PYTHON=$PWD/.venv/bin/python verify/prepush_prose_check.sh <work>/pr-body-257-121-10.md` → 0.
5. **Stop.** Export the commit as `<work>/submit-257-121-10.bundle` (`git bundle create ... origin/main..submit-257-121-10`)
   plus `git format-patch` output, and copy the final note, PR body, verdict, ladder log and witness into the work
   folder; `git switch main` so the user's clone is back where it was (branch kept); update the project memory
   with the outcome.

### Deferred hand-off, after the constructors consent (not executed now)
@AlessioBaldelli99 opens the PR from their own GitHub account: fork
`unitaryfoundation/qldpc-challenge`, `git fetch <bundle> submit-257-121-10:submit-257-121-10` (or apply the
patch) on a branch from upstream `main`, run `verify/prepush_prose_check.sh <pr-body.md>`, push to their fork,
`gh pr create --repo unitaryfoundation/qldpc-challenge --base main --body-file <pr-body.md>`. CI's authorship
check then passes because the opener is a listed @handle author.

## Stop conditions

- Gate or ladder finds weight 9 → re-stage as [[257,121,9]] (still board-advancing per `does_it_advance.py`) and
  report before continuing; weight ≤ 8 → dominated, stop, no submission.
- Preflight failure in `save_submission` / gate → stop and report the class; never edit `verify/` (Tier 1).
- `make fast` fails in WSL → stop and report (the reuse route needs it); no edits to `verify/` or `Makefile`.

## Verification (end-to-end)

Converter assertions pass and `.npz` round-trips to the CSVs; gate `passed: true` + `board_advancing: true`;
ladder flat at 10 through 2M trials per side at pair depth 64; `qldpc submit` exits 0 with no frontier/peer-audit
refusal; `check_prose.py`, `check_authorship.py`, scope classify (tier 0) and `prepush_prose_check.sh` all exit 0.
`check_authorship.py --author AlessioBaldelli99` passes. Final report: [[257,121,10]], cell `weight-9plus × unrestricted`
(CSS), ladder depth reached, files produced (`.npz`, staged JSON + verdict, `codes/`/`notes/` files, PR body,
bundle/patch), and the hand-off steps for the constructor who opens the PR.
