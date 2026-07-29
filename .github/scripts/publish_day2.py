from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "index.html"
DATABASE = ROOT / "data" / "master-database.json"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)


html = INDEX.read_text(encoding="utf-8")

html = replace_once(
    html,
    "🗿 頭大佛 → 🦐 場外市場 → 🎓 北海道大學 → 🏙 小樽",
    "⛩️ 琴似神社 → 🦐 海鮮早餐 → 🎓 北大 → 🗿 頭大佛 → 🏙 小樽",
    "Day 2 preview route",
)

if "kotoniJinja:Object.freeze" not in html:
    marker = "  hokudaiMarcheCafe:Object.freeze({"
    insert = '''  kotoniJinja:Object.freeze({
    id:"kotoni-jinja",
    name:"琴似神社",
    mapUrl:"https://maps.app.goo.gl/C7Hq32wX3t4aCAuQ9",
    hours:"境內自由參拜"
  }),
  marusanMikamiMarusantei:Object.freeze({
    id:"marusan-mikami-marusan-tei",
    name:"㈱マルサン三上商店／まるさん亭 本店",
    mapUrl:"https://maps.app.goo.gl/9ojJpxLfgaYLS4se9",
    hours:"07:00–15:00"
  }),
  hokkaidoUniversity:Object.freeze({
    id:"hokkaido-university",
    name:"北海道大學",
    mapUrl:"https://www.google.com/maps/search/?api=1&query=北海道大学",
    hours:""
  }),
  hillOfBuddha:Object.freeze({
    id:"hill-of-buddha",
    name:"頭大佛",
    mapUrl:"https://www.google.com/maps?cid=15134224251499317861",
    hours:"09:00–16:00"
  }),
'''
    html = replace_once(html, marker, insert + marker, "master location insertion")

hokudai_pattern = re.compile(
    r'  hokudaiMarcheCafe:Object\.freeze\(\{\n.*?\n  \}\),',
    re.S,
)
hokudai_replacement = '''  hokudaiMarcheCafe:Object.freeze({
    id:"hokudai-marche-cafe",
    name:"北大マルシェ Café & Labo",
    mapUrl:"https://www.google.com/maps/search/?api=1&query=北大マルシェ+Café%26Labo",
    hours:"10:00–16:00"
  }),'''
html, count = hokudai_pattern.subn(hokudai_replacement, html, count=1)
if count != 1:
    raise RuntimeError(f"hokudai master location: expected 1 match, found {count}")

