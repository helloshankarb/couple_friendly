import json, re, sys

with open('app/src/main/assets/flirt_dataset.json','r',encoding='utf-8-sig') as f:
    data = json.load(f)

# Truly non-native formal English patterns (not casual code-mix like plan/call/okay/hot)
patterns_to_find = [
    'absence', 'painful', 'beautiful', 'happiness', 'seriously', 
    'definitely', 'honestly', 'incredible', 'wonderful', 'amazing',
    'completely', 'actually', 'basically', 'probably', 'suddenly',
    'finally', 'exactly', 'truly', 'without you', 'forever',
    'everything to me', 'nothing without', 'something special',
    'my world', 'my life', 'my heart', 'my dream', 'my angel',
    'my heaven', 'deserve', 'appreciate', 'protect', 'possessive'
]

results = {}
for entry in data:
    for tone in ['romantic','sweet','funny','bold']:
        if tone in entry:
            for s in entry[tone]:
                low = s.lower()
                for p in patterns_to_find:
                    if p in low:
                        if p not in results:
                            results[p] = []
                        results[p].append(s[:70])

print('Non-native formal English patterns found:')
for p, examples in sorted(results.items(), key=lambda x:-len(x[1])):
    print(f'\n  "{p}" ({len(examples)} occurrences):')
    for ex in examples[:3]:
        print(f'    - {ex}')
print(f'\nTotal sentences to fix: {sum(len(v) for v in results.values())}')
