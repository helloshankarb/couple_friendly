import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('app/src/main/assets/flirt_dataset.json', encoding='utf-8') as f:
    data = json.load(f)
for i, e in enumerate(data):
    if i in (3, 8):
        print(f"Entry {i}: incoming={repr(e['incoming'])}")
        print(f"  romantic[0]={repr(e['romantic'][0])}")
        print(f"  funny[1]={repr(e['funny'][1])}")
        if i == 8:
            print(f"  romantic[3]={repr(e['romantic'][3])}")
            print(f"  bold[3]={repr(e['bold'][3])}")
