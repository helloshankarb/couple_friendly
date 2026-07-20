import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('app/src/main/assets/flirt_dataset.json', encoding='utf-8') as f:
    data = json.load(f)
flagged = [8,9,19,21,22,27,28,30,32,36,41,42,44,45,47,50,54,56,57,58,59,60,61,62,63,64,65,69,70,74,76,78,84,85,86,87,89,91,92,93,95,96,97,98,101,102,103,104,106,107,108,110,111,113,114,115,116,117,119,121,122,123,124,126,127,128,131,135,137,138,139,140,142,146,147,148,151,152,153,154,155,156,157,158,159,160,161,162,164,166,167,168,171,172,176,178,179,181,184,185,186,188,190,191,194,195,197,199,200,203]
for i in flagged:
    e = data[i]
    print(f'[{i}] incoming={repr(e["incoming"])} cat={e["category"]}')
    for tone in ("romantic","sweet","funny","bold"):
        for j,r in enumerate(e[tone]):
            print(f'  {tone}[{j}]: {r}')
    print()
