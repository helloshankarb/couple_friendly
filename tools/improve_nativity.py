"""
improve_nativity.py
===================
Improves Telugu nativity and realism across all entries in flirt_dataset.json.

Two-pass approach:
  Pass 1: Pattern-based fixes (fast, covers ~80 bad phrases)
  Pass 2: Full entry rewrites for selected critical incoming messages

Run: python tools/improve_nativity.py
"""

import json
import re
import copy

DATASET_PATH = r'e:\apps\couple_friendly\app\src\main\assets\flirt_dataset.json'

# ============================================================
# PASS 1: String-level replacements (case-sensitive)
# ============================================================
REPLACEMENTS = [
    # Remove English "Aww" → native expressions
    ("Aww same here bujji", "Same here bujji"),
    ("Aww same here bangaram", "Same ra bangaram"),
    ("Aww really chala khushi aipoyanu", "Nijam ga chala happy aipoya bujji"),
    ("Aww that's so sweet bangaram", "Chala sweet ga cheppav bangaram"),
    ("Aww adorable bujji", "Cute ga cheppav bujji"),
    ("Aww chivariki msg chesav, khushi aipoyanu", "Chivariki msg chesav, day set aipoyindhi"),
    ("Aww so formal ga cheppav cute undhi", "Enti formality baby, direct ga matladudam kadaa"),
    ("Aww ne msg vasthe automatic ga navvu vasthundhi bangaram", "Ne msg vasthe automatic ga navvu vasthundhi bangaram"),
    ("Aww", "Arey"),

    # Fix "ne leni lotu" pattern → more natural
    ("Cute ga cheppav ne leni lotu too baby", "Ne leka ee roju boring ga undhi baby"),
    ("ne leni lotu more bujji pakka", "Ne leka ikkade sit chesunna bujji"),
    ("ne leni lotu more bujji", "Ne leka chala bore avthunna"),
    ("ne leni lotu bharinchaleka too bangaram", "Ne leka sit avvatledu bangaram nijam ga"),
    ("Ne leni lotu more", "Ne leka miss avthunna"),
    ("ne leni lotu", "ne leka miss avthunna"),

    # Remove dramatic Bollywood-ish phrases
    ("Nuvvu lekunda upiri aagipothundhi nijam ga", "Ne leka undalekupothunna bujji nijam ga"),
    ("Nuvvu lekunda upiri aagipothundhi", "Nee leka undalekupothunna"),
    ("upiri aagipothundhi", "miss avthunna chala"),
    ("upiri theeskuntunna", "nee dhyasa lo unna"),
    ("Oopiri theeskuntunna", "Nee msg kosam wait chesthunna"),
    ("oopiri", "upiri"),
    ("ne ae naa oxygen daily", "nee gurinche daily alochisthunna"),
    ("ne gundey karigipoyindhi", "chala happy aipoya"),
    ("Na gundey ne kosam cry chesthundi", "Nee leka sit avvatledu nijam ga"),
    ("na gundey cry", "nenu chala miss avthunna"),
    ("die aipothunna ikkada", "miss avthunna chala bujji"),
    ("die aipothunna", "chala miss avthunna"),
    ("unbearable aipothundi", "miss avthunna chala"),
    ("unbearable", "chala miss avthunna"),
    ("puri munigipoyanu", "poorthiga nee dhyasa lo unna"),

    # Fix overly formal words
    ("khushi aipoyanu", "happy aipoya"),
    ("khushi aipoyanu!", "happy aipoya! "),
    ("Khushi aipoyanu", "Happy aipoya"),
    ("khushi aipotha", "happy avtha"),
    ("khushi aipoyindhi", "happy aipoyindhi"),
    ("karigipoyindhi", "melted aipoyindhi"),

    # Fix repeated "same" responses
    ("Same bangaram unbearable aipothundi", "Nenu kuda miss avthunna bangaram, eppudu kaladam?"),
    ("same ne msgs naa treasure chest laga", "ne msgs anni save chesunna ikkada"),

    # Add more native Hyderabadi flavor to generic phrases
    ("blessed feel", "chala blessed ga feel avthunna"),
    ("night night ippudu nundi gurthu vasthunnav already", "paduko bujji, dreams lo vastha pakka"),
    ("ne daggara undaali kaani distance torture", "distance unnaa nee gurinche alochisthunna le bangaram"),
    ("ne thoughts naa favorite time pass", "nee gurinche aalochinchataame naa best timepass"),

    # Fix tone in bold — remove explicit/disrespectful
    ("Ne bed lo space undha naaku bujji", "Tonight meet avvadamaa plans fix cheddaam bujji"),
    ("ne bed lo undhi na better address", "Nee room ki vastha tonight meet avvadama"),
    ("kiss ivvakunda padukuthav aa", "paduko baby, morning matladaam"),
    ("morning kiss tho lepista pakka", "morning lo first msg nuvve chesav pakka"),

    # Fix double spaces / typos
    ("screenshot teesukunna proof kosamm", "screenshot teesukunna proof kosam"),
    ("  ", " "),
]

