#!/usr/bin/env python3
"""Minimal static site generator for the toxicology example site.
Reads entries/**/*.md (YAML frontmatter + Markdown body) and renders
styled HTML into dist/.
"""
import glob, os, shutil, yaml, markdown
from datetime import date

SEVERITY_COLOR = {
    "lethal": "#e05a4e",
    "high": "#e0a72e",
    "moderate": "#d8c869",
    "low": "#7fd858",
}
CATEGORY_LABEL = {
    "venom": "Venom",
    "plant-toxin": "Plant Toxin",
    "chemical": "Chemical",
}

CSS = """
:root{
  --bg:#0c0d0b; --surface:#16181a; --surface2:#1c1f1c; --border:#2b2e2a;
  --text:#eae7e0; --text2:#9c9c94; --accent:#7fd858; --amber:#e0a72e;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
  font-family:-apple-system,Segoe UI,Inter,sans-serif;line-height:1.55}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
header{padding:28px 24px 8px;max-width:960px;margin:0 auto}
.brand{font-size:22px;font-weight:700;letter-spacing:.01em}
.brand span{color:var(--accent)}
.tagline{color:var(--text2);font-size:14px;margin-top:4px}
.banner{max-width:960px;margin:16px auto 0;padding:10px 16px;
  background:#241d0f;border:1px solid var(--amber);border-radius:8px;
  color:var(--amber);font-size:13px}
main{max-width:960px;margin:0 auto;padding:24px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px;margin-top:16px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:18px;display:block}
.card:hover{border-color:var(--accent);text-decoration:none}
.card h3{margin:0 0 2px;font-size:16px;color:var(--text)}
.sci{color:var(--text2);font-style:italic;font-size:12.5px;margin:0 0 10px}
.badges{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px}
.badge{font-size:11px;font-weight:600;padding:3px 9px;border-radius:999px;border:1px solid var(--border)}
.excerpt{color:var(--text2);font-size:13px}
.back{color:var(--text2);font-size:13px}
.entry h1{font-size:28px;margin:12px 0 2px}
.entry .sci{font-size:15px;margin-bottom:14px}
.entry section{margin-top:22px}
.entry h2{font-size:15px;text-transform:uppercase;letter-spacing:.06em;color:var(--accent);
  border-bottom:1px solid var(--border);padding-bottom:6px}
.meta{color:var(--text2);font-size:12px;margin-top:36px;border-top:1px solid var(--border);padding-top:12px}
ul{padding-left:20px}
footer{max-width:960px;margin:40px auto 24px;padding:0 24px;color:var(--text2);font-size:12px}
"""

def load_entries():
    entries = []
    for path in sorted(glob.glob("entries/**/*.md", recursive=True)):
        raw = open(path, encoding="utf-8").read()
        _, fm_text, body = raw.split("---", 2)
        fm = yaml.safe_load(fm_text)
        fm["slug"] = os.path.splitext(os.path.basename(path))[0]
        fm["body_html"] = markdown.markdown(body.strip())
        entries.append(fm)
    return entries

def badge(text, color):
    return f'<span class="badge" style="color:{color};border-color:{color}66">{text}</span>'

def page_shell(title, body_html):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>{CSS}</style></head><body>
<header>
  <div class="brand">Tox<span>icology</span> Reference <span style="color:var(--text2);font-weight:400;font-size:13px">— example</span></div>
  <div class="tagline">A community-reviewed reference on poisons and venoms.</div>
</header>
<div class="banner">EXAMPLE CONTENT — this site demonstrates the design and publishing pipeline only. Entries are not verified for real-world use. In an actual poisoning or envenomation event, contact emergency services or a poison control center.</div>
<main>{body_html}</main>
<footer>Built from Markdown in this repo &middot; example of the GitHub + Cloudflare Pages setup</footer>
</body></html>"""

def render_index(entries):
    cards = ""
    for e in entries:
        sev_color = SEVERITY_COLOR.get(e.get("severity"), "#9c9c94")
        excerpt = (e.get("mechanism_of_toxicity") or "")[:110] + "…"
        cards += f"""<a class="card" href="{e['slug']}.html">
  <h3>{e['common_name']}</h3>
  <p class="sci">{e['scientific_name']}</p>
  <div class="badges">
    {badge(CATEGORY_LABEL.get(e.get('category'), e.get('category','')), '#7fd858')}
    {badge(e.get('severity','').title(), sev_color)}
  </div>
  <p class="excerpt">{excerpt}</p>
</a>"""
    body = f'<h2 style="font-size:14px;color:var(--text2);font-weight:600;text-transform:uppercase;letter-spacing:.06em">All entries ({len(entries)})</h2><div class="grid">{cards}</div>'
    return page_shell("Toxicology Reference — Example", body)

def render_entry(e):
    sev_color = SEVERITY_COLOR.get(e.get("severity"), "#9c9c94")
    symptoms = "".join(f"<li>{s}</li>" for s in e.get("symptoms", []))
    sources = "".join(f"<li>{s}</li>" for s in e.get("sources", []))
    body = f"""<a class="back" href="index.html">&larr; All entries</a>
<div class="entry">
  <h1>{e['common_name']}</h1>
  <p class="sci">{e['scientific_name']}</p>
  <div class="badges">
    {badge(CATEGORY_LABEL.get(e.get('category'), e.get('category','')), '#7fd858')}
    {badge(e.get('severity','').title(), sev_color)}
  </div>
  <section><h2>Mechanism of Toxicity</h2><p>{e.get('mechanism_of_toxicity','')}</p></section>
  <section><h2>Onset</h2><p>{e.get('onset','')}</p></section>
  <section><h2>Symptoms</h2><ul>{symptoms}</ul></section>
  <section><h2>Treatment</h2><p>{e.get('treatment','')}</p></section>
  <section><h2>Antidote</h2><p>{e.get('antidote','')}</p></section>
  <section>{e['body_html']}</section>
  <section><h2>Sources</h2><ul>{sources}</ul></section>
  <div class="meta">Last reviewed {e.get('last_reviewed','—')} &middot; {e.get('reviewed_by','—')}</div>
</div>"""
    return page_shell(f"{e['common_name']} — Toxicology Reference", body)

def main():
    os.makedirs("dist", exist_ok=True)
    entries = load_entries()
    open("dist/index.html", "w", encoding="utf-8").write(render_index(entries))
    for e in entries:
        open(f"dist/{e['slug']}.html", "w", encoding="utf-8").write(render_entry(e))
    print(f"Built {len(entries)} entries into dist/")

if __name__ == "__main__":
    main()
