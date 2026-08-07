from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / 'data' / 'master-database.json'

data = json.loads(DB.read_text(encoding='utf-8'))
project = data['projects']['2026-hokkaido']
place = project['places']['don-quijote-susukino']

place.update({
    'displayName': '唐吉訶德 薄野店',
    'name': 'ドン・キホーテ すすきの店',
    'mapUrl': 'https://maps.app.goo.gl/MCJ91HKKE3WrvuQt7',
    'officialUrl': 'https://www.donki.com/store/shop_detail.php?shop_id=657',
    'address': '〒064-0805 北海道札幌市中央区南5条西3丁目11番地',
    'phone': '0570-069-090',
    'hours': '10:00–05:00',
    'regularHoliday': '無',
    'parking': {'available': False, 'note': '店舖無專用停車場'},
    'access': '札幌市營地下鐵南北線「すすきの站」步行約2分鐘',
    'services': ['免稅', '醫藥品', '酒類', '信用卡', '銀聯卡', '電子支付'],
    'category': 'Day 1／札幌晚上／採買',
    'source': 'ドン・キホーテ官方店舗情報',
    'verifiedAt': '2026-08-07'
})

data['databaseVersion'] = '1.6'
data['updatedAt'] = '2026-08-07T15:36:00+08:00'

for item in project.get('pendingUiChanges', []):
    if item.get('id') == 'donki-susukino-day1-shopping':
        item['status'] = 'completed-local'
        item['websitePublished'] = False
        item['targetDisplay'] = {
            'displayName': '唐吉訶德 薄野店',
            'name': 'ドン・キホーテ すすきの店',
            'hours': '10:00–05:00',
            'mapUrl': 'https://maps.app.goo.gl/MCJ91HKKE3WrvuQt7',
            'address': '〒064-0805 北海道札幌市中央区南5条西3丁目11番地'
        }

scope = 'Day 1 札幌晚上／唐吉訶德薄野店資料補齊'
if not any(x.get('scope') == scope for x in data.get('changeLog', [])):
    data.setdefault('changeLog', []).append({
        'date': '2026-08-07',
        'projectId': '2026-hokkaido',
        'scope': scope,
        'changes': [
            '補入中文顯示名稱：唐吉訶德 薄野店',
            '保留日文正式名稱：ドン・キホーテ すすきの店',
            '補入官方地址、電話、官方店舖頁、定休日、交通資訊',
            '補入無專用停車場資訊',
            '補入免稅、醫藥品、酒類、信用卡、銀聯卡與電子支付服務資訊',
            '網頁本機版以中文名稱為主、日文正式名稱為次要資訊'
        ],
        'websitePublished': False
    })

DB.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Don Quijote Susukino data enriched.')
