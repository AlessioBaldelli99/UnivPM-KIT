# Opening the PR for CAMEL [[257,121,10]]

## Before you start

**Who opens the PR:** @AlessioBaldelli99, or one of the other listed @handle authors (@sisimiao, @JonathanMandelbaum, @lschmalen). CI's authorship check (`verify/check_authorship.py`) requires the PR opener to be a listed author. That check was run locally: it passes for @AlessioBaldelli99 and fails for @LeaCat.

**What you are submitting:** three commits on top of unitaryfoundation/qldpc-challenge `main` @ `067168503`. They add two files:

- `codes/257-121-10.json`: the entry. It is a CSS code with n = 257, k = 121 and d ≤ 10 on both sides, as witness-backed upper bounds. Its max check weight is 17, so it sits in the weight-9plus × unrestricted cell.
- `notes/257-121-10.md`: the research note.

All of the files below are in this folder:

| File | What it is |
|---|---|
| `submit-257-121-10.bundle` | git bundle of the 3 commits; it needs commit `067168503` to be present |
| `patches/0001…0003-*.patch` | the same commits as patches, for `git am` |
| `pr-body-257-121-10.md` | the finished PR body: prompts replaced, checklist true, prose check passed |
| `gate_257.verdict.json`, `257-ladder.log`, `checks_final.log` | the evidence: gate verdict, deep RIS ladder, final checks |

## Steps

Run these from a clone of unitaryfoundation/qldpc-challenge. A sparse worktree is recommended; see AGENTS.md, "Worktrees".

1. Fork unitaryfoundation/qldpc-challenge if you have no fork yet:
   ```
   gh repo fork unitaryfoundation/qldpc-challenge --clone=false
   ```

2. Get the branch:
   ```
   git fetch origin main
   git fetch <path>/submit-257-121-10.bundle submit-257-121-10:submit-257-121-10
   git switch submit-257-121-10
   ```
   Or, as an alternative:
   ```
   git switch -c submit-257-121-10 origin/main && git am <path>/patches/*.patch
   ```
   If `main` has moved, run `git rebase origin/main`. Then confirm the code still advances its cell:
   ```
   uv run --extra research python research/does_it_advance.py --n 257 --k 121 --d 10 --w 17 --locality unrestricted
   ```
   It should report `board_advancing: True`.

3. Run the pre-push gate. It must exit 0:
   ```
   PR_AUTHOR=AlessioBaldelli99 verify/prepush_prose_check.sh <path>/pr-body-257-121-10.md
   ```
   This was not run as-is during preparation, because the prepared clone is a full 9 GB checkout and the script makes a full temporary worktree of it. Its two components did pass on the final commit:
   - `check_submission_scope.py --base origin/main`
   - `check_prose.py --base origin/main` with the body and the note

4. Push the branch to your fork:
   ```
   git push -u <your-fork-remote> submit-257-121-10
   ```

5. Open the PR:
   ```
   gh pr create --repo unitaryfoundation/qldpc-challenge --base main \
     --head AlessioBaldelli99:submit-257-121-10 \
     --title "Add [[257,121,10]] dyadic CAMEL QD-LDPC code (weight-9plus, unrestricted)" \
     --body-file <path>/pr-body-257-121-10.md
   ```

CI re-verifies the code and the distance, and runs the prose, scope and authorship checks.
