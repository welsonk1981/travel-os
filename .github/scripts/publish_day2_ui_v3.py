from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "index.html"
DATABASE = ROOT / "data" / "master-database.json"
PUBLISHED_AT = "2026-07-30T08:08:00+08:00"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)


html = INDEX.read_text(encoding="utf-8")

# 1. Add compact and hierarchy UI styles once.
if ".compact-place-card{" not in html:
    css_anchor = ".walk-shop-map{display:inline-grid;flex:0 0 auto;place-items:center;width:25px;height:25px;border:1px solid #b9cad7;border-radius:8px;background:#f5f9fc;text-decoration:none;font-size:14px;line-height:1}\n"
    css_addition = r'''.walk-shop-actions{display:flex;align-items:center;gap:7px;margin-left:auto}
.walk-shop-parking{display:inline-grid;flex:0 0 auto;place-items:center;width:25px;height:25px;border:1px solid #c8b98c;border-radius:8px;background:#fffaf0;text-decoration:none;font-size:14px;line-height:1}
.compact-place-card{margin-top:10px;padding:14px 15px;border:1px solid #dce4ea;border-left:4px solid #8469aa;border-radius:15px;background:#fff}
.compact-place-head{display:flex;align-items:center;justify-content:space-between;gap:12px}
.compact-place-name{color:#1769aa;font-size:17px;font-weight:900;line-height:1.35}
.compact-place-meta{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-top:6px;color:#5f6972;font-size:13px;font-weight:800}
.compact-place-hours{color:#66717a;font-weight:700}
.hierarchy-area{border:1px solid var(--line);border-radius:16px;padding:13px;margin-top:9px}
.hierarchy-area>summary{cursor:pointer;font-weight:800}
.hierarchy-list{padding-top:6px}
.hierarchy-group{padding:15px 0;border-bottom:1px solid #edf0f2}
.hierarchy-group:last-child{border-bottom:0;padding-bottom:2px}
.hierarchy-category{display:inline-flex;align-items:center;padding:3px 8px;border-radius:999px;background:#edf2f6;color:#677580;font-size:11px;font-weight:850}
.hierarchy-place{margin-top:7px}
.hierarchy-name-row{display:flex;align-items:center;justify-content:space-between;gap:10px}
.hierarchy-name{color:#1769aa;text-decoration:none;font-size:17px;font-weight:900;line-height:1.35}
.hierarchy-map{display:inline-grid;place-items:center;flex:0 0 auto;width:28px;height:28px;border:1px solid #b9cad7;border-radius:8px;background:#f5f9fc;text-decoration:none;font-size:14px}
.hierarchy-summary{margin-top:4px;color:#68737d;font-size:14px;line-height:1.45;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.hierarchy-hours{margin-top:6px;color:#505a65;font-size:13px;font-weight:750}
.hierarchy-choice-title{margin-top:7px;color:#334b5d;font-size:16px;font-weight:900}
.hierarchy-choice{padding:11px 0;border-top:1px dashed #e1e5e8}
.hierarchy-choice:first-of-type{border-top:0;padding-top:8px}
.hierarchy-badge{display:inline-flex;padding:3px 8px;border-radius:999px;background:#f0edf7;color:#705791;font-size:11px;font-weight:850;margin-bottom:5px}
'''
    html = replace_once(html, css_anchor, css_anchor + css_addition, "UI CSS anchor")

# 2. Add parking place to page-side master locations.
if "sapporoJogaiMarketParking:Object.freeze" not in html:
    parking_anchor = '''  marusanMikamiMarusantei:Object.freeze({
    id:"marusan-mikami-marusan-tei",
    name:"㈱マルサン三上商店／まるさん亭 本店",
    mapUrl:"https://maps.app.goo.gl/9ojJpxLfgaYLS4se9",
    hours:"07:00–15:00"
  }),
'''
    parking_addition = '''  sapporoJogaiMarketParking:Object.freeze({
    id:"sapporo-jogai-market-parking",
    name:"札幌場外市場 共用免費停車場",
    mapUrl:"https://www.google.com/maps/search/?api=1&query=札幌場外市場+駐車場",
    hours:""
  }),
'''
    html = replace_once(html, parking_anchor, parking_anchor + parking_addition, "parking master location")