# ============================================================
# PASS 2: Full entry rewrites for key incoming messages
# These are 100% native Hyderabadi-style rewrites
# ============================================================
FULL_REWRITES = {
    "Hi": {
        "romantic": [
            "Ne msg chuste chaalu bangaram, na day perfect ayipothundhi! ❤️",
            "Chivariki hi chesav, entha sepu eduru chusano telusa bujji! 😘",
            "Ne oka hi ki na gundey full on happy aipoyindhi! 🥰",
            "Late ayyindhi kaani vacchav kadaa bangaram, chaalu naaku! 💕",
            "Ne hi chuste naa face lo smile automatic ga vasthundhi! 😍"
        ],
        "sweet": [
            "Heyy bujji, em scene ippudu? 🥰",
            "Hi baby, chala sepu nundi msg raaledu wait chestunte vacchav! 😊",
            "Hiiii bangaram, baaga unnav kadaa? 💕",
            "Ne msg vasthe automatic ga navvu vasthundhi bangaram! 😘",
            "Heyy, gurthu vasthunnav chala ninnati nundi! 🥰"
        ],
        "funny": [
            "Enti idi miracle aa, nuvvu msg chesav? 😂",
            "Oh god notification ochindhi, screenshot teesukunna proof kosam! 😜",
            "Arey ne phone panichesthunda confirm chesuko bujji! 🤭",
            "Idi nijamaa leda kalana ani cheyyi gichukunna! 😂",
            "Nuvvu msg cheyadam enti, sunrise laga rare event! 🤣"
        ],
        "bold": [
            "Hi kaadu bujji, call cheyyi voice vinali! 😏",
            "Ne msg vasthe plans puttukunthayi automatic ga! 🔥",
            "Hi aithe ok, ippudu tarvatha em cheddaam? 😉",
            "Ne oka hi ki full on excited aipoyanu! 😏",
            "Hi cheppav chaalu, inka ne meeda control ledu! 😘"
        ]
    },
    "Miss avthunna": {
        "romantic": [
            "Nenu double miss avthunna bangaram, nee kanna ekkuva! ❤️",
            "Same bujji, ne daggara undaali anipistundhi prathi second! 😘",
            "Miss avthunnav ante na gunde melted aipoyindhi baby! 🥰",
            "Eppudu kaladam? Nenu wait chesthunna bangaram! 💕",
            "Ne leka ee roju boring ga undhi bujji, twaraga kalayyi! 😍"
        ],
        "sweet": [
            "Same here bujji, chala gurthu vasthunnav! 🥰",
            "Nenu kuda bangaram, twaraga kaladam please! 😊",
            "Ne msg vasthe miss taggindhi konchem, call cheyyana? 💕",
            "Nuvvu kuda gurthu vasthunnav roju motham! 😘",
            "Same feeling bujji, soon kaladam pakka! 🥰"
        ],
        "funny": [
            "GPS on cheyyi vasthunna ippude running! 😂",
            "Miss ante marks takkuva osthayi careful bujji! 🤣",
            "Aithe raa solve chesukondaam, miss problem solve! 😜",
            "Enti adhe msg cheyyi daily reminder la! 🤭",
            "Miss avthunna ante naaku cheppali enduku bujji, raa direct ga! 😂"
        ],
        "bold": [
            "Miss aithe raa direct na daggara ki! 😏",
            "Miss cheyyadam aapu, feel cheyyi daggara ga! 😉",
            "Aithe tonight kaladam fix cheddaam pakka! 🔥",
            "Raa bujji, miss ni cure chestha guarantee! 😏",
            "Door open undhi bangaram, ne vasthe miss aagipothundhi! 😘"
        ]
    },
    "Good morning": {
        "romantic": [
            "Morning bangaram, ne msg tho day already won aipoyindhi! ❤️",
            "Ne morning msg chuste coffee kanna better feel avthundhi! 😘",
            "Good morning naa bujji, ne face chudaali anipistundhi! 🥰",
            "Rise and shine bangaram, ne gurinche morning lo alochisthunna! 💕",
            "Morning lo ne msg vasthe day poorthiga set aipothundhi! 😍"
        ],
        "sweet": [
            "Good morning bujji, baaga padukunnav aa? 🥰",
            "Morning baby, sweet dreams ocha ninnu gurinchi? 😊",
            "Aww morning lo first msg nuvve chesav, khushi! 💕",
            "Good morning bangaram, have an amazing day! 😘",
            "Morning bujji, ne navvu oohinchukunthunna ikkade! 🥰"
        ],
        "funny": [
            "Morning alarm kanna mundu msg chesav, nuvvu genius ra! 😂",
            "Enti early bird aipoyav sudden ga? 🤣",
            "Good morning, coffee ready chesava naaku kuda? 😜",
            "Idi miracle nuvvu early ga lechav today! 🤭",
            "Morning dreams lo nenu ocha kadaa, nijam ga cheppu! 😂"
        ],
        "bold": [
            "Morning bujji, ne pakkanaa levali anipistundhi! 😏",
            "Good morning, video call chesthe day perfect aipothundhi! 😉",
            "Morning hot stuff, neeku vishesham! 🔥",
            "Morning lo ne face chudaali please, video call cheyyi! 😏",
            "Morning ra, ne smile chuste day set! 😘"
        ]
    },
    "Good night": {
        "romantic": [
            "Good night bangaram, dreams lo kaladam promise! ❤️",
            "Night night bujji, ne dreams lo definite ga vastha! 😘",
            "Paduko baby, nee gurinche sweet dreams kanali! 🥰",
            "Good night naa jeevitham, ne last thought nuvve always! 💕",
            "Night bangaram, naadu ee roju last thought kuda nuvve! 😍"
        ],
        "sweet": [
            "Good night bujji, tight ga paduko! 🥰",
            "Night bangaram, sweet dreams kanali nuvvu! 😊",
            "Good night baby, tomorrow twaraga matladaam! 💕",
            "Paduko baaga, good night bangaram! 😘",
            "Night bujji, rest teesuko, tomorrow fresh ga matladaam! 🥰"
        ],
        "funny": [
            "Enti already padukuthunnav, ippudu 10 ey aindhi! 😂",
            "Good night, snoring competition modalu cheyyi! 🤣",
            "Night dreams lo maths homework cheyyi baby! 😜",
            "Ok paduko, free time dorikithe msg cheyyi! 🤭",
            "Good night phone kinda pettukoku, posture bad avthundhi! 😂"
        ],
        "bold": [
            "Good night bujji, dreams lo kalustham! 😏",
            "Night bujji, voice note pampu padukotam mundu! 😉",
            "Good night, tomorrow morning first msg nuvve cheyyi! 🔥",
            "Night bangaram, tomorrow meet avvadamaa plan cheppu! 😏",
            "Paduko, morning lo ne smile chudaali! 😘"
        ]
    },
    "Nuvvu gurthochav": {
        "romantic": [
            "Nuvvu naa prathi kshanam lo untav bangaram! ❤️",
            "Ne gurthu raakunda undatam impossible bujji! 😘",
            "Same bujji, nuvvu naa permanent thought! 🥰",
            "Ne gurthu raataame naa daily happiness! 💕",
            "Nuvvu gurthu vaste chaalu bangaram, day bagaipothundhi! 😍"
        ],
        "sweet": [
            "Nijam ga chala happy aipoya bujji! 🥰",
            "Em chusav nenu gurthocha? Cute! 😊",
            "Nenu kuda ne gurinche alochisthunna, telepathy kadaa! 🥰",
            "Cute ga cheppav bangaram, nenu kuda same! 😘",
            "Nuvvu kuda naa mind lo permanent ga unnav! 🥰"
        ],
        "funny": [
            "Enti em chesanu TV lo ocha nenu? 😂",
            "Gurthu ochanu ante bayam veyaala neeku? 🤣",
            "Nenu ekkada poyanu, gurthu raavaniki! 😜",
            "Enti nenu ghost laga haunt chesana? 🤭",
            "Em chusi gurthocha, honest ga cheppu! 😂"
        ],
        "bold": [
            "Gurthu kaadu bujji, daggara undaali! 😏",
            "Aithe msg kaadu, call cheyyi voice vinali! 😉",
            "Gurthoste raa, real lo kaladam chaalu! 🔥",
            "Ne mind lo nundi poledhu le, permanent unna! 😏",
            "Gurthocha ante action lo pettu raa! 😘"
        ]
    },
    "Em chesthunnav": {
        "romantic": [
            "Ne gurinche alochinchataame naa full time pani! ❤️",
            "Nuvvu msg chese varaku ne kosam wait chesthunna bangaram! 😘",
            "Emi chesina nee dhyasa lo unna bujji! 🥰",
            "Nothing much, nee gurinche alochisthunna le! 💕",
            "Ne daggara undaali anipistundhi, adhe naa mood! 😍"
        ],
        "sweet": [
            "Nothing much bujji, ne msg kosam eduru choostunna! 🥰",
            "Bore avthunna, nuvvu msg chesav happy aipoya! 😊",
            "Just chill chesthunna, nuvvu cheppu em plan? 💕",
            "Phone lo unna, nee gurinche alochisthunna nijam ga! 😘",
            "Netflix chusthunna, nuvvu vasthe better! 🥰"
        ],
        "funny": [
            "Vanta chesthunna Maggi, masterchef feeling! 😂",
            "Prapancham ni daachipettukuntunna Superman laga! 🤣",
            "Free ga unna, pettukovoyyi baby! 😜",
            "Phone chusthunna, ne photos anni chusthunna! 🤭",
            "Nothing productive, nuvvu cheppu em scene? 😂"
        ],
        "bold": [
            "Ne gurinche alochisthunna wild ga! 😏",
            "Nuvvu vasthe em chesthunnano cheptha bujji! 😉",
            "Ne daggara unte better undedhi ee boring ki! 🔥",
            "Ne company gurthu vasthundhi, vasthav aa? 😏",
            "Waiting ra, nuvvu vasthe plans unnay! 😘"
        ]
    }
}


