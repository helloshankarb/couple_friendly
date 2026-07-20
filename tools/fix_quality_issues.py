"""
fix_quality_issues.py
=====================
Fixes all remaining quality issues in flirt_dataset.json:
  1. CORPORATE 'certified' / 'premium' → replace with natural Telugu humor
  2. CRINGE 'activate' / 'mode' → replace with native alternatives
  3. TOO SHORT replies (< 4 words) → expand with natural filler

Run: python tools/fix_quality_issues.py
"""

import json, re, sys

DATASET_PATH = r'e:\apps\couple_friendly\app\src\main\assets\flirt_dataset.json'
sys.stdout.reconfigure(encoding='utf-8')

# ── Pass 1: direct string replacements ─────────────────────────────────────

STR_FIXES = [
    # certified / premium → native-style
    ("Air thinna healthy diet certified! 🤣", "Air thinna healthy diet expert nuvvu bujji! 🤣"),
    ("Maggi ae single jeevitham food certified! 🤣", "Maggi ae naa single jeevitham food hero! 🤣"),
    ("I know born cute certified! 🤣", "I know born cute, neeku cheppali enduku! 🤣"),
    ("Bathroom singer certified official ga! 😂", "Bathroom singer unnav official ga announce chesukuntunna! 😂"),
    ("Vampire schedule lo unna certified! 😂", "Vampire schedule lo unna, day night ulatipoyindhi! 😂"),
    ("Naa daggara bore impossible certified! 😅", "Naa daggara bore avvadam impossible, try chesthe telustundhi! 😅"),
    ("Shakespeare of hmm certified bujji! 😂", "Hmm ki intha meaning isthe Shakespeare ni savalista ra! 😂"),
    ("Stress buster nenu certified! 😢", "Stress buster nenu, try chesthe telustundhi bujji! 😢"),
    ("Legal torture office certified! 😂", "Legal torture adi, daily survive chesthunte hero unnav! 😂"),
    ("Energy drinks fake certified bujji! 😂", "Energy drinks anni fake, nuvvu msg chesthe real energy vasthundhi! 😂"),
    ("Hug best heater certified bujji! 🤗", "Hug best heater, winter lo naaku ne chaalu bujji! 🤗"),
    ("Stress relief naa speciality certified! 😏", "Stress relief naa speciality, appointment book chesuko! 😏"),
    ("Job hating club member certified! 🤣", "Job hating club member ga welcome, nenu president! 🤣"),
    ("Born comedian certified official ga! 😂", "Born comedian nuvvu, naaku prove chesav today! 😂"),
    ("Professional teaser certified! 🤣", "Professional teaser unnav, nenu professional responder! 🤣"),
    ("Drama king certified award bujji! 😂", "Drama king unnav, Oscar petition vestha naaku kuda! 😂"),
    ("Surveillance expert certified! 😂", "Surveillance expert aipoyav, nenu tracking off chesukunta! 😂"),
    ("Unique specimen certified lab report! 🤣", "Unique specimen unnav, lab report kavala naaku validate chesukodaniki! 🤣"),
    ("One of a kind certified! 😂", "One of a kind nuvvu, duplicate ledu market lo! 😂"),
    ("Google maps expert certified! 🤣", "Google maps expert unnav, naa location miss chesukuntunnav ee drama tho! 🤣"),
    ("Single premium Netflix enjoy bujji! 😂", "Single ga premium Netflix enjoy chestha, invitation ochindhi mee nundi! 😂"),
    ("Best chef naa bangaram certified! ❤️", "Best chef naa bangaram, ee hands tho chesina vanta taste avthundhi! ❤️"),
    ("Protein shake addict certified! 🏃", "Protein shake addict aipoyav, health is wealth le! 🏃"),
    ("Sweat masking expert certified! 🤣", "Sweat masking expert aipoyav gym lo, teaching cheyyi naaku! 🤣"),

    # cringe activate → native
    ("Penguin mode activate waddle! 🐧", "Penguin laga walk chestunte cute ga untav bujji! 🐧"),
    ("Serious mode permanent activate! 😂", "Serious ga unnav always, oka navvu cheyyi please! 😂"),
    ("Telepathy activate concentration! 🤣", "Telepathy try chestha, ne gurinche alochishunte signal vasthundha? 🤣"),
    ("Secret agent mode activate! 😂", "Secret agent laga disappear aipoyav, trace avvatledu! 😂"),
    ("Panic mode activate hide everything! 🤣", "Panic aipoyav kada, adhe cute ga undhi ne lo! 🤣"),
    ("Marry me energy peak level! 😍", "Nee tho forever undaali anipistundhi nijam ga bujji! 😍"),

    # premium
    ("Single premium Netflix enjoy bujji! 😂", "Single ga premium Netflix enjoy, ee life lo balance undali! 😂"),
]

# ── Pass 2: index-based fixes for TOO SHORT replies ─────────────────────────
# Format: (entry_index, tone, reply_index, new_reply)

