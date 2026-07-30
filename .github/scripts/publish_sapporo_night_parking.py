from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "index.html"
DATABASE = ROOT / "data" / "master-database.json"
PUBLISHED_AT = "2026-07-30T10:08:00+08:00"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)


html = INDEX.read_text(encoding="utf-8")

old_sapporo_night = '''      {
        title:"札幌晚上",
        note:"先沿狸小路採買，再依序前往兩家消夜。",
        shops:[
          ["備選","BicCamera Select 札幌狸小路店","補行動電源、充電線、轉接頭、記憶卡與旅行小電器。","10:00–23:00","https://www.google.com/maps/search/?api=1&query=ビックカメラ+Select+札幌狸小路店","🛍️ 採買",null,"狸小路5丁目"],
          ["必去","TNOC THE STORE SAPPORO T4","買北海道主題 T-shirt、帽子、外套、包袋與生活雜貨。","10:00–21:00","https://www.google.com/maps/search/?api=1&query=TNOC+THE+STORE+SAPPORO+T4","🛍️ 採買",null,"狸小路4丁目"],
          ["第一站","海味はちきょう別亭 おやじ","北海道海鮮居酒屋。","依當日營業時間","https://maps.app.goo.gl/QBdXeb7Gv2NY18vLA?g_st=il","🌙 消夜",null,"南3條西3丁目"],
          ["第二站","迴轉壽司 根室花丸 COCONO SUSUKINO店","根室海鮮握壽司、花咲蟹與當日推薦品項。","依當日營業時間","https://maps.app.goo.gl/J65RA13a5K1ozkZF7?g_st=il","🌙 消夜",null,"南4條西4丁目"]
        ]
      }'''

new_sapporo_night = '''      {
        title:"札幌晚上",
        note:"先選平面停車場，再沿狸小路採買並依序前往兩家宵夜。",
        shops:[
          ["首選","Parking（南3條西9丁目）","平面停車場；20:00–23:00 預估停車費 ¥800。","20:00–08:00｜30分 ¥300；夜間最高 ¥800；入庫後12小時最高 ¥1,600","https://maps.app.goo.gl/Z1dYJfc6i8WCAitJ6","🅿️ 停車候選",null,"南3條西9丁目"],
          ["備選","遠藤興産㈱ 南３西７パーキング","平面停車場；20:00–23:00 預估停車費 ¥1,400。","24小時｜30分 ¥330；入庫後24小時最高 ¥1,400","https://maps.app.goo.gl/b7qBjfFCpby2eTCA8","🅿️ 停車候選",null,"南3條西7丁目"],
          ["備選","BicCamera Select 札幌狸小路店","補行動電源、充電線、轉接頭、記憶卡與旅行小電器。","10:00–23:00","https://www.google.com/maps/search/?api=1&query=ビックカメラ+Select+札幌狸小路店","🛍️ 採買",null,"狸小路5丁目"],
          ["必去","TNOC THE STORE SAPPORO T4","買北海道主題 T-shirt、帽子、外套、包袋與生活雜貨。","10:00–21:00","https://www.google.com/maps/search/?api=1&query=TNOC+THE+STORE+SAPPORO+T4","🛍️ 採買",null,"狸小路4丁目"],
          ["第一站","海味はちきょう別亭 おやじ","北海道海鮮居酒屋。","18:00–24:00（L.O.23:00）；週日休，週一為國定假日時週日營業","https://maps.app.goo.gl/QBdXeb7Gv2NY18vLA?g_st=il","🌙 宵夜",null,"南3條西3丁目"],
          ["第二站","迴轉壽司 根室花丸 COCONO SUSUKINO店","根室海鮮握壽司、花咲蟹與當日推薦品項。","11:00–21:00（L.O.20:30）","https://maps.app.goo.gl/J65RA13a5K1ozkZF7?g_st=il","🌙 宵夜",null,"南4條西4丁目"]
        ]
      }'''

if old_sapporo_night in html:
    html = replace_once(html, old_sapporo_night, new_sapporo_night, "Sapporo night section")
elif new_sapporo_night not in html:
    raise RuntimeError("Sapporo night section not found")

old_satudora = '["採買","サツドラ小樽堺町店","補防曬、暈車藥、腸胃藥、止痛藥、面膜與旅行消耗品。","營業時間待確認","https://www.google.com/maps/search/?api=1&query=サツドラ小樽堺町店",""]'
new_satudora = '["採買","サツドラ小樽堺町店","補防曬、暈車藥、腸胃藥、止痛藥、面膜與旅行消耗品。","10:30–19:00","https://www.google.com/maps/search/?api=1&query=サツドラ小樽堺町店",""]'
if old_satudora in html:
    html = replace_once(html, old_satudora, new_satudora, "Satudora hours")
elif new_satudora not in html:
    raise RuntimeError("Satudora row not found")