new_day2 = '''  day2:{
    label:"Day 2｜9/17（四）",
    highlights:["琴似神社","㈱マルサン三上商店／まるさん亭 本店","北海道大學","頭大佛","小樽港町"],
    missions:["琴似神社晨間參拜","08:30 海鮮早餐","北大マルシェ乳製品體驗","頭大佛參觀","14:30 花窗玻璃美術館","小樽 Muse晚餐"],
    foodFocus:["まるさん亭海鮮早餐","北大マルシェ牛奶／冰淇淋","小樽冰品候選"],
    route:"琴似住宿 → 琴似神社 → ㈱マルサン三上商店 → 北海道大學 → 頭大佛 → 小樽",
    hotel:"小樽住宿",
    stops:[
      {time:"07:30–12:25",name:"札幌早晨｜琴似神社・海鮮早餐・北大・頭大佛",steps:[["07:30","札幌住宿步行出發"],["07:40–08:00","琴似神社"],["08:00–08:10","步行返回住宿"],["08:10–08:30","取車並前往海鮮早餐"],["08:30–09:20","㈱マルサン三上商店／まるさん亭 本店"],["09:20–09:45","前往北海道大學並停車"],["09:45–10:00","北海道大學短散步"],["10:00–10:40","北大マルシェ Café & Labo"],["10:40–11:30","前往頭大佛"],["11:30–12:25","頭大佛"]],stay:"約 4 小時 55 分",next:"12:25 出發前往小樽",collapsible:true},
      {time:"12:25–13:35",name:"前往小樽",note:"由頭大佛前往小樽住宿附近。",stay:"開車約 70 分",next:"抵達後停車、放行李"},
      {time:"13:35–14:05",name:"抵達小樽／停車・放行李",note:"住宿停車後改為步行。",stay:"約 30 分",next:"步行前往花窗玻璃美術館"},
      {time:"14:05–14:25",name:"步行前往花窗玻璃美術館",note:"由住宿附近步行前往。",stay:"約 20 分",next:"14:30 入館"},
      {time:"14:30–15:15",name:"⑦ 花窗玻璃美術館（舊高橋倉庫）｜必去",note:"營業時間 09:30–17:00。",stay:"約 45 分",next:"步行約 15 分前往堺町通"},
      {time:"15:30–17:30",name:"堺町通｜依關門時間順逛",steps:[["15:30–15:45","⑥ アイスクリームパーラー美園｜11:00–17:00"],["15:50–16:10","⑤ ポプラファーム 小樽店｜11:00–17:30（L.O.17:00）"],["16:15–16:35","③ 六花亭 小樽運河店｜10:00–18:00"],["16:35–16:55","② 北菓楼 小樽本館｜10:00–18:00"],["17:00–17:30","① LeTAO 總店｜09:00–19:00"]],stay:"約 2 小時",next:"18:30 小樽 Muse 晚餐",collapsible:true},
      {time:"18:30",name:"⑧ 小樽 Muse",reservation:"已預約",note:"燭光洋食餐廳",stay:"60–90 分",next:"晚餐後可前往小樽運河"},
      {time:"20:30",name:"⑨ 小樽運河",note:"晚餐後欣賞夜景；若當晚太累，可改隔天清晨散步。",stay:"約 30–60 分"}
    ],
    areas:[
      {
        title:"札幌北側早晨",
        note:"",
        layout:"walking-guide",
        shops:[
          ["●",masterLocations.kotoniJinja.name,"",masterLocations.kotoniJinja.hours,masterLocations.kotoniJinja.mapUrl,""],
          ["●",masterLocations.marusanMikamiMarusantei.name,"",masterLocations.marusanMikamiMarusantei.hours,masterLocations.marusanMikamiMarusantei.mapUrl,""],
          ["●",masterLocations.hokkaidoUniversity.name,"",masterLocations.hokkaidoUniversity.hours,masterLocations.hokkaidoUniversity.mapUrl,""],
          ["●",masterLocations.hokudaiMarcheCafe.name,"",masterLocations.hokudaiMarcheCafe.hours,masterLocations.hokudaiMarcheCafe.mapUrl,""]
        ]
      },
      {
        title:"頭大佛",
        layout:"place-guide",
        shops:[
          ["1",masterLocations.hillOfBuddha.name,"11:30–12:25","",masterLocations.hillOfBuddha.mapUrl,"開放時間 09:00–16:00"]
        ]
      },
      {
        title:"小樽",
        note:"從 1-19 Shinonomechō 出發，由近到遠。",
        layout:"walking-guide",
        shops:[
          ["①",masterLocations.letAoMain.name,"Double Fromage 雙層起司蛋糕、Royal Montagne 巧克力；LeTAO PLUS 的 Jersey 牛乳霜淇淋。","09:00–19:00",masterLocations.letAoMain.mapUrl,"甜點選購"],
          ["②","北菓楼 小樽本館","妖精之森年輪蛋糕、開拓おかき與夢不思議泡芙。","10:00–18:00","https://www.google.com/maps/search/?api=1&query=北菓楼+小樽本館","甜點選購"],
          ["③","六花亭 小樽運河店","Marusei 奶油夾心餅、草莓巧克力與雪やこんこ。","10:00–18:00","https://www.google.com/maps/search/?api=1&query=六花亭+小樽運河店","甜點選購"],
          ["④","北一硝子三号館","玻璃杯、醬油瓶與燈具；Terrace 的八段霜淇淋。","10:00–17:30（L.O.17:15）","https://www.google.com/maps/search/?api=1&query=北一硝子三号館","玻璃工藝"],
          ["⑤","ポプラファーム 小樽店","サンタのヒゲ：半顆哈密瓜搭配北海道牛奶霜淇淋。","11:00–17:30（L.O.17:00）","https://www.google.com/maps/search/?api=1&query=ポプラファーム+小樽店","冰品備選"],
          ["⑥","アイスクリームパーラー美園","自家製傳統冰淇淋、聖代或冰淇淋蘇打。","11:00–17:00","https://www.google.com/maps/search/?api=1&query=アイスクリームパーラー美園+小樽","老舖冰品"],
          ["⑦","花窗玻璃美術館（舊高橋倉庫）","先參觀有固定閉館時間的必去景點。","09:30–17:00","https://maps.app.goo.gl/4S6TfKmJY84Zrqd47","必去美術館"],
          ["⑧","小樽 Muse","漢堡排、蛋包飯等洋食。","18:30｜17:00–20:30（L.O.20:00）；週一休","https://www.google.com/maps/search/?api=1&query=小樽+Muse","","","", "已預約"],
          ["⑨","小樽運河","晚餐後欣賞夜景，或隔天清晨散步；拍攝石造倉庫、煤氣燈與水面倒影。","全天開放","https://www.google.com/maps/search/?api=1&query=小樽運河","晚間／清晨皆可"]
        ]
      }
    ]
  },
  day3:{'''

day2_pattern = re.compile(r'  day2:\{\n.*?\n  \},\n  day3:\{', re.S)
html, count = day2_pattern.subn(new_day2, html, count=1)
if count != 1:
    raise RuntimeError(f"Day 2 object: expected 1 match, found {count}")

must_do_pattern = re.compile(r'  "9/17":\[[^\n]*\],')
new_must_do = '  "9/17":["⛩️ 07:40 琴似神社","🦐 08:30 ㈱マルサン三上商店／まるさん亭 本店","🎓 10:00 北大マルシェ Café & Labo","🗿 11:30 頭大佛","🪟 14:30 花窗玻璃美術館（舊高橋倉庫）","🍽️ 18:30 小樽 Muse"],'
html, count = must_do_pattern.subn(new_must_do, html, count=1)
if count != 1:
    raise RuntimeError(f"Day 2 must-do: expected 1 match, found {count}")

html = re.sub(
    r'<!-- pages-redeploy:[^>]*-->',
    '<!-- pages-redeploy:2026-07-29T15:23+08:00 -->',
    html,
    count=1,
)

required = [
    "札幌北側早晨",
    "琴似神社",
    "㈱マルサン三上商店／まるさん亭 本店",
    "北大マルシェ Café & Labo",
    "11:30–12:25",
]
for value in required:
    if value not in html:
        raise RuntimeError(f"missing required published value: {value}")

INDEX.write_text(html, encoding="utf-8")

with DATABASE.open("r", encoding="utf-8") as fh:
    database = json.load(fh)

database["updatedAt"] = "2026-07-29T15:23:00+08:00"
if database.get("changeLog"):
    database["changeLog"][-1]["websitePublished"] = True
    database["changeLog"][-1]["publishedAt"] = "2026-07-29T15:23:00+08:00"

with DATABASE.open("w", encoding="utf-8", newline="\n") as fh:
    json.dump(database, fh, ensure_ascii=False, indent=2)
    fh.write("\n")

print("Day 2 publication patch completed.")