# 3. Add the parking button to the Marusan row.
old_marusan_row = '["●",masterLocations.marusanMikamiMarusantei.name,"",masterLocations.marusanMikamiMarusantei.hours,masterLocations.marusanMikamiMarusantei.mapUrl,""]'
new_marusan_row = '["●",masterLocations.marusanMikamiMarusantei.name,"",masterLocations.marusanMikamiMarusantei.hours,masterLocations.marusanMikamiMarusantei.mapUrl,"",masterLocations.sapporoJogaiMarketParking.mapUrl]'
if old_marusan_row in html:
    html = replace_once(html, old_marusan_row, new_marusan_row, "Marusan parking row")
elif new_marusan_row not in html:
    raise RuntimeError("Marusan row not found")

# 4. Convert Head Buddha to a compact single card.
old_buddha = '''      {
        title:"頭大佛",
        layout:"place-guide",
        shops:[
          ["1",masterLocations.hillOfBuddha.name,"11:30–12:25","",masterLocations.hillOfBuddha.mapUrl,"開放時間 09:00–16:00"]
        ]
      },'''
new_buddha = '''      {
        title:"頭大佛",
        layout:"compact-place",
        shops:[
          ["",masterLocations.hillOfBuddha.name,"11:30–12:25","",masterLocations.hillOfBuddha.mapUrl,"開放時間 09:00–16:00"]
        ]
      },'''
if old_buddha in html:
    html = replace_once(html, old_buddha, new_buddha, "Head Buddha data layout")
elif 'layout:"compact-place"' not in html:
    raise RuntimeError("Head Buddha area not found")

# 5. Keep Day 3 Otaru order but apply hierarchical rendering.
otaru_anchor = '''      {
        title:"小樽",
        note:"住宿停車後步行；12:30 整理完成並退房",
        shops:['''
otaru_replacement = '''      {
        title:"小樽",
        note:"住宿停車後步行；12:30 整理完成並退房",
        layout:"hierarchy",
        shops:['''
if otaru_anchor in html:
    html = replace_once(html, otaru_anchor, otaru_replacement, "Day 3 Otaru hierarchy")
elif 'title:"小樽",\n        note:"住宿停車後步行；12:30 整理完成並退房",\n        layout:"hierarchy"' not in html:
    raise RuntimeError("Day 3 Otaru area not found")

# 6. Add custom render branches and parking action.
compact_branch_anchor = '''    if(a.layout==="place-guide"){
'''
compact_branch = '''    if(a.layout==="compact-place"){
      const shop=a.shops[0];
      return `<article class="compact-place-card">
        <div class="compact-place-head">
          <div>
            <div class="compact-place-name">${shop[1]}</div>
            <div class="compact-place-meta"><span>🕐 ${shop[2]}</span>${shop[5]?`<span class="compact-place-hours">${shop[5]}</span>`:""}</div>
          </div>
          <a class="place-guide-link" href="${shop[4]}" target="_blank" rel="noopener" aria-label="在 Google Maps 開啟 ${shop[1]}" title="在 Google Maps 開啟">📍</a>
        </div>
      </article>`;
    }
    if(a.layout==="hierarchy"){
      return `<details class="hierarchy-area">
        <summary>${a.title}</summary>
        <div class="hierarchy-list">
          ${a.shops.map(shop=>{
            if(shop[0]==="__BURGER__"){
              return `<section class="hierarchy-group">
                <div class="hierarchy-category">漢堡</div>
                <div class="hierarchy-choice-title">${shop[1]}</div>
                ${shop[2].map((option,index)=>`<article class="hierarchy-choice">
                  <div class="hierarchy-badge">${index===0?"主選":"備選"}</div>
                  <div class="hierarchy-name-row"><a class="hierarchy-name" href="${option[3]}" target="_blank" rel="noopener">${option[0]}</a><a class="hierarchy-map" href="${option[3]}" target="_blank" rel="noopener" aria-label="在 Google Maps 開啟 ${option[0]}">📍</a></div>
                  <div class="hierarchy-summary">${option[1].replace(/^(主選|備選)：/,"")}</div>
                  <div class="hierarchy-hours">🕘 ${option[2]}</div>
                </article>`).join("")}
              </section>`;
            }
            return `<section class="hierarchy-group">
              <div class="hierarchy-category">${shop[0]}</div>
              <article class="hierarchy-place">
                <div class="hierarchy-name-row"><a class="hierarchy-name" href="${shop[4]}" target="_blank" rel="noopener">${shop[1]}</a><a class="hierarchy-map" href="${shop[4]}" target="_blank" rel="noopener" aria-label="在 Google Maps 開啟 ${shop[1]}">📍</a></div>
                ${shop[2]?`<div class="hierarchy-summary">${shortText(shop[2])}</div>`:""}
                ${shop[3]?`<div class="hierarchy-hours">🕘 ${shop[3]}</div>`:""}
              </article>
            </section>`;
          }).join("")}
        </div>
      </details>`;
    }
    if(a.layout==="place-guide"){
'''
if 'if(a.layout==="compact-place")' not in html:
    html = replace_once(html, compact_branch_anchor, compact_branch, "custom layout render branches")