def apply_replacements(text):
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    # Remove double spaces
    text = re.sub(r'  +', ' ', text)
    return text.strip()


def main():
    with open(DATASET_PATH, encoding='utf-8-sig') as f:
        data = json.load(f)

    original = copy.deepcopy(data)
    pass1_changes = 0
    pass2_changes = 0

    # Pass 1: pattern replacements
    for entry in data:
        for tone in ['romantic', 'sweet', 'funny', 'bold']:
            replies = entry.get(tone, [])
            new_replies = []
            for r in replies:
                new_r = apply_replacements(r)
                if new_r != r:
                    pass1_changes += 1
                new_replies.append(new_r)
            entry[tone] = new_replies

    # Pass 2: full entry rewrites
    for entry in data:
        incoming = entry.get('incoming', '')
        if incoming in FULL_REWRITES:
            rewrite = FULL_REWRITES[incoming]
            for tone in ['romantic', 'sweet', 'funny', 'bold']:
                if tone in rewrite:
                    entry[tone] = rewrite[tone]
                    pass2_changes += 1

    # Save
    with open(DATASET_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Pass 1 (pattern fixes): {pass1_changes} reply changes")
    print(f"Pass 2 (full rewrites): {pass2_changes} tone sets rewritten")
    print(f"Total entries: {len(data)}")
    print(f"Dataset saved.")


if __name__ == '__main__':
    main()