INDEX_FIXES = [
    # [8] Hii
    (8, "sweet", 0, "Hiiii bujji em chesthunnav ippudu? 🥰"),
    (8, "sweet", 2, "Hii baby em scene ippudu cheppu? 💕"),
    (8, "funny", 4, "Hiiiii back bujji, ee sudden ga msg chesav! 😂"),

    # [18] Chupiddama related
    (18, "bold", 2, "Chupiddama marchipoledu ani socha, vasthav aa? 😏"),
    (20, "bold", 3, "Chupiddama tonight, free unnav aa bujji? 😅"),

    # [21] Ayyoo sorry
    (21, "sweet", 3, "Ayyoo sorry bujji hurt chesanu, forgive chesav aa? 🥺"),

    # [26] Nuvvu adbhutam
    (26, "sweet", 4, "Nuvvu adbhutam bangaram, eppudu chusina same feel! 🥰"),
    (26, "bold", 2, "Chupinchu tonight bujji, prove chestha! 😏"),

    # [27] Same bujji
    (27, "sweet", 1, "Same feeling bujji, nee tho matladataame chaalu! 🥰"),

    # [28] khushi tears
    (28, "sweet", 3, "Khushi tears vasthunnai bujji, ne words lo magic undhi! 🥹"),

    # [29] Gurtuchesav thanks
    (29, "sweet", 4, "Gurtuchesav thanks bangaram, naa day bright aipoyindhi! 🥰"),

    # [31] Biryani baby
    (31, "sweet", 2, "Biryani baby delicious, ne hands lo magic undhi! 😋"),

    # [35] Ippude modalu
    (35, "bold", 1, "Ippude modalu chesanu, ready ga undhu! 😉"),

    # [40] Aagalekapothunna super
    (40, "sweet", 4, "Aagalekapothunna super excited bujji, eppudu kaladam? 🥰"),

    # [43] Haha thanks baby
    (43, "sweet", 2, "Haha thanks baby, nee words tho day set aipoyindhi! 😊"),

    # [44] Nuvvu gorgeous
    (44, "sweet", 1, "Nuvvu gorgeous bujji, daily cheppali anipistundhi! 🥰"),
    (44, "sweet", 2, "Arey sweet ga cheppav thanks bangaram! 😊"),

    # [46] Nammu bujji / Abhimanam
    (46, "sweet", 4, "Nammu bujji please, nenu nijam ga chesthunna! 🥰"),
    (46, "bold", 2, "Abhimanam nachindhi baby, nee tone lo fire undhi! 😏"),

    # [55] Em aalochisthunnav / Matladam
    (55, "sweet", 4, "Em aalochisthunnav baby cheppu, vintunna! 🥰"),
    (56, "sweet", 1, "Matladam inka bujji, chala miss chesanu! 🥰"),
    (56, "sweet", 2, "Okay baby, ippudu matladaam kadaa! 😊"),

    # [57] baadha avvaku / [58] Please aapu / [59] Tension
    (57, "sweet", 2, "Baadha avvaku baby, nenu unna kadaa side lo! 🥹"),
    (58, "sweet", 3, "Please aapu baby, nenu hurt avthunna vintu! 🥺"),
    (59, "sweet", 3, "Tension cheyaku baby, fix avthundhi andham ga! 😊"),

    # [60] Sure bujji / [60] Ippude chestha
    (60, "sweet", 2, "Sure bujji coming, ready ga undhu! 😊"),
    (60, "sweet", 4, "Ippude chestha bangaram, wait cheyyi! 🥰"),

    # [61] Ready bujji calling
    (61, "sweet", 4, "Ready bujji calling, phone lift cheyyi! 📞"),

    # [62] Nuvvu chesthav
    (62, "sweet", 2, "Nuvvu chesthav baby, naa faith unnadi nee meeda! 😊"),

    # [63] Tonight bharistha
    (63, "bold", 4, "Tonight bharistha aagu, prove chestha nenu! 😏"),

    # [64] Teesukosthanu
    (64, "bold", 2, "Teesukosthanu back, tappinchukolevu bujji! 😏"),

    # [68] Energize chestha
    (68, "bold", 3, "Energize chestha guarantee, try cheyyi once! 😉"),

    # [73] Enjoy bujji
    (73, "sweet", 4, "Enjoy bujji, deserve chesav full on! 🥰"),

    # [77] Already okay
    (77, "sweet", 3, "Already okay avthindhi bujji, nenu unna kada side lo! 😊"),

    # [83] Smart bujji
    (83, "sweet", 3, "Smart bujji unnav, nee mind ni love chestha! 😊"),

    # [84] Celebrations time
    (84, "sweet", 4, "Celebrations time bangaram, together celebrate cheddaam! 🥰"),

    # [85] Party cheddama
    (85, "sweet", 2, "Party cheddama celebrate, ne tho avvali! 😊"),

    # [86] Support chestha always
    (86, "sweet", 4, "Support chestha always bujji, nee side lo unna! 🥰"),

    # [88] Chivariki recognition
    (88, "funny", 0, "Chivariki recognition dorikinadhi, late ayyindhi kaani vandham! 😂"),
]


def main():
    with open(DATASET_PATH, encoding='utf-8-sig') as f:
        data = json.load(f)

    str_changes = 0
    idx_changes = 0

    # Pass 1: string replacements
    for entry in data:
        for tone in ['romantic', 'sweet', 'funny', 'bold']:
            replies = entry.get(tone, [])
            for k, r in enumerate(replies):
                new_r = r
                for old, new in STR_FIXES:
                    if old in new_r:
                        new_r = new_r.replace(old, new)
                if new_r != r:
                    replies[k] = new_r
                    str_changes += 1

    # Pass 2: index-based
    for (ei, tone, ri, new_reply) in INDEX_FIXES:
        if ei < len(data):
            replies = data[ei].get(tone, [])
            if ri < len(replies):
                replies[ri] = new_reply
                idx_changes += 1

    with open(DATASET_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Pass 1 (string fixes): {str_changes} changes")
    print(f"Pass 2 (index fixes):  {idx_changes} changes")
    print("Done.")


if __name__ == '__main__':
    main()
