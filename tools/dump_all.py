import json, sys
sys.stdout.reconfigure(encoding='utf-8')
data = json.load(open('app/src/main/assets/flirt_dataset.json','r',encoding='utf-8'))
for i, e in enumerate(data):
    print(f'[{i:3}] {repr(e["incoming"])} ({e["category"]})')
    for tone in ['romantic','sweet','funny','bold']:
        if tone in e:
            print(f'  [{tone}]')
            for s in e[tone]:
                print(f'    - {s}')
