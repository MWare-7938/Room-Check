# Upload to GitHub

A short cheat sheet for getting this repo onto github.com. Pick whichever of the three paths matches your comfort level.

**Before you start, make sure these files exist alongside this one (they should):**

```
README.md   LICENSE   .gitignore   pyproject.toml   src/   tests/
```

If they don't, you're in the wrong folder.

---

## Path 1 — git CLI (recommended)

```powershell
# Windows PowerShell
cd "$env:USERPROFILE\Documents\Orivia\room-check-oss"

git init
git add .
git status                  # ← scan for .dyson-auth.json. Should NOT appear.
git commit -m "Initial release v1.0.0"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/room-check.git
git push -u origin main
```

```bash
# macOS / Linux
cd ~/Documents/Orivia/room-check-oss
# ...rest is identical
```

When `git push` asks for credentials:
- Username: your GitHub username
- Password: a **personal access token** from https://github.com/settings/tokens (NOT your GitHub password — GitHub doesn't accept those in the terminal)

The token needs the `repo` scope. 7-day expiry is fine for the hackathon.

---

## Path 2 — GitHub Desktop (point-and-click)

1. Install from https://desktop.github.com.
2. **File → Add local repository** → browse to `room-check-oss` → **Add repository**.
3. It says "not a Git repository" → click **create a repository**.
4. Bottom-left: commit message `Initial release v1.0.0` → **Commit to main**.
5. Top: **Publish repository** → uncheck "Keep this code private" → **Publish repository**.

Done.

---

## Path 3 — GitHub web UI (drag-and-drop, no software)

1. github.com → **+** → **New repository**.
2. Name: `room-check`. Description: `Open-source indoor air-quality safety translator`. **Public**. **Don't** check any "Initialize" boxes.
3. Click **Create repository**.
4. Click **uploading an existing file** on the next page.
5. **Enable hidden files in File Explorer first:** View → Show → Hidden items. Otherwise `.gitignore` and `.github/` won't appear in the drag.
6. Open `C:\Users\miche\Documents\Orivia\room-check-oss\` → press `Ctrl+A` → drag everything into the browser.
7. Wait for the upload bar to complete.
8. Commit message: `Initial release v1.0.0` → **Commit changes**.

---

## Pre-push checklist

Run these checks before you push, regardless of which path you picked:

- [ ] `.dyson-auth.json` is NOT in the folder. Run `dir .dyson-auth.json` (Windows) or `ls .dyson-auth.json` (mac/Linux). "File not found" is the answer you want.
- [ ] No `__pycache__/` or `.pytest_cache/` showing up in your commit. The `.gitignore` should block them.
- [ ] You replaced `YOUR-ORG` in `pyproject.toml` line 39 and the README badge URLs with your actual GitHub username.
- [ ] You can run `pytest` locally and all tests pass (`pip install -e ".[dev]" && pytest`).

---

## After the first push — 5 minutes of polish

These take 1 minute each but make the repo look professional.

### Add a description and topics

On the repo page, click the ⚙ gear next to "About" (top-right).

- Description: `Open-source indoor air-quality safety translator. Sensor-agnostic. GREEN/YELLOW/RED + plain-language alerts.`
- Website: leave blank or paste your demo URL
- Topics: `air-quality`, `iaq`, `co2`, `pm25`, `voc`, `sensors`, `dyson`, `inkbird`, `python`, `open-source`, `home-automation`, `building-resilience`

### Tag a release

**Releases → Draft a new release**:
- Choose tag: `v1.0.0` (create new tag on publish)
- Title: `Room Check v1.0.0`
- Description: paste the contents of `CHANGELOG.md`
- Attach files: drag `room-check-oss-v1.0.0.zip` from `Documents/Orivia/`
- Click **Publish release**

Anyone can now download the zip from `https://github.com/YOUR-USERNAME/room-check/releases/latest`.

### Verify CI ran

Go to the **Actions** tab. The GitHub Actions workflow in `.github/workflows/test.yml` should have triggered automatically on your first push. It runs the test suite on Linux/macOS/Windows × Python 3.10/3.11/3.12 — should turn green within ~3 minutes.

If it failed, click into it to see the error. Common cause: missing test dependency. Fix and push again.

### Pin one issue or discussion

Open an Issue titled "Roadmap — what's next" with the bullet list from README.md's Roadmap section. Pin it. New contributors will use this to find good first issues.

---

## When you push updates later

Every time you change code:

```powershell
git add .
git commit -m "describe what changed"
git push
```

GitHub Actions reruns automatically. If you want to release a new version:

1. Bump the version in `pyproject.toml` and `src/roomcheck/__init__.py`.
2. Add a `## [1.x.y]` section to `CHANGELOG.md`.
3. Commit + push.
4. **Releases → Draft a new release** → tag `v1.x.y`.

---

## If something goes wrong

**"fatal: Authentication failed"** → You typed your GitHub password instead of a personal access token. Generate a token at https://github.com/settings/tokens, paste that as the password.

**"failed to push some refs"** → Someone (or you, on another machine) pushed first. Run `git pull --rebase` then `git push`.

**".dyson-auth.json was committed by accident"** → Change your MyDyson password right now (the old one is in git history). Then:
```bash
git rm .dyson-auth.json
git commit -m "remove credentials"
git push
```
The old commit still has it in history. For a hackathon repo that's acceptable as long as you've rotated the password. For a serious project, use BFG Repo-Cleaner to purge it from history entirely.

**"hidden files won't drag into the browser"** → Windows hides `.gitignore` and `.github/`. Open File Explorer → View → Show → Hidden items. Try the drag again. Or just use Path 1 (git CLI), which doesn't have this problem.

**"GitHub Actions is failing on Windows but passing elsewhere"** → Common; usually a path-separator issue. Open the failing run, click into the failed step, copy the error here and we'll debug.

---

## TL;DR

```powershell
cd "$env:USERPROFILE\Documents\Orivia\room-check-oss"
git init && git add . && git status
# verify nothing sensitive
git commit -m "Initial release v1.0.0"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/room-check.git
git push -u origin main
```

Then add description, topics, and a Release on github.com. Done.
