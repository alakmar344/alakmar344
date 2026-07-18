#!/usr/bin/env python3
"""Generate banner.svg dynamically from the GitHub API for user alakmar344.

Run by the daily GitHub Actions workflow. Regenerates the contribution graph,
featured projects, and most-used languages sections.
"""
import json
import urllib.request
from datetime import datetime, timezone

USER = "alakmar344"
API = "https://api.github.com/users/" + USER
REPOS_API = API + "/repos?per_page=100&sort=updated"

LANG_COLORS = {
    "HTML": "#e34c26",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Kotlin": "#a97bff",
    "C++": "#f34b7d",
    "Python": "#3572A5",
    "CSS": "#563d7c",
    "Java": "#b07219",
    "Go": "#00ADD8",
    "Rust": "#dea584",
    "Shell": "#89e051",
}


def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "banner-generator",
        "Accept": "application/vnd.github+json",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def main():
    profile = fetch(API)
    repos = fetch(REPOS_API)

    # total public repos / products note
    public_repos = profile.get("public_repos", 0)

    # featured projects: ranked by stars, fallback to recency
    ranked = sorted(
        repos,
        key=lambda r: (r.get("stargazers_count", 0), r.get("pushed_at") or ""),
        reverse=True,
    )
    top_repos = [r for r in ranked if r.get("name")][:4]

    # most used languages by repo count
    lang_counts = {}
    for r in repos:
        lang = r.get("language")
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
    top_langs = sorted(lang_counts.items(), key=lambda x: -x[1])[:4]

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    repo_rows = "\n".join(
        f'  <text class="repo" x="60" y="{328 + i * 20}">★ {esc(r["name"])}</text>'
        for i, r in enumerate(top_repos)
    )

    lang_rows = "\n".join(
        f'  <rect class="lang-dot" x="420" y="{322 + i * 24}" width="10" height="10" style="fill:{LANG_COLORS.get(lang, "#888")}"/>\n'
        f'  <text class="lang-name" x="438" y="{331 + i * 24}">{esc(lang)}</text>\n'
        f'  <text class="lang-count" x="715" y="{331 + i * 24}" text-anchor="end">{count}</text>'
        for i, (lang, count) in enumerate(top_langs)
    )

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg fill="none" viewBox="0 0 800 440" width="800" height="440" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" font-family="'IBM Plex Mono', monospace">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,700;1,600&amp;family=Crimson+Text&amp;family=IBM+Plex+Mono&amp;display=swap');

      .container {{ fill: #F3F0E9; }}
      .header {{ font-family: 'IBM Plex Mono', monospace; fill: #999; font-size: 10px; letter-spacing: 2.5px; }}
      .line {{ stroke: #999; stroke-width: 1; }}
      .title {{ font-family: 'Crimson Pro', serif; font-weight: 700; font-size: 26px; fill: #1A1A1A; }}
      .title-i {{ fill: #B84333; font-weight: 600; font-style: italic; }}
      .section-label {{ font-family: 'IBM Plex Mono', monospace; fill: #A3A098; font-size: 10px; letter-spacing: 2px; }}
      .repo {{ font-family: 'Crimson Text', serif; font-size: 13px; fill: #333; }}
      .lang-dot {{ rx: 3; }}
      .lang-name {{ font-family: 'IBM Plex Mono', monospace; font-size: 11px; fill: #444; }}
      .lang-count {{ font-family: 'IBM Plex Mono', monospace; font-size: 11px; fill: #999; }}
      .rule {{ stroke: #D1CEC7; stroke-width: 1; }}
      .card {{ fill: #FAF8F3; stroke: #E4E0D8; stroke-width: 1; rx: 8; }}
    </style>
    <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
      <path d="M10 0H0V10" fill="none" stroke="#ECE8DF" stroke-width="0.5"/>
    </pattern>
  </defs>

  <rect class="container" x="0" y="0" width="800" height="440" rx="12"/>
  <rect x="0" y="0" width="800" height="440" rx="12" fill="url(#grid)"/>

  <line class="line" x1="45" y1="40" x2="80" y2="40"/>
  <text class="header" x="92" y="44">ALAKMAR TEENWALA — FOUNDER &amp; LEAD ARCHITECT</text>

  <text class="title" x="45" y="78">What shall we <tspan class="title-i">architect</tspan> today?</text>

  <rect class="card" x="45" y="98" width="710" height="170"/>
  <text class="section-label" x="60" y="118">GITHUB CONTRIBUTIONS · @{USER}</text>
  <image x="60" y="128" width="680" height="120"
         xlink:href="https://ghchart.rshah.org/1A1A1A/{USER}"/>
  <text class="lang-count" x="60" y="258">source: github.com/{USER}</text>

  <rect class="card" x="45" y="284" width="350" height="130"/>
  <text class="section-label" x="60" y="304">FEATURED PROJECTS</text>
{repo_rows}
  <text class="lang-count" x="60" y="408">{public_repos} public repos</text>

  <rect class="card" x="405" y="284" width="350" height="130"/>
  <text class="section-label" x="420" y="304">MOST USED LANGUAGES</text>
{lang_rows}

  <line class="rule" x1="45" y1="428" x2="755" y2="428"/>
  <text class="lang-count" x="755" y="440" text-anchor="end">generated {generated}</text>
</svg>
'''

    with open("banner.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"banner.svg regenerated at {generated}")


if __name__ == "__main__":
    main()
