import json

with open(r'e:\apps\couple_friendly\app\src\main\assets\flirt_dataset.json', encoding='utf-8-sig') as f:
    data = json.load(f)

all_replies = []
for entry in data:
    for tone in ['romantic', 'sweet', 'funny', 'bold']:
        all_replies.extend(entry.get(tone, []))

bad_patterns = [
    'Aww', 'ne leni lotu', 'upiri aagipothundhi', 'upiri theeskuntunna',
    'oxygen', 'cry chesthundi', 'die aipothunna', 'unbearable',
    'khushi aipoyanu', 'Nuvvu lekunda', 'ne ae naa oxygen',
    'puri munigipoyanu', 'oopiri', 'Nuvvu lekunda upiri',
    'Na gundey ne kosam', 'ne gundey karigipoyindhi',
]

for p in bad_patterns:
    count = sum(1 for r in all_replies if p.lower() in r.lower())
    if count > 0:
        print(f'{count:3d} replies contain: "{p}"')

print(f'\nTotal replies: {len(all_replies)}')
print(f'Total entries: {len(data)}')
cats = sorted(set(e["category"] for e in data))
print(f'Categories ({len(cats)}): {cats}')
