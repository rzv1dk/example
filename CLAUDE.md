# CLAUDE.md — Toxicology Reference Site

Project context for Claude Code. Drop this file in the root of the `example-site` repo (already git-initialized and pushed to `github.com/rzv1dk/example`).

## What this project is

A static, git-backed toxicology reference site (poisons and venoms). There is no application server or database — the GitHub repo is the datastore. Content is Markdown with YAML frontmatter; a Python script builds it into static HTML; Cloudflare Pages hosts it.

## Repo layout

```
entries/poisons/       one .md file per substance, YAML frontmatter + Markdown body
entries/venoms/         one .md file per species
templates/               blank templates to copy when adding a new entry
scripts/validate_frontmatter.py   CI check — fails if required fields are missing
.github/workflows/validate-entries.yml   runs the check on every PR
.github/CODEOWNERS       reviewer routing (update the placeholder username)
build.py                 static site generator — reads entries/, writes dist/
dist/                    build output — gitignored, not committed
```

## Required frontmatter fields (enforced by CI)

`title`, `common_name`, `scientific_name`, `category`, `severity`, `mechanism_of_toxicity`, `treatment`, `sources`. A PR fails validation if any of these are empty.

## Content standards

Every claim about toxicity, symptoms, or treatment must be sourced (`sources` field, non-empty). Content is reference information, not medical advice — this disclaimer appears on every page and should not be removed. Existing entries are demo/placeholder content and are explicitly marked as unverified; real entries need real citations before being treated as authoritative.

## Governance model

Public contributors fork and open a PR; trusted editors can push branches directly. Every change requires: CI passing (schema + citation check) → human review (routed via CODEOWNERS) → merge to `main`. No one pushes directly to `main`. Full detail in `toxicology-site-operations.md` if that file is present in this repo or the working folder.

## Local development

```
python3 build.py                        # builds dist/ from entries/
python3 scripts/validate_frontmatter.py  # runs the same check CI runs
open dist/index.html                     # preview locally
```

## Deployment

Cloudflare Pages is connected to this GitHub repo. Build command: `python3 build.py`. Output directory: `dist`. Production branch: `main`. Every open PR also gets an automatic preview deployment.

## Current status / remaining setup

- [x] Repo created and pushed to GitHub
- [ ] `.github/CODEOWNERS` still has a placeholder username — replace with the real reviewer(s)
- [ ] Branch protection not yet enabled on `main` (require PR + review + passing CI)
- [ ] Cloudflare Pages project not yet connected
- [ ] Custom domain not yet attached
- [ ] `dist/` not yet gitignored — check before next commit

## Security — do not skip this

- Never write API tokens, passwords, or other credentials into files in this repo, including this one. If a workflow needs a secret (e.g., a bot token for AI-drafted PRs), it belongs in GitHub Actions repository secrets, not in tracked files.
- Don't commit a `.env` file with real values. If one is needed locally, keep it out of git via `.gitignore`.
- If a secret is ever accidentally committed, treat it as compromised: revoke/rotate it immediately, don't just remove it in a later commit (it's still in git history).
