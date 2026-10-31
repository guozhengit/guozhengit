#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自托管 GitHub 统计卡生成器（替代 github-readme-stats.vercel.app 公共实例）。
在 GitHub Actions 中运行，读取 env GITHUB_TOKEN / USERNAME，
产出 assets/stats-{dark,light}.svg 与 assets/langs-{dark,light}.svg。
数据源: GitHub GraphQL(贡献数) + REST(仓库/星标/语言字节)，无任何第三方服务。
"""
import json, os, urllib.request

TOKEN = os.environ["GITHUB_TOKEN"]
USER = os.environ.get("USERNAME", "guozhengit")
OUT = "assets"

THEMES = {
    "dark":  dict(bg="#0e100f", border="#303731", grid="#303731", text="#f1f3ed",
                  muted="#a0aaa1", accent="#c2ef82"),
    "light": dict(bg="#fbfbf8", border="#d8dbd2", grid="#e3e6de", text="#1c1e1c",
                  muted="#6b7268", accent="#4d7c1e"),
}
FONT = "Segoe UI,Microsoft YaHei,PingFang SC,sans-serif"

def api(url):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "profile-stats",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def gql(query):
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"Bearer {TOKEN}", "User-Agent": "profile-stats",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def svg(w, h, t, rid, title, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="{rid}" font-family="{FONT}">'
            f'<title id="{rid}">{esc(title)}</title>'
            f'<defs><pattern id="{rid}-g" width="24" height="24" patternUnits="userSpaceOnUse">'
            f'<circle cx="1" cy="1" r=".7" fill="{t["grid"]}"/></pattern></defs>'
            f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="10" fill="{t["bg"]}" stroke="{t["border"]}"/>'
            f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="10" fill="url(#{rid}-g)"/>' + body + '</svg>')

def fetch_data():
    u = api(f"https://api.github.com/users/{USER}")
    data = {"followers": u["followers"], "public_repos": u["public_repos"]}

    repos = []
    page = 1
    while True:
        batch = api(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner&page={page}")
        repos += batch
        if len(batch) < 100:
            break
        page += 1
    own = [r for r in repos if not r["fork"]]
    data["stars"] = sum(r["stargazers_count"] for r in own)
    data["forks"] = sum(r["forks_count"] for r in own)

    langs = {}
    for r in own[:40]:
        try:
            for name, byt in api(r["languages_url"]).items():
                langs[name] = langs.get(name, 0) + byt
        except Exception:
            pass
    data["langs"] = sorted(langs.items(), key=lambda x: -x[1])[:5]

    try:
        res = gql(f'query{{user(login:"{USER}"){{contributionsCollection{{contributionCalendar{{totalContributions}}}}}}}}')
        data["contribs"] = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    except Exception:
        data["contribs"] = None
    return data

def gen_stats(d):
    metrics = [("FOLLOWERS", d["followers"]), ("STARS", d["stars"]),
               ("FORKS", d["forks"]), ("REPOS", d["public_repos"])]
    if d["contribs"] is not None:
        metrics.append(("CONTRIBS 1Y", d["contribs"]))
    n = len(metrics)
    W, H = 960, 170
    for mode, t in THEMES.items():
        body = (f'<text x="40" y="42" fill="{t["muted"]}" font-size="13" letter-spacing="2">'
                f'GUOZHENGIT / GITHUB / {d["public_repos"]} PUBLIC REPOS</text>')
        cw = (W - 80) / n
        for i, (label, val) in enumerate(metrics):
            x = 40 + i * cw
            body += f'<text x="{x}" y="102" fill="{t["accent"]}" font-size="40" font-weight="700">{val}</text>'
            body += f'<text x="{x}" y="132" fill="{t["muted"]}" font-size="12" letter-spacing="1.5">{label}</text>'
            if i:
                body += f'<path d="M{x-16} 62V138" stroke="{t["border"]}"/>'
        with open(f"{OUT}/stats-{mode}.svg", "w", encoding="utf-8") as f:
            f.write(svg(W, H, t, f"stats-{mode}", "GitHub 统计", body))

def gen_langs(d):
    total = sum(v for _, v in d["langs"]) or 1
    top = 5
    W, H = 960, 90 + top * 34
    for mode, t in THEMES.items():
        body = (f'<text x="40" y="42" fill="{t["muted"]}" font-size="13" letter-spacing="2">'
                f'TOP LANGUAGES / BY BYTES ACROSS OWNED REPOS</text>')
        y = 78
        maxv = d["langs"][0][1] if d["langs"] else 1
        for name, byt in d["langs"][:top]:
            pct = byt / total * 100
            bw = (byt / maxv) * 620
            body += f'<text x="40" y="{y+16}" fill="{t["text"]}" font-size="15" font-weight="600" width="160">{esc(name)}</text>'
            body += f'<rect x="220" y="{y+4}" height="14" width="620" rx="4" fill="{t["grid"]}"/>'
            body += f'<rect x="220" y="{y+4}" height="14" width="{max(bw,8):.0f}" rx="4" fill="{t["accent"]}"/>'
            body += f'<text x="916" y="{y+16}" fill="{t["muted"]}" font-size="13" text-anchor="end">{pct:.1f}%</text>'
            y += 34
        with open(f"{OUT}/langs-{mode}.svg", "w", encoding="utf-8") as f:
            f.write(svg(W, H, t, f"langs-{mode}", "Top languages", body))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    d = fetch_data()
    print("数据:", {k: (v if k != 'langs' else [n for n, _ in v]) for k, v in d.items()})
    gen_stats(d)
    gen_langs(d)
    print("已生成 assets/stats-*.svg 与 assets/langs-*.svg")
