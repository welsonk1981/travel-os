from __future__ import annotations

import json
from pathlib import Path

DB = Path('data/master-database.json')
UPDATED_AT = '2026-08-07T14:59:00+08:00'

with DB.open('r', encoding='utf-8') as fh:
    data = json.load(fh)

project = data['projects']['2026-hokkaido']
places = project.setdefault('places', {})
places['don-quijote-susukino'] = {
    'id': 'don-quijote-susukino',
    'name': 'ドン・キホーテ すすきの店',
    'mapUrl': 'https://maps.app.goo.gl/MCJ91HKKE3WrvuQt7',
    'hours': '10:00–05:00',
    'category': 'Day 1／札幌晚上／採買'
}

day1 = project.setdefault('itineraries', {}).setdefault('day1', {'date': '2026-09-16'})
shopping = day1.setdefault('eveningShoppingPlaceIds', [])
if 'don-quijote-susukino' not in shopping:
    shopping.append('don-quijote-susukino')

pending = project.setdefault('pendingUiChanges', [])
if not any(x.get('id') == 'donki-susukino-day1-shopping' for x in pending):
    pending.append({
        'id': 'donki-susukino-day1-shopping',
        'scope': 'Day 1／札幌晚上／採買',
        'status': 'recorded',
        'websitePublished': False,
        'placeId': 'don-quijote-susukino',
        'targetCategory': '🛍️ 採買',
        'targetDisplay': {
            'name': 'ドン・キホーテ すすきの店',
            'hours': '10:00–05:00',
            'mapUrl': 'https://maps.app.goo.gl/MCJ91HKKE3WrvuQt7'
        }
    })

log = data.setdefault('changeLog', [])
if not any(x.get('scope') == 'Day 1 札幌晚上／唐吉訶德薄野店' for x in log):
    log.append({
        'date': '2026-08-07',
        'projectId': '2026-hokkaido',
        'scope': 'Day 1 札幌晚上／唐吉訶德薄野店',
        'changes': [
            '新增ドン・キホーテ すすきの店',
            'Google Maps：https://maps.app.goo.gl/MCJ91HKKE3WrvuQt7',
            '營業時間：10:00–05:00',
            '歸類至 Day 1 札幌晚上／採買',
            '本次先寫入 Master Database；正式 GitHub Pages 尚未發布'
        ],
        'websitePublished': False
    })

data['updatedAt'] = UPDATED_AT

with DB.open('w', encoding='utf-8', newline='\n') as fh:
    json.dump(data, fh, ensure_ascii=False, indent=2)
    fh.write('\n')

print('Master Database updated: Don Quijote Susukino')
