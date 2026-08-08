#!/usr/bin/env python3
"""Minimal static site generator for the toxicology example site.
Reads entries/**/*.md (YAML frontmatter + Markdown body) and renders
styled HTML into dist/.
"""
import glob
import html
import os

from scripts.content_parser import markdown_to_html, parse_document

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
SECTION_LABEL = {
    "snakes": "Snakes",
    "spiders-scorpions": "Spiders & Scorpions",
    "marine-life": "Marine Life",
    "poisonous-plants": "Poisonous Plants",
    "poisonous-mushrooms": "Poisonous Mushrooms",
    "environmental-toxins": "Environmental Toxins",
}

SECTION_SLUGS = {
    "black-mamba": "snakes",
    "inland-taipan": "snakes",
    "deathstalker-scorpion": "spiders-scorpions",
    "blue-ringed-octopus": "marine-life",
    "box-jellyfish": "marine-life",
    "cone-snail": "marine-life",
    "castor-bean-ricin": "poisonous-plants",
    "oleander": "poisonous-plants",
    "death-cap": "poisonous-mushrooms",
    "carbon-monoxide": "environmental-toxins",
    "cyanide": "environmental-toxins",
    "methanol": "environmental-toxins",
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
.site-nav{max-width:960px;margin:12px auto 0;padding:0 24px;display:flex;gap:6px;flex-wrap:wrap}
.site-nav a{color:var(--text2);font-size:12px;padding:6px 9px;border-radius:7px;border:1px solid transparent}
.site-nav a:hover{color:var(--text);border-color:var(--border);text-decoration:none;background:var(--surface)}
.banner{max-width:960px;margin:16px auto 0;padding:10px 16px;
  background:#241d0f;border:1px solid var(--amber);border-radius:8px;
  color:var(--amber);font-size:13px}
main{max-width:960px;margin:0 auto;padding:24px}
.emergency{display:grid;grid-template-columns:1fr auto;gap:18px;align-items:center;margin-bottom:30px;
  padding:20px 22px;background:#211414;border:1px solid #8c453f;border-radius:12px}
.eyebrow{margin:0 0 5px;color:#ef8b7f;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.08em}
.emergency h1{margin:0;font-size:21px}
.emergency p{margin:6px 0 0;color:#c8b9b5;font-size:13px;max-width:680px}
.emergency-links{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}
.emergency-link{display:inline-flex;align-items:center;min-height:38px;padding:7px 12px;border-radius:8px;
  border:1px solid #d56d62;color:#f4c2bc;font-size:12px;font-weight:700;white-space:nowrap}
.emergency-link:hover{background:#321c1b;text-decoration:none}
.directory{margin-bottom:30px}
.section-heading{margin:0;font-size:22px}
.section-intro{margin:6px 0 0;color:var(--text2);font-size:14px;max-width:720px}
.browse-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:16px}
.browse-card{min-height:104px;text-align:left;padding:15px;border:1px solid var(--border);border-radius:11px;
  background:var(--surface);color:var(--text);cursor:pointer}
.browse-card:hover{border-color:var(--accent);background:#192019}
.browse-card strong{display:block;font-size:14px}
.browse-card span{display:block;margin-top:4px;color:var(--text2);font-size:12px}
.browse-count{margin-top:12px!important;color:var(--accent)!important;font-weight:650}
.catalog{scroll-margin-top:16px}
.catalog-heading{display:flex;align-items:baseline;justify-content:space-between;gap:12px}
.catalog-heading h2{font-size:14px;color:var(--text2);font-weight:600;text-transform:uppercase;
  letter-spacing:.06em;margin:0}
.result-count{color:var(--text2);font-size:12px}
.search-panel{display:grid;grid-template-columns:minmax(210px,1fr) 165px 145px 135px auto;
  gap:10px;margin-top:14px;padding:14px;background:var(--surface);border:1px solid var(--border);
  border-radius:12px}
.field{display:flex;flex-direction:column;gap:5px}
.field label{font-size:11px;font-weight:650;color:var(--text2);text-transform:uppercase;letter-spacing:.05em}
input,select,button{font:inherit}
input,select{width:100%;height:40px;color:var(--text);background:var(--bg);border:1px solid var(--border);
  border-radius:8px;padding:0 11px}
input:focus,select:focus{outline:2px solid var(--accent);outline-offset:1px;border-color:transparent}
.clear-button{align-self:end;height:40px;border:1px solid var(--border);border-radius:8px;
  padding:0 14px;background:var(--surface2);color:var(--text);cursor:pointer}
.clear-button:hover{border-color:var(--accent)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px;margin-top:16px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:18px;display:block}
.card:hover{border-color:var(--accent);text-decoration:none}
.card[hidden]{display:none}
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
.empty-state{display:none;margin:20px 0;color:var(--text2);font-size:14px}
.empty-state.visible{display:block}
.get-involved{margin-top:34px;padding:22px;background:linear-gradient(135deg,#162016,#16181a 68%);
  border:1px solid #365535;border-radius:12px}
.get-involved h2{margin:0 0 6px;font-size:18px}
.get-involved p{margin:0;color:var(--text2);font-size:14px;max-width:680px}
.actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}
.action{display:inline-flex;align-items:center;min-height:40px;padding:8px 13px;border-radius:8px;
  border:1px solid var(--accent);font-size:13px;font-weight:650}
.action.secondary{border-color:var(--border);color:var(--text)}
.action:hover{background:#20301f;text-decoration:none}
.about-resource{margin-top:22px;padding:20px 22px;border:1px solid var(--border);border-radius:12px;background:var(--surface)}
.about-resource h2{margin:0 0 7px;font-size:17px}
.about-resource p{margin:0;color:var(--text2);font-size:13px}
.about-resource p+p{margin-top:9px}
ul{padding-left:20px}
footer{max-width:960px;margin:40px auto 24px;padding:0 24px;color:var(--text2);font-size:12px}
@media(max-width:720px){
  .emergency{grid-template-columns:1fr}
  .emergency-links{justify-content:flex-start}
  .browse-grid{grid-template-columns:1fr 1fr}
  .search-panel{grid-template-columns:1fr 1fr}
  .field.search-field{grid-column:1/-1}
}
@media(max-width:480px){
  .browse-grid{grid-template-columns:1fr}
  .search-panel{grid-template-columns:1fr}
  .field.search-field{grid-column:auto}
  .clear-button{width:100%}
}
"""

def load_entries():
    entries = []
    for path in sorted(glob.glob("entries/**/*.md", recursive=True)):
        raw = open(path, encoding="utf-8").read()
        fm, body = parse_document(raw)
        fm["slug"] = os.path.splitext(os.path.basename(path))[0]
        fm["body_html"] = markdown_to_html(body)
        entries.append(fm)
    return entries

def badge(text, color):
    return f'<span class="badge" style="color:{color};border-color:{color}66">{text}</span>'

def browse_description(section):
    descriptions = {
        "snakes": "Venom, clinical effects, first aid and treatment context.",
        "spiders-scorpions": "Terrestrial invertebrate bites and stings.",
        "marine-life": "Jellyfish, molluscs and other marine envenomations.",
        "poisonous-plants": "Plant toxins and accidental exposure risks.",
        "poisonous-mushrooms": "Toxic fungi and delayed poisoning syndromes.",
        "environmental-toxins": "Important non-biological toxic exposures.",
    }
    return descriptions.get(section, "Browse reference entries.")

def page_shell(title, body_html):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>{CSS}</style></head><body>
<header>
  <div class="brand">Tox<span>icology</span> Reference <span style="color:var(--text2);font-weight:400;font-size:13px">— example</span></div>
  <div class="tagline">A community-reviewed reference on poisons and venoms.</div>
</header>
<nav class="site-nav" aria-label="Primary navigation">
  <a href="index.html#first-aid">First aid</a>
  <a href="index.html#directory">Site directory</a>
  <a href="index.html#catalog">Browse entries</a>
  <a href="index.html#about">About</a>
  <a href="index.html#get-involved">Get involved</a>
</nav>
<div class="banner">EXAMPLE CONTENT — this site demonstrates the design and publishing pipeline only. Entries are not verified for real-world use. In an actual poisoning or envenomation event, contact emergency services or a poison control center.</div>
<main>{body_html}</main>
<footer>Built from Markdown in this repo &middot; example of the GitHub + Cloudflare Pages setup</footer>
</body></html>"""

def render_index(entries):
    cards = ""
    section_counts = {section: 0 for section in SECTION_LABEL}
    for e in entries:
        sev_color = SEVERITY_COLOR.get(e.get("severity"), "#9c9c94")
        excerpt = (e.get("mechanism_of_toxicity") or "")[:110] + "…"
        section = SECTION_SLUGS.get(e["slug"], "environmental-toxins")
        section_counts[section] += 1
        search_text = " ".join([
            e.get("common_name", ""), e.get("scientific_name", ""),
            CATEGORY_LABEL.get(e.get("category"), e.get("category", "")),
            SECTION_LABEL.get(section, section), e.get("severity", ""),
            e.get("mechanism_of_toxicity", ""),
        ]).lower()
        cards += f"""<a class="card" href="{e['slug']}.html"
  data-search="{html.escape(search_text, quote=True)}"
  data-section="{section}"
  data-category="{html.escape(e.get('category', ''), quote=True)}"
  data-severity="{html.escape(e.get('severity', ''), quote=True)}">
  <h3>{e['common_name']}</h3>
  <p class="sci">{e['scientific_name']}</p>
  <div class="badges">
    {badge(CATEGORY_LABEL.get(e.get('category'), e.get('category','')), '#7fd858')}
    {badge(e.get('severity','').title(), sev_color)}
  </div>
  <p class="excerpt">{excerpt}</p>
</a>"""
    browse_cards = "".join(
        f"""<button class="browse-card" type="button" data-browse-section="{section}">
  <strong>{label}</strong>
  <span>{browse_description(section)}</span>
  <span class="browse-count">{section_counts[section]} {"entry" if section_counts[section] == 1 else "entries"}</span>
</button>"""
        for section, label in SECTION_LABEL.items()
    )
    body = f"""<section class="emergency" id="first-aid" aria-labelledby="emergency-title">
  <div>
    <p class="eyebrow">Australian emergency guidance</p>
    <h1 id="emergency-title">Need help now?</h1>
    <p>If someone has collapsed, stopped breathing, had a seizure, or has a severe allergic reaction, call Triple Zero (000). For suspected poisoning without those emergency signs, call the Poisons Information Centre on 13 11 26.</p>
  </div>
  <div class="emergency-links">
    <a class="emergency-link" href="tel:000">Call 000</a>
    <a class="emergency-link" href="tel:131126">Poisons: 13 11 26</a>
    <a class="emergency-link" href="https://www.healthdirect.gov.au/poisoning">Official guidance</a>
  </div>
</section>
<section class="directory" id="directory" aria-labelledby="directory-title">
  <p class="eyebrow" style="color:var(--accent)">Clinical toxinology directory</p>
  <h2 class="section-heading" id="directory-title">Explore by source</h2>
  <p class="section-intro">A modern directory based on the broad subject structure of the former Toxinology.com resource: venomous animals, poisonous organisms, plants, mushrooms, and practical clinical context.</p>
  <div class="browse-grid">{browse_cards}</div>
</section>
<section class="catalog" id="catalog" aria-labelledby="catalog-title">
<div class="catalog-heading">
  <h2 id="catalog-title">All entries ({len(entries)})</h2>
  <span class="result-count" id="result-count" aria-live="polite">Showing all {len(entries)}</span>
</div>
<div class="search-panel" role="search" aria-label="Search toxicology entries">
  <div class="field search-field">
    <label for="entry-search">Search entries</label>
    <input id="entry-search" type="search" placeholder="Name, species, toxin or mechanism…" autocomplete="off">
  </div>
  <div class="field">
    <label for="section-filter">Area</label>
    <select id="section-filter">
      <option value="">All areas</option>
      {''.join(f'<option value="{section}">{label}</option>' for section, label in SECTION_LABEL.items())}
    </select>
  </div>
  <div class="field">
    <label for="category-filter">Category</label>
    <select id="category-filter">
      <option value="">All categories</option>
      <option value="venom">Venom</option>
      <option value="plant-toxin">Plant toxin</option>
      <option value="chemical">Chemical</option>
    </select>
  </div>
  <div class="field">
    <label for="severity-filter">Severity</label>
    <select id="severity-filter">
      <option value="">All severities</option>
      <option value="lethal">Lethal</option>
      <option value="high">High</option>
      <option value="moderate">Moderate</option>
      <option value="low">Low</option>
    </select>
  </div>
  <button class="clear-button" id="clear-filters" type="button">Clear</button>
</div>
<div class="grid" id="entry-grid">{cards}</div>
<p class="empty-state" id="empty-state">No entries match those filters. Try a broader search.</p>
</section>
<section class="get-involved" id="get-involved" aria-labelledby="get-involved-title">
  <h2 id="get-involved-title">Get involved</h2>
  <p>Help improve the reference by suggesting a subject, reporting a correction, or sending feedback directly to the webmaster. Each message is tracked publicly so progress is easy to follow.</p>
  <div class="actions">
    <a class="action" href="https://github.com/rzv1dk/example/issues/new?title=Entry%20suggestion%3A%20">Suggest an entry</a>
    <a class="action secondary" href="https://github.com/rzv1dk/example/issues/new?title=Content%20correction%3A%20">Report a correction</a>
    <a class="action secondary" href="https://github.com/rzv1dk/example/issues/new?title=Webmaster%20feedback%3A%20">Contact the webmaster</a>
    <a class="action secondary" href="https://github.com/rzv1dk/example">View the project</a>
  </div>
</section>
<section class="about-resource" id="about" aria-labelledby="about-title">
  <h2 id="about-title">About this rebuild</h2>
  <p>The former Clinical Toxinology Resources website was created as a searchable global reference covering venomous snakes, spiders, scorpions, marine organisms, poisonous plants and mushrooms, antivenoms, and clinical management. This independent example rebuild preserves that broad directory concept in a current, accessible interface.</p>
  <p>It is not an official replacement, is not affiliated with the University of Adelaide or Women’s and Children’s Hospital, and currently contains only twelve demonstration entries. Historical context: <a href="https://www.mja.com.au/journal/2002/177/11/wwwtoxinologycom">Medical Journal of Australia overview</a>.</p>
</section>
<script>
(() => {{
  const search = document.querySelector('#entry-search');
  const section = document.querySelector('#section-filter');
  const category = document.querySelector('#category-filter');
  const severity = document.querySelector('#severity-filter');
  const cards = [...document.querySelectorAll('.card')];
  const count = document.querySelector('#result-count');
  const empty = document.querySelector('#empty-state');

  function applyFilters() {{
    const query = search.value.trim().toLowerCase();
    let visible = 0;
    cards.forEach(card => {{
      const matches = (!query || card.dataset.search.includes(query)) &&
        (!section.value || card.dataset.section === section.value) &&
        (!category.value || card.dataset.category === category.value) &&
        (!severity.value || card.dataset.severity === severity.value);
      card.hidden = !matches;
      if (matches) visible += 1;
    }});
    count.textContent = visible === cards.length ? `Showing all ${{visible}}` : `Showing ${{visible}} of ${{cards.length}}`;
    empty.classList.toggle('visible', visible === 0);
  }}

  search.addEventListener('input', applyFilters);
  section.addEventListener('change', applyFilters);
  category.addEventListener('change', applyFilters);
  severity.addEventListener('change', applyFilters);
  document.querySelector('#clear-filters').addEventListener('click', () => {{
    search.value = '';
    section.value = '';
    category.value = '';
    severity.value = '';
    applyFilters();
    search.focus();
  }});
  document.querySelectorAll('[data-browse-section]').forEach(button => {{
    button.addEventListener('click', () => {{
      search.value = '';
      section.value = button.dataset.browseSection;
      category.value = '';
      severity.value = '';
      applyFilters();
      document.querySelector('#catalog').scrollIntoView({{behavior: 'smooth', block: 'start'}});
    }});
  }});
}})();
</script>"""
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
