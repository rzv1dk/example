# Example Toxicology Site

This is a working example of the GitHub + Cloudflare Pages setup described in
`toxicology-site-operations.md` and `toxicology-site-setup-guide.md`.

- `entries/` — example poison/venom entries (demo content, not verified for real use)
- `templates/` — blank entry templates
- `scripts/validate_frontmatter.py` — CI check enforcing required fields
- `.github/workflows/validate-entries.yml` — runs the check on every PR
- `.github/CODEOWNERS` — reviewer routing (replace `@yourusername`)
- `build.py` — static site generator: reads entries, renders styled HTML into `/dist`

## Run it

    python3 build.py
    open dist/index.html

To turn this into the real thing: push this repo to GitHub, then follow
`toxicology-site-setup-guide.md` from Step 6 onward (branch protection →
Cloudflare Pages → custom domain).
