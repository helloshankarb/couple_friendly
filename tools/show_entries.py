import json
with open('app/src/main/assets/flirt_dataset.json', encoding='utf-8-sig') as f:
    data = json.load(f)
for i in range(195, 220):
    if i < len(data):
        entry = data[i]
        print(f'[{i}] "{entry["incoming"]}" ({entry["category"]})')