html = re.sub(
    r'<!-- pages-redeploy:[^>]*-->',
    '<!-- pages-redeploy:2026-07-30T10:08+08:00 -->',
    html,
    count=1,
)

required = [
    'Parking（南3條西9丁目）',
    '遠藤興産㈱ 南３西７パーキング',
    '20:00–23:00 預估停車費 ¥800',
    '20:00–23:00 預估停車費 ¥1,400',
    '🌙 宵夜',
    '18:00–24:00（L.O.23:00）',
    '11:00–21:00（L.O.20:30）',
    'サツドラ小樽堺町店","補防曬、暈車藥、腸胃藥、止痛藥、面膜與旅行消耗品。","10:30–19:00',
]
for value in required:
    if value not in html:
        raise RuntimeError(f"missing published value: {value}")

INDEX.write_text(html, encoding="utf-8")

with DATABASE.open("r", encoding="utf-8") as fh:
    database = json.load(fh)

database["databaseVersion"] = "1.5"
database["updatedAt"] = PUBLISHED_AT
project = database["projects"]["2026-hokkaido"]
places = project.setdefault("places", {})

places["sapporo-minami3-nishi9-parking"] = {
    "id": "sapporo-minami3-nishi9-parking",
    "name": "Parking（南3條西9丁目）",
    "mapUrl": "https://maps.app.goo.gl/Z1dYJfc6i8WCAitJ6",
    "type": "平面停車場",
    "hours": "24小時",
    "pricing": {
        "daytime": "08:00–20:00｜30分 ¥300",
        "nighttime": "20:00–08:00｜30分 ¥300",
        "nightMaximumYen": 800,
        "maximum": "入庫後12小時最高 ¥1,600"
    },
    "estimatedParking": {
        "start": "20:00",
        "end": "23:00",
        "durationMinutes": 180,
        "rawYen": 1800,
        "appliedCap": "夜間最高",
        "totalYen": 800
    }
}

places["endo-minami3-nishi7-parking"] = {
    "id": "endo-minami3-nishi7-parking",
    "name": "遠藤興産㈱ 南３西７パーキング",
    "mapUrl": "https://maps.app.goo.gl/b7qBjfFCpby2eTCA8",
    "type": "平面停車場",
    "hours": "24小時",
    "pricing": {
        "allDay": "30分 ¥330",
        "maximum": "入庫後24小時最高 ¥1,400（重複適用）"
    },
    "estimatedParking": {
        "start": "20:00",
        "end": "23:00",
        "durationMinutes": 180,
        "rawYen": 1980,
        "appliedCap": "24小時最高",
        "totalYen": 1400
    }
}

itineraries = project.setdefault("itineraries", {})
day1 = itineraries.setdefault("day1", {"date": "2026-09-16"})
day1["parkingOptions"] = [
    "sapporo-minami3-nishi9-parking",
    "endo-minami3-nishi7-parking"
]
day1["parkingEstimateWindow"] = "20:00–23:00"
day1["preferredParkingType"] = "平面停車場"

for item in project.get("pendingUiChanges", []):
    if item.get("id") in {
        "satudora-otaru-sakaimachi-hours",
        "hachikyo-oyaji-hours",
        "nemuro-hanamaru-cocono-hours",
        "late-night-wording",
    }:
        item["status"] = "published"
        item["websitePublished"] = True
        item["publishedAt"] = PUBLISHED_AT

project.setdefault("pendingUiChanges", []).append({
    "id": "sapporo-night-parking-options",
    "scope": "Day 1／札幌晚上／停車",
    "status": "published",
    "websitePublished": True,
    "publishedAt": PUBLISHED_AT,
    "placeIds": [
        "sapporo-minami3-nishi9-parking",
        "endo-minami3-nishi7-parking"
    ],
    "estimateWindow": "20:00–23:00",
    "display": "列出兩個平面停車候選與預估停車費"
})

database.setdefault("changeLog", []).append({
    "date": "2026-07-30",
    "projectId": "2026-hokkaido",
    "scope": "Day 1 札幌晚上／平面停車與營業時間",
    "changes": [
        "新增 Parking（南3條西9丁目）平面停車場；20:00–23:00 原價 ¥1,800，套用夜間最高後預估 ¥800",
        "新增遠藤興産㈱ 南３西７パーキング；20:00–23:00 原價 ¥1,980，套用24小時最高後預估 ¥1,400",
        "網頁札幌晚上區塊列出兩個停車候選與 Google Maps 定位",
        "海味はちきょう別亭 おやじ與根室花丸 COCONO SUSUKINO店補上營業時間",
        "『消夜』統一改為『宵夜』",
        "サツドラ小樽堺町店營業時間更新為10:30–19:00"
    ],
    "websitePublished": True,
    "publishedAt": PUBLISHED_AT
})

with DATABASE.open("w", encoding="utf-8", newline="\n") as fh:
    json.dump(database, fh, ensure_ascii=False, indent=2)
    fh.write("\n")

print("Sapporo night parking and pending business-hours updates published.")
