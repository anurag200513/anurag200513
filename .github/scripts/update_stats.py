#!/usr/bin/env python3
"""Auto-update assets/radar-telemetry.svg weekly via GitHub GraphQL (Blue & Green theme)."""
import json, math, os, urllib.request
from pathlib import Path

LOGIN = os.environ.get("TARGET_USER", "anurag200513")
TOKEN = os.environ["GH_TOKEN"]
QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    pullRequests { totalCount }
    contributionsCollection { contributionCalendar { totalContributions } }
    repositories(first: 50, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      totalCount
      nodes {
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""
req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
    headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json", "User-Agent": "radar-updater"},
)
user = json.loads(urllib.request.urlopen(req).read().decode())["data"]["user"]
repos = user["repositories"]["nodes"]
lb = {}
for r in repos:
    for e in r["languages"]["edges"]:
        n, c = e["node"]["name"], (e["node"]["color"] or "#38bdf8")
        lb[n] = (lb.get(n, (0, c))[0] + e["size"], c)
tot = sum(v[0] for v in lb.values()) or 1
top = sorted([(k, v[0], v[0] * 100.0 / tot, v[1]) for k, v in lb.items()], key=lambda x: x[1], reverse=True)[:4]

cx, cy, max_r = 200.0, 138.0, 70.0
axes = [("JavaScript",0.90,-90),("HTML / CSS",0.88,-30),("Python APIs",0.82,30),("Git &amp; Collab",0.88,90),("Prototyping",0.84,150),("UI Craft",0.85,210)]
pt = lambda r, d: (cx + r * math.cos(math.radians(d)), cy + r * math.sin(math.radians(d)))
rings = [f'<polygon points="{" ".join(f"{pt(max_r*f,a[2])[0]:.1f},{pt(max_r*f,a[2])[1]:.1f}" for a in axes)}" fill="none" stroke="#163547" stroke-width="1"/>' for f in (0.33,0.66,1.0)]
spokes, labels, dpts, dots = [], [], [], []
for n, v, d in axes:
    ox, oy = pt(max_r, d); spokes.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{ox:.1f}" y2="{oy:.1f}" stroke="#163547" stroke-width="1"/>')
    dx, dy = pt(max_r*v, d); dpts.append(f"{dx:.1f},{dy:.1f}"); dots.append(f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="4" fill="#34d399" stroke="#07131e" stroke-width="1.5"/>')
    lx, ly = pt(max_r+18, d)
    anc = "middle" if d in (-90,90) else ("start" if -89<d<89 else "end")
    ly += (-2 if d==-90 else (10 if d==90 else 4))
    labels.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anc}" fill="#bae6fd" font-family="Segoe UI, Ubuntu, sans-serif" font-size="11.5" font-weight="600">{n}</text>')

bx, bw, cur = 26, 348, 26.0
segs, leg = [], []
for i, (n, _s, p, c) in enumerate(top):
    sw = (bx+bw)-cur if i==len(top)-1 else bw*(p/100.0)
    segs.append(f'<rect x="{cur:.1f}" y="314" width="{max(sw,2.0):.1f}" height="10" fill="{c}"/>'); cur += sw
    tx, ty = 26+(i%2)*182, 346+(i//2)*22
    leg.append(f'<circle cx="{tx+5}" cy="{ty-4}" r="4.5" fill="{c}"/><text x="{tx+15}" y="{ty}" fill="#e0f2fe" font-family="Segoe UI, sans-serif" font-size="11.5" font-weight="600">{n}</text><text x="{tx+162}" y="{ty}" text-anchor="end" fill="#94a3b8" font-family="Consolas, monospace" font-size="11">{p:.1f}%</text>')

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="390" viewBox="0 0 400 390" role="img" aria-label="Skill Radar and GitHub Metrics">
  <defs><linearGradient id="radFill" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#0ea5e9" stop-opacity="0.42"/><stop offset="100%" stop-color="#10b981" stop-opacity="0.38"/></linearGradient><clipPath id="u2BarClip"><rect x="26" y="314" width="348" height="10" rx="5"/></clipPath></defs>
  <rect x="2" y="2" width="396" height="386" rx="16" fill="#07131e" stroke="#163a4a" stroke-width="1.4"/>
  <text x="24" y="32" fill="#f0f9ff" font-family="Segoe UI, Ubuntu, sans-serif" font-size="14.5" font-weight="700">✦ Stack Radar &amp; Snapshot</text>
  <text x="374" y="32" text-anchor="end" fill="#34d399" font-family="Consolas, monospace" font-size="10.5" font-weight="700">SINCE {user['createdAt'][:4]}</text>
  {"".join(rings)}{"".join(spokes)}<polygon points="{' '.join(dpts)}" fill="url(#radFill)" stroke="#10b981" stroke-width="2"/>{"".join(dots)}{"".join(labels)}
  <line x1="24" y1="254" x2="376" y2="254" stroke="#153243" stroke-width="1"/>
  <rect x="24" y="266" width="80" height="36" rx="8" fill="#0c2030"/><text x="64" y="281" text-anchor="middle" fill="#94a3b8" font-family="Consolas, monospace" font-size="9">REPOS</text><text x="64" y="296" text-anchor="middle" fill="#38bdf8" font-family="Consolas, monospace" font-size="14" font-weight="700">{user['repositories']['totalCount']}</text>
  <rect x="114" y="266" width="84" height="36" rx="8" fill="#0c2030"/><text x="156" y="281" text-anchor="middle" fill="#94a3b8" font-family="Consolas, monospace" font-size="9">CONTRIBS</text><text x="156" y="296" text-anchor="middle" fill="#34d399" font-family="Consolas, monospace" font-size="14" font-weight="700">{user['contributionsCollection']['contributionCalendar']['totalContributions']}</text>
  <rect x="208" y="266" width="76" height="36" rx="8" fill="#0c2030"/><text x="246" y="281" text-anchor="middle" fill="#94a3b8" font-family="Consolas, monospace" font-size="9">PRs</text><text x="246" y="296" text-anchor="middle" fill="#0ea5e9" font-family="Consolas, monospace" font-size="14" font-weight="700">{user['pullRequests']['totalCount']}</text>
  <rect x="294" y="266" width="82" height="36" rx="8" fill="#0c2030"/><text x="335" y="281" text-anchor="middle" fill="#94a3b8" font-family="Consolas, monospace" font-size="9">GALAXY</text><text x="335" y="296" text-anchor="middle" fill="#6ee7b7" font-family="Consolas, monospace" font-size="14" font-weight="700">x4 Gold</text>
  <rect x="26" y="314" width="348" height="10" rx="5" fill="#102938"/><g clip-path="url(#u2BarClip)">{"".join(segs)}</g>{"".join(leg)}
</svg>"""
Path("assets/radar-telemetry.svg").write_text(svg, encoding="utf-8")