old_walk_branch = '''    if(a.layout==="walking-guide"){
      return `<details class="area-card">
        <summary>${a.title}</summary>
        <section class="walk-guide">
        <div class="walk-guide-note">${a.note}</div>
        ${a.shops.map(shop=>`<article class="walk-shop">
          <div class="walk-shop-name"><span>${shop[0]} ${shop[1]}</span><a class="walk-shop-map" href="${shop[4]}" target="_blank" rel="noopener" aria-label="在 Google Maps 開啟 ${shop[1]}">📍</a></div>
          <div class="walk-shop-desc">${shop[5]?`<span class="walk-shop-tag">${shop[5]}</span>`:""}<span class="walk-shop-desc-text">${shop[2]}</span></div>
          ${shop[3]?`<div class="walk-shop-meta"><div class="walk-shop-hours">🕘 ${shop[3]}</div></div>`:""}
        </article>`).join("")}
        </section>
      </details>`;
    }
'''
new_walk_branch = '''    if(a.layout==="walking-guide"){
      return `<details class="area-card">
        <summary>${a.title}</summary>
        <section class="walk-guide">
        <div class="walk-guide-note">${a.note}</div>
        ${a.shops.map(shop=>`<article class="walk-shop">
          <div class="walk-shop-name"><span>${shop[0]} ${shop[1]}</span><span class="walk-shop-actions"><a class="walk-shop-map" href="${shop[4]}" target="_blank" rel="noopener" aria-label="在 Google Maps 開啟 ${shop[1]}" title="店家定位">📍</a>${shop[6]?`<a class="walk-shop-parking" href="${shop[6]}" target="_blank" rel="noopener" aria-label="開啟 ${shop[1]} 停車場定位" title="停車場定位">🅿️</a>`:""}</span></div>
          <div class="walk-shop-desc">${shop[5]?`<span class="walk-shop-tag">${shop[5]}</span>`:""}<span class="walk-shop-desc-text">${shop[2]}</span></div>
          ${shop[3]?`<div class="walk-shop-meta"><div class="walk-shop-hours">🕘 ${shop[3]}</div></div>`:""}
        </article>`).join("")}
        </section>
      </details>`;
    }
'''
if old_walk_branch in html:
    html = replace_once(html, old_walk_branch, new_walk_branch, "walking guide parking render")
elif 'walk-shop-parking' not in html:
    raise RuntimeError("walking-guide renderer not found")

# Keep the area heading visible because custom compact cards no longer provide a duplicate title.
html = html.replace(
    '${orderedAreas.some(a=>a.layout==="place-guide")?"":`<h3 style="margin:14px 0 2px">今日會經過的區域</h3>`}',
    '<h3 style="margin:14px 0 2px">今日會經過的區域</h3>',
)

html = re.sub(
    r'<!-- pages-redeploy:[^>]*-->',
    '<!-- pages-redeploy:2026-07-30T08:08+08:00 -->',
    html,
    count=1,
)

required = [
    'class="walk-shop-parking"',
    'layout:"compact-place"',
    'layout:"hierarchy"',
    'class="compact-place-card"',
    'class="hierarchy-category"',
    '札幌場外市場 共用免費停車場',
]
for value in required:
    if value not in html:
        raise RuntimeError(f"missing published value: {value}")

INDEX.write_text(html, encoding="utf-8")

# Update Master Database publication status.
with DATABASE.open("r", encoding="utf-8") as fh:
    database = json.load(fh)

database["updatedAt"] = PUBLISHED_AT
project = database["projects"]["2026-hokkaido"]
for item in project.get("pendingUiChanges", []):
    if item.get("id") == "otaru-area-information-hierarchy":
        item["status"] = "published"
        item["websitePublished"] = True
        item["publishedAt"] = PUBLISHED_AT

for entry in database.get("changeLog", []):
    if entry.get("scope") in {"Day 2 顯示與停車資料", "小樽區域資訊欄排版"}:
        entry["websitePublished"] = True
        entry["publishedAt"] = PUBLISHED_AT

with DATABASE.open("w", encoding="utf-8", newline="\n") as fh:
    json.dump(database, fh, ensure_ascii=False, indent=2)
    fh.write("\n")

print("Day 2 parking, Head Buddha compact card, and Otaru hierarchy published.")
