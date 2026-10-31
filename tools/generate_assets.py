#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
guozhengit GitHub profile 资产生成器
生成 assets/ 下的 roles / work-card / toolbox 系列 SVG（明暗双主题）。
用法: python tools/generate_assets.py   （在仓库根目录执行）
"""
import os

OUT = "assets"

# ---------- 主题 ----------
DARK = dict(bg="#0e100f", border="#303731", grid="#303731", text="#f1f3ed",
            muted="#a0aaa1", accent="#c2ef82", chip="#161916")
LIGHT = dict(bg="#fbfbf8", border="#d8dbd2", grid="#e3e6de", text="#1c1e1c",
             muted="#6b7268", accent="#4d7c1e", chip="#f1f3ec")

FONT = "Segoe UI,Microsoft YaHei,PingFang SC,sans-serif"

def cjk_w(s, size):
    """粗略估算文本宽度: CJK ≈ 1.0×size, 其他 ≈ 0.55×size"""
    return sum(size if ord(c) > 0x2E80 else size * 0.55 for c in s)

def svg_open(w, h, theme, title, desc, rid):
    t = theme
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="{rid}" font-family="{FONT}">'
            f'<title id="{rid}">{title}</title><desc id="{rid}-d">{desc}</desc>'
            f'<defs><pattern id="{rid}-grid" width="24" height="24" patternUnits="userSpaceOnUse">'
            f'<circle cx="1" cy="1" r=".7" fill="{t["grid"]}"/></pattern></defs>'
            f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="10" fill="{t["bg"]}" stroke="{t["border"]}"/>'
            f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="10" fill="url(#{rid}-grid)"/>')

def save(name, content):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  ✓", path)

# ---------- 1. 角色三连徽章 ----------
ROLES = [
    ("Java 后端 · 8 YEARS", "PRIMARY"),
    ("支付 / 清结算 / 电子签约", "BUSINESS"),
    ("AI Ops · Agent 工程", "EXPLORING"),
]

def gen_roles(rid_suffix):
    for mode, t in (("dark", DARK), ("light", LIGHT)):
        rid = f"roles-{mode}{rid_suffix}"
        H = 64
        parts = [svg_open(960, H, t, "郭永争的技术定位",
                          "Java 后端 8 年；支付、清结算、电子签约业务；AI Ops 与 Agent 工程", rid)]
        x = 0
        for label, tag in ROLES:
            w = cjk_w(label, 20) + 72
            parts.append(f'<rect x="{x+1}" y="1" width="{w-2}" height="{H-2}" rx="10" '
                         f'fill="{t["chip"]}" stroke="{t["border"]}"/>')
            parts.append(f'<circle cx="{x+26}" cy="{H//2}" r="4" fill="{t["accent"]}"/>')
            parts.append(f'<text x="{x+42}" y="{H//2+7}" fill="{t["text"]}" font-size="20" '
                         f'font-weight="600">{label}</text>')
            parts.append(f'<text x="{x+w-14}" y="{H//2+5}" fill="{t["muted"]}" font-size="9" '
                         f'text-anchor="end" letter-spacing="1">{tag}</text>')
            x += w + 14
        parts.append("</svg>")
        save(f"roles-{mode}.svg", "".join(parts))

# ---------- 2. 作品卡片 ----------
WORKS = [
    ("interview", "01 / WEBSITE · 知识工程", "Java → AI Agent 知识库",
     "流程图、时序图与源码分析，串起 Java 后端、分布式系统与 Agent 工程",
     "interview.sageflow.online",
     "专题文档 · 工程图解 · 运行时安全 · LLM 可观测性"),
    ("train", "02 / WEBSITE · 在线应用", "面试训练中心",
     "机试题、口述题、项目答辩训练台，带题库检索与答题记录",
     "train.sageflow.online",
     "按训练类型组织 · 错题复习 · 从阅读到动手"),
    ("resume", "03 / WEBSITE · 职业经历", "在线简历与项目经历",
     "电子签约、支付清结算、AI 签约助手等项目背景与本人职责",
     "resume.sageflow.online",
     "工作经历 · 企业项目 · 在线阅读 / 导出 PDF"),
]

def gen_works(rid_suffix):
    for key, kicker, title, desc, host, extra in WORKS:
        for mode, t in (("dark", DARK), ("light", LIGHT)):
            rid = f"work-{key}-{mode}{rid_suffix}"
            W, H = 960, 190
            p = [svg_open(W, H, t, title, f"{kicker} {desc} {host}", rid)]
            # 左侧强调条
            p.append(f'<rect x="1" y="14" width="5" height="{H-28}" rx="2" fill="{t["accent"]}"/>')
            p.append(f'<text x="44" y="44" fill="{t["muted"]}" font-size="13" '
                     f'letter-spacing="2">{kicker}</text>')
            p.append(f'<text x="44" y="86" fill="{t["text"]}" font-size="30" font-weight="700">'
                     f'{title} <tspan fill="{t["accent"]}">↗</tspan></text>')
            p.append(f'<text x="44" y="122" fill="{t["muted"]}" font-size="16">{desc}</text>')
            p.append(f'<text x="44" y="152" fill="{t["accent"]}" font-size="13" opacity=".85">{extra}</text>')
            p.append(f'<path d="M44 166H916" stroke="{t["border"]}"/>')
            p.append(f'<text x="916" y="166" dy="-8" fill="{t["muted"]}" font-size="13" '
                     f'text-anchor="end">{host}</text>')
            p.append("</svg>")
            save(f"work-{key}-{mode}.svg", "".join(p))

if __name__ == "__main__":
    print("生成 profile SVG 资产…")
    gen_roles("")
    gen_works("")
    print("完成。")
