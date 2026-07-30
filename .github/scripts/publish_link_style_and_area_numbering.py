from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "index.html"
DATABASE = ROOT / "data" / "master-database.json"
PUBLISHED_AT = "2026-07-30T11:15:00+08:00"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)


html = INDEX.read_text(encoding="utf-8")

# Otaru hierarchy links: use the same inline arrow style as the other area cards.
old_css = '.hierarchy-name-row{display:flex;align-items:center;justify-content:space-between;gap:10px}\n'
new_css = '.hierarchy-name-row{display:flex;align-items:center;gap:10px}\n'
if old_css in html:
    html = replace_once(html, old_css, new_css, "hierarchy name row CSS")
elif new_css not in html:
    raise RuntimeError("hierarchy name row CSS not found")

numbered_css_anchor = '.hierarchy-badge{display:inline-flex;padding:3px 8px;border-radius:999px;background:#f0edf7;color:#705791;font-size:11px;font-weight:850;margin-bottom:5px}\n'
numbered_css = '''.numbered-area{counter-reset:area-place}\n.numbered-area .shop{position:relative;padding-left:38px}\n.numbered-area .shop::before{counter-increment:area-place;content:counter(area-place);position:absolute;left:0;top:11px;display:grid;place-items:center;width:25px;height:25px;border-radius:50%;background:var(--blue-soft);color:var(--blue);font-size:12px;font-weight:900}\n'''
if '.numbered-area{counter-reset:area-place}' not in html:
    html = replace_once(html, numbered_css_anchor, numbered_css_anchor + numbered_css, "numbered area CSS")

old_burger_link = '<div class="hierarchy-name-row"><a class="hierarchy-name" href="${option[3]}" target="_blank" rel="noopener">${option[0]}</a><a class="hierarchy-map" href="${option[3]}" target="_blank" rel="noopener" aria-label="在 Google Maps 開啟 ${option[0]}">📍</a></div>'
new_burger_link = '<div class="hierarchy-name-row"><a class="hierarchy-name" href="${option[3]}" target="_blank" rel="noopener">${option[0]} ↗</a></div>'
if old_burger_link in html:
    html = replace_once(html, old_burger_link, new_burger_link, "hierarchy burger link")
elif new_burger_link not in html:
    raise RuntimeError("hierarchy burger link not found")

old_place_link = '<div class="hierarchy-name-row"><a class="hierarchy-name" href="${shop[4]}" target="_blank" rel="noopener">${shop[1]}</a><a class="hierarchy-map" href="${shop[4]}" target="_blank" rel="noopener" aria-label="在 Google Maps 開啟 ${shop[1]}">📍</a></div>'
new_place_link = '<div class="hierarchy-name-row"><a class="hierarchy-name" href="${shop[4]}" target="_blank" rel="noopener">${shop[1]} ↗</a></div>'
if old_place_link in html:
    html = replace_once(html, old_place_link, new_place_link, "hierarchy place link")
elif new_place_link not in html:
    raise RuntimeError("hierarchy place link not found")

# Number the five Toyako stops automatically, without hard-coding numbers in place data.
old_toyako = '''      {
        title:"洞爺湖",
        note:"",
        shops:['''
new_toyako = '''      {
        title:"洞爺湖",
        note:"",
        numbered:true,
        shops:['''
if old_toyako in html:
    html = replace_once(html, old_toyako, new_toyako, "Toyako numbered flag")
elif 'title:"洞爺湖",\n        note:"",\n        numbered:true,' not in html:
    raise RuntimeError("Toyako area not found")

old_generic = '''    const groupClass=/晚餐/.test(a.title)?"group-meal":/晚間採買/.test(a.title)?"group-essentials":/藥妝|藥局/.test(a.title)?"group-pharmacy":/便利商店/.test(a.title)?"group-convenience":/大型採買/.test(a.title)?"group-shopping":/冰品/.test(a.title)?"group-dessert":"";
    return `
    <details class="area-card ${groupClass}">'''
new_generic = '''    const groupClass=/晚餐/.test(a.title)?"group-meal":/晚間採買/.test(a.title)?"group-essentials":/藥妝|藥局/.test(a.title)?"group-pharmacy":/便利商店/.test(a.title)?"group-convenience":/大型採買/.test(a.title)?"group-shopping":/冰品/.test(a.title)?"group-dessert":"";
    const numberedClass=a.numbered?" numbered-area":"";
    return `
    <details class="area-card ${groupClass}${numberedClass}">'''
if old_generic in html:
    html = replace_once(html, old_generic, new_generic, "generic area numbered class")
elif 'const numberedClass=a.numbered?" numbered-area":"";' not in html:
    raise RuntimeError("generic area renderer not found")

html = re.sub(
    r'<!-- pages-redeploy:[^>]*-->',
    '<!-- pages-redeploy:2026-07-30T11:15+08:00 -->',
    html,
    count=1,
)

required = [
    '${option[0]} ↗',
    '${shop[1]} ↗',
    'numbered:true',
    'numbered-area',
    'counter(area-place)',
]
for value in required:
    if value not in html:
        raise RuntimeError(f"missing published value: {value}")

INDEX.write_text(html, encoding="utf-8")

with DATABASE.open("r", encoding="utf-8") as fh:
    database = json.load(fh)

database["updatedAt"] = PUBLISHED_AT
project = database["projects"]["2026-hokkaido"]
changes = project.setdefault("pendingUiChanges", [])
change_id = "area-link-style-and-toyako-auto-numbering"
existing = next((item for item in changes if item.get("id") == change_id), None)
change_record = {
    "id": change_id,
    "scope": "Day 3／今日會經過的區域",
    "status": "published",
    "websitePublished": True,
    "publishedAt": PUBLISHED_AT,
    "changes": [
        "小樽階層資訊的 Google Maps 連結由右側方形圖釘改為店名後方的 ↗ 內嵌連結",
        "洞爺湖區域的五個停留點以 CSS 自動編號顯示，不在資料內容中寫死序號",
        "保留原有地點順序與內容"
    ]
}
if existing:
    existing.clear()
    existing.update(change_record)
else:
    changes.append(change_record)

database.setdefault("changeLog", []).append({
    "date": "2026-07-30",
    "projectId": "2026-hokkaido",
    "scope": "Day 3 區域資訊連結與編號",
    "changes": change_record["changes"],
    "websitePublished": True,
    "publishedAt": PUBLISHED_AT
})

with DATABASE.open("w", encoding="utf-8", newline="\n") as fh:
    json.dump(database, fh, ensure_ascii=False, indent=2)
    fh.write("\n")

print("Inline map links and Toyako automatic numbering published.")
