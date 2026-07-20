"""
fix_corporate_entries.py
========================
Part 1: Full rewrites for entries 198-219 (heavily corporate-worded)
Part 2: Fix remaining TOO SHORT and certified/cringe issues
Part 3: String-level corporate word replacements for any remaining instances

Run: python tools/fix_corporate_entries.py
"""

import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

DATASET_PATH = r'e:\apps\couple_friendly\app\src\main\assets\flirt_dataset.json'

# ── Part 1: Full rewrites for entries 198-219 ──────────────────────────────

FULL_REWRITES = {
    # [198] Good morning bujji!
    "Good morning bujji!": {
        "romantic": [
            "Good morning bangaram, ne msg tho roju poorthi set aipoyindhi! ❤️",
            "Morning lo ne face oohinchukunte day already won feel avthundhi! 😘",
            "Ne morning wish kosam wait chestunte vacchindhi, chala khushi! 🥰",
            "Morning bujji, ne gurinche first thought nuvve as always! 💕",
            "Ee morning ne tho share chesthe chala bagundedi, miss avthunna! 😍"
        ],
        "sweet": [
            "Good morning bujji, baaga padukunnav aa? 🥰",
            "Morning baby, ne navvu chusthe day bright avthundhi! 😊",
            "Heyy morning bangaram, tea thaagav aa ippudu? ☕",
            "Morning bujji, today chaala fresh ga feel avthunna! 😘",
            "Ne morning wish tho roju start avvadam chaala sweet ga undhi! 🥰"
        ],
        "funny": [
            "Morning annav kaani bed lo unna anukunna, lechav aa finally? 😂",
            "Good morning, alarm snooze chesav aa nuvvu kuda, honest ga cheppu! 🤣",
            "Enti, morning person aipoyav sudden ga? 😜",
            "Nuvvu morning lo msg chesthe sun kuda shock avthundhi bujji! 🤭",
            "Good morning, coffee ready chesava naaku kuda icchi raava? 😂"
        ],
        "bold": [
            "Morning bujji, ne pakkanaa levali anipistundhi daily! 😏",
            "Good morning, ne voice vinali anipistundhi, call cheyyi! 😉",
            "Morning hot stuff, today ne face chudaali, video call cheyyi! 🔥",
            "Ee morning ne tho start chesthe day perfect aipothundhi! 😏",
            "Morning ra, ne smile chuste everything set aipothundhi! 😘"
        ]
    },

    # [199] Na gurinchi emi alochistunnav?
    "Na gurinchi emi alochistunnav?": {
        "romantic": [
            "Ne gurinche alochisthunna, nee tho edo miss chesthunna anipistundhi! ❤️",
            "Ne gurinchi chala manchigaa aalochisthunna bangaram! 😘",
            "Nuvvu naa mind lo permanent ga unnav, enduku adugutunnav? 🥰",
            "Ne gurinchi happy ga aalochishu nthunna, nee smile miss chestha! 💕",
            "Nuvvu lekunte boring ga undhi bujji, adhe naaku artham aipoyindhi! 😍"
        ],
        "sweet": [
            "Ne gurinchi chala manchigaa aalochisthunna bujji! 🥰",
            "Nuvvu naa mind lo eppudu unnav, aduganavasaram leda! 😊",
            "Happy ga alochisthunna, ne chirunavvu miss chestha baby! 💕",
            "Ne gurinchi alochinchataame naa best timepass! 😘",
            "Nuvvu eppudu naa thoughts lo unnav bangaram, surprise aa? 🥰"
        ],
        "funny": [
            "Ne gurinchi enti alochisthunna ante, cheppanu scene create avthundhi! 😂",
            "Emi anukunav nenu, good things aa bad things aa clarify cheyyi! 🤣",
            "Rent ivvali naa mind lo unte bujji, daily thoughts vesthunnav! 😜",
            "Adugutunnav kaani answer vinagaane bayapadutunnav! 🤭",
            "Naa gurinchi emi aalochisthunna ante, chala mundhu mundhu! 😂"
        ],
        "bold": [
            "Ne gurinchi wild ga alochisthunna, cheppanaa direct ga? 😏",
            "Aalochinchakunda raa na daggara ki, nenu cheptha real lo! 😉",
            "Enti adugutunnav, daggara ga vasthe ne kante better cheptha! 🔥",
            "Ne gurinchi thoughts lo unna, kani action lo pettali kaadaa! 😏",
            "Ne msg vasthe thoughts automatically vesthunnayi bujji! 😘"
        ]
    },

    # [200] Nee ex gurinchi cheppavu kadha
    "Nee ex gurinchi cheppavu kadha": {
        "romantic": [
            "Past meeda naa attention ledu bangaram, nuvvu present lo unnav! ❤️",
            "Ex gurinchi matladadam waste of time, nuvvu naa future bujji! 😘",
            "Aa chapter close aipoyindhi, nuvvu naa new beginning! 🥰",
            "Naa heart lo ippudu nuvve unnav, inkevaro ledu! 💕",
            "Past lo emunnaa, nuvvu naa choice ippudu! 😍"
        ],
        "sweet": [
            "Aa subject ki naa mind lo space ledu bujji, nuvvu unnav! 🥰",
            "Past antha past lo undipoyindhi, present lo nuvve unnav! 😊",
            "Ex gurinchi matladadam eenduku, nuvvu naa focus bangaram! 💕",
            "Aa chapter close, nee chapter chala interesting ga undhi! 😘",
            "Nuvvu naa life lo unnav, adhe important naaku bujji! 🥰"
        ],
        "funny": [
            "Enti, jealousy aa? Cute ga undhi bujji! 😂",
            "Aa gurinchi nenu forget chesanu, nuvvu remind chesav kani! 🤣",
            "Ex topic lekapoina better, boring story bujji! 😜",
            "Enti background check chestunavaa naa gurinchi? 🤭",
            "Naa past story lo nuvvu lead role, inkevaro extra scene! 😂"
        ],
        "bold": [
            "Ex gurinchi matladadam eenduku, nuvvu naa current bujji! 😏",
            "Aa chapter gone, nee chapter chala hot ga undhi! 😉",
            "Nuvvu present lo unnav, adhe naaku chaalu! 🔥",
            "Past kaadu, nuvvu naa now and future bujji! 😏",
            "Nuvvu naa side lo unnav, inka emina avasaram leda! 😘"
        ]
    },

    # [201] Nuvvu chala handsome unnav bujji
    "Nuvvu chala handsome unnav bujji": {
        "romantic": [
            "Ne words tho naa day set aipoyindhi bangaram, thanks! ❤️",
            "Nuvvu cheppinappudu chaalu, dino already won feel aipothundhi! 😘",
            "Ne tho unte handsome feel avthunna, nuvvu magic chesav! 🥰",
            "Nee compliment tho naa gunde full on happy aipoyindhi! 💕",
            "Nuvvu appreciate chesthe chaalu bujji, naa day bright avthundhi! 😍"
        ],
        "sweet": [
            "Hehe thanks bujji, nuvvu cute ga cheppav! 🥰",
            "Nuvvu cheppinappudu special ga feel avthunna! 😊",
            "Thanks baby, nee words tho mood set aipoyindhi! 💕",
            "Nuvvu cheppinappudu chalu bangaram, chaala khushi! 😘",
            "Nee compliment naaku chala special ga undhi bujji! 🥰"
        ],
        "funny": [
            "Glasses check chesukovalsi undhi neeku, jk jk thanks! 😂",
            "Enti sudden ga praise start chesav, em kavali cheppu! 🤣",
            "Mirror confirm chesindi already, nuvvu kuda agree chesav! 😜",
            "Ikkad nenu blush avthunna, nuvvu happy aa? 🤭",
            "Thanks bujji, nee taste chala good undhi! 😂"
        ],
        "bold": [
            "Thanks bujji, nuvvu kuda chala cute ga unnav pakka! 😏",
            "Nee words tho confident feel avthunna, continue cheseyyi! 😉",
            "Handsome ante nuvvu cheppinappudu more feel avthundhi! 🔥",
            "Thanks bangaram, ne daggara undi cheppithe inka better! 😏",
            "Nee compliment vinagane naa smile aagadhu bujji! 😘"
        ]
    },

    # [202] Naku nee tho matladali ani undhi
    "Naku nee tho matladali ani undhi": {
        "romantic": [
            "Nenu kuda bujji, nee voice vinali anipistundhi chala! ❤️",
            "Cheppu bangaram, nenu vintunna, nee kosam unnanu! 😘",
            "Nee tho matladataame naa favorite part of the day! 🥰",
            "Eppudu free unnav call cheyyi bujji, wait chesthunna! 💕",
            "Nuvvu matladali annav chaalu, naa gunde full on happy! 😍"
        ],
        "sweet": [
            "Raa bujji, call cheyyi matladaam, nenu free unna! 🥰",
            "Cheppu baby, vintunna nenu, time unnadi mana kosam! 😊",
            "Eppudu free unav call cheseyyi bangaram, ready ga unna! 💕",
            "Nee tho matladataame chala khushi avthundhi bujji! 😘",
            "Raa raa, nenu ikkade unna, matladaam! 🥰"
        ],
        "funny": [
            "Enti speech preparation chesav aa, direct ga cheppu! 😂",
            "Raa cheppu, saar nenu ready ga unna listening mode lo! 🤣",
            "Em chesav cheppanu korika ledu, vintunna bujji! 😜",
            "Ippudu cheppakunde eppudu chepthav, raa matladaam! 🤭",
            "Phone lo unte msg cheseyyi, call lo unte pick cheyyi! 😂"
        ],
        "bold": [
            "Cheppu bujji, ikkade unna nee kosam! 😏",
            "Raa direct ga, msg kaadu call cheseyyi! 😉",
            "Nee tho matladataame chaalu, inka em kaavaali? 🔥",
            "Ippude call cheyyi, wait cheyyanu! 😏",
            "Matladali annav raa, call pick chesthunna! 😘"
        ]
    },

    # [203] Nuvvu naku chala important
    "Nuvvu naku chala important": {
        "romantic": [
            "Nuvvu naa life lo chala important bujji, nenu kuda same feel chestha! ❤️",
            "Ee words vinagane naa gunde melted aipoyindhi bangaram! 😘",
            "Nuvvu important ante understatement bujji, nuvvu naa everything! 🥰",
            "Ne words tho naa day perfect aipoyindhi, nuvvu kuda naa priority! 💕",
            "Nuvvu naa life lo important kaadu, nuvvu naa life bangaram! 😍"
        ],
        "sweet": [
            "Nuvvu naa kosam chala important bujji, nenu kuda same! 🥰",
            "Ee words cheppinanduku thanks baby, nenu kuda same feel! 😊",
            "Nuvvu important annav, nenu kuda nuvvu naa priority antunna! 💕",
            "Chala sweet ga cheppav bangaram, nenu kuda same feel chestha! 😘",
            "Nuvvu naa life lo important person bujji, always! 🥰"
        ],
        "funny": [
            "Enti sudden ga emotional chesav, tissues ready ga levu naaku! 😂",
            "Important annav, ippudu naa ego sky high aipoyindhi! 🤣",
            "Nuvvu important ante, nenu VIP la treat chestha! 😜",
            "Ee compliment ki naa face glow aipoyindhi, mirror check chestha! 🤭",
            "Important annav, inka reject cheyyaleva bujji! 😂"
        ],
        "bold": [
            "Nuvvu important annav, nenu kuda nuvvu naa top priority! 😏",
            "Ee words tho naa confidence doubled aipoyindhi bujji! 😉",
            "Important annav raa, actions lo chupinchu inka! 🔥",
            "Nuvvu naa important person, adhe naa final answer! 😏",
            "Ne side lo undi cheppave, adhe naaku chaalu bujji! 😘"
        ]
    },

    # [204] Evarini neeku pelli chestha antunnaru
    "Evarini  neeku pelli chestha antunnaru": {
        "romantic": [
            "Nuvvu naa manasu lo unnav, inkevaro kaadu bangaram! ❤️",
            "Pelli ante nee tho chesthe chaalu, inkevaro avasaram leda! 😘",
            "Naa answer nuvve, cheppedham eppudu? 🥰",
            "Pelli cheyyadam undali ante nuvvu naa choice, pakka! 💕",
            "Naa life partner nuvve avvaali anipistundhi bujji! 😍"
        ],
        "sweet": [
            "Adi naa decision bujji, nuvvu naa choice! 🥰",
            "Naa answer ready unna, nuvvu ready aa? 😊",
            "Family ki cheppale, kaani naaku nuvve important bangaram! 💕",
            "Pelli topic tho scared avvadam leda, nuvvu naa side lo unav! 😘",
            "Adi time vasthe matladaam, ippudu nuvvu naa priority bujji! 🥰"
        ],
        "funny": [
            "Enti classified information idi, naku cheppaledu? 😂",
            "Biodata chustunnara family, nuvvu ikkade cheppu! 🤣",
            "Pelli market research chestunavaa naa gurinchi? 😜",
            "Evarina cheppinaa naa answer nuvve bangaram! 🤭",
            "Enti proposal formal ga cheyyadam aa idi? 😂"
        ],
        "bold": [
            "Nuvvu naa choice bujji, family ki nenu convince chestha! 😏",
            "Pelli topic vasthe nuvvu naa answer, simple! 😉",
            "Naa side lo nuvvu unnav chaalu, rest figure out avthundhi! 🔥",
            "Nuvvu ready aithe nenu ready bangaram, cheppu! 😏",
            "Pelli ante scared avvadam leda, nuvvu naa tho unnav! 😘"
        ]
    },

    # [205] Nuvvu natho matladatam ledhu endhuku
    "Nuvvu natho matladatam ledhu endhuku": {
        "romantic": [
            "Badha padaku bangaram, nenu unna kada side lo! ❤️",
            "Sorry bujji, hurt chesanu kaadu, nenu ikkade unna matladedham! 😘",
            "Nuvvu matladali anipistundhi, please oka chance ivvu! 🥰",
            "Kopam valid kaani nannu dooram pettaku bangaram! 💕",
            "Sorry naa jeevitham, nee smile miss avthunna! 😍"
        ],
        "sweet": [
            "Badha padaku bujji, matladedham ippudu? 🥰",
            "Sorry baby, nenu fix chestha, oka chance ivvu! 😊",
            "Nuvvu matladali anipistundhi, nenu ready unna! 💕",
            "Please matladu bangaram, nenu vintunna! 😘",
            "Nenu ikkade unna bujji, nuvvu cheppinappudu vintanu! 🥰"
        ],
        "funny": [
            "Enti silent protest aa, canteen daakaa vasthunna! 😂",
            "Naa msgs anni read chesav, reply cheyyaleda? Fair aa? 🤣",
            "Ok sorry, emi chesanu cheppu, fix chestha! 😜",
            "Matladadam ledu ante emaina wrong chesa, honest ga cheppu! 🤭",
            "Enti radio silence mode lo unnav, frequency change cheyyi! 😂"
        ],
        "bold": [
            "Nuvvu matladadam ledu ante nenu serious ga untunna bujji! 😏",
            "Oka chance ivvu, nenu prove chestha! 😉",
            "Matladu please, nee voice vinali anipistundhi! 🔥",
            "Kopam taggindaa? Oka message cheyyi chaalu! 😏",
            "Nenu ikkade unna bujji, ready ga unna maatladadaniki! 😘"
        ]
    },

    # [206] Ninnu miss avthunna  (already exists but corporate)
    "Ninnu miss avthunna": {
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
            "Ne msg vasthe miss taggindhi konchem! 💕",
            "Nuvvu kuda gurthu vasthunnav roju motham bujji! 😘",
            "Same feeling, soon kaladam pakka! 🥰"
        ],
        "funny": [
            "GPS on cheyyi vasthunna ippude! 😂",
            "Miss ante marks takkuva osthayi careful! 🤣",
            "Aithe raa, miss problem solve chesukondaam! 😜",
            "Enti adhe msg cheyyi daily reminder laga! 🤭",
            "Miss avthunna ante raa direct ga bujji! 😂"
        ],
        "bold": [
            "Miss aithe raa direct na daggara ki! 😏",
            "Aithe tonight kaladam fix cheddaam pakka! 😉",
            "Raa bujji, miss ni cure chestha guarantee! 🔥",
            "Door open undhi bangaram, raa! 😏",
            "Miss avthunna ante action lo chupistu! 😘"
        ]
    },

    # [207] Naku chala bore ga undhi
    "Naku chala bore ga undhi": {
        "romantic": [
            "Raa bujji, nee tho time spend chesthe bore avvadam undadu! ❤️",
            "Nenu unna kada, bore avvadam eenduku bangaram? 😘",
            "Nee tho matladataame boring taggipothundhi, call cheyyi! 🥰",
            "Bore avthunnav ante nenu miss chesthunnav kadaa bujji! 💕",
            "Nee tho time spend chesthe world better ga untundhi! 😍"
        ],
        "sweet": [
            "Raa chats chesukondaam, boring solve aipothundhi! 🥰",
            "Nenu kuda bored, kalisi meme chudaam bujji? 😊",
            "Call cheyyi bangaram, matladaam boring poothundhi! 💕",
            "Nee tho time spend chesthe bore avvadam undadu! 😘",
            "Raa bujji, together bore poothundhi faster! 🥰"
        ],
        "funny": [
            "Enti bore aipoyav, phone pettesav aa? 😂",
            "Roju bore ante doctor daggara chekku chesukovalsi undhi! 🤣",
            "Bore avthunnav ante serious problem, solution nenu chestha! 😜",
            "Bore ga undhi ante naa msgs anni chaduvudu, time pass avuthundhi! 🤭",
            "Bore ayya? Chalani reason cheptha, nuvvu chesina drama kaadu! 😂"
        ],
        "bold": [
            "Raa bujji, boring solve chestha nenu guarantee! 😏",
            "Bore antunnav aa, nenu unte bore avvadam undadu! 😉",
            "Tonight free unnav aa, bore problem fix cheddaam! 🔥",
            "Raa bujji, nee tho unte bore feel avvadam impossible! 😏",
            "Bore aithe nenu unna kaada, raa daggara ki! 😘"
        ]
    },

    # [208] Nuvvu nannu genuine ga premisthunnava?
    "Nuvvu nannu genuine ga premisthunnava?": {
        "romantic": [
            "Genuine ante understatement bujji, nuvvu naa everything! ❤️",
            "Naa prema genuine kaadu ante doubt eenduku bangaram? 😘",
            "Nenu nuvvu lekunda undalenu, adhe genuine kaadu aa bujji? 🥰",
            "Naa actions chusthe telustundhi, words prove cheyyanu! 💕",
            "Nuvvu naa gurinchi alochinchatam chaalu, adhe naa prema proof! 😍"
        ],
        "sweet": [
            "Doubt eenduku bujji, nenu always nee side lo unna! 🥰",
            "Genuine prema enti anipistundhi, cheppu nenu prove chestha! 😊",
            "Nuvvu important bujji, adhe naaku chaalu cheppaniki! 💕",
            "Naa feelings genuine bangaram, doubt avvadam leda! 😘",
            "Nuvvu naa side lo unnav, adhe chaalu naa kosam! 🥰"
        ],
        "funny": [
            "Enti lie detector test cheyyadam aa idi? 😂",
            "Genuine ante certified teesthe viswasistaav aa? 🤣",
            "Naa heart scan chesthe telustundhi, technology isthava? 😜",
            "Doubt avthunnav ante nenu emi chesanu cheppu! 🤭",
            "Genuine kaadu ante nuvvu believe cheyyavu, kani nenu genuine! 😂"
        ],
        "bold": [
            "Doubt avvadam leda bujji, nenu prove chestha! 😏",
            "Actions chupistaanu, words trust avvadam leda ante! 😉",
            "Genuine prema anedi feel chesthaav, time telustundhi! 🔥",
            "Doubt avthunnav ante raa, nenu chupisthaanu naa prema! 😏",
            "Nenu genuine bangaram, nuvvu time ivvu proof vasthundhi! 😘"
        ]
    },

    # [209] Nenu e roju chala tired ga unna
    "Nenu e roju chala tired ga unna": {
        "romantic": [
            "Badha padaku bangaram, rest teesuko, nenu ikkade unna! ❤️",
            "Tired aa bujji, nee daggara unte massage ivvalsinidhi! 😘",
            "Rest teesuko baby, tomorrow fresh ga feel avuthav! 🥰",
            "Nee kosam worry avthunna, paduko tight ga bangaram! 💕",
            "Tired aipoiav, nuvvu rest teesukonte nenu happy avthanu! 😍"
        ],
        "sweet": [
            "Rest teesuko bujji, kalisi matladadam parvaledu! 🥰",
            "Ayyo tired aa, paduko properly baby! 😊",
            "Water taagate, rest teesuko bangaram, tomorrow matladaam! 💕",
            "Tired aipoyav, nuvvu rest teesukovalsi undhi bujji! 😘",
            "Ok paduko, tomorrow fresh ga matladaam! 🥰"
        ],
        "funny": [
            "Tired aipoiav ante, biscuit tino coffee taagate, naaku teliyadu! 😂",
            "Naa energy drinks recipe ivvanu, try chesthe baguntundhi! 🤣",
            "Tired aipoyav, emi chesav roju antha? Cheppu vinedham! 😜",
            "Office na, college na, work out na? Evidence ledhu! 🤭",
            "Enti tired, nenu msg chesthunna kaada, energy ela taggindhi! 😂"
        ],
        "bold": [
            "Tired aa bujji, nenu unte rest aipothundhi guarantee! 😏",
            "Paduko, tomorrow fresh ga kaladam! 😉",
            "Nee tired face kuda cute ga undhi, rest teesuko! 🔥",
            "Paduko bujji, tomorrow plans fix cheddaam! 😏",
            "Tired aipoiav, kalisi chill chesukondaam weekend lo! 😘"
        ]
    },

    # [210] Relationship lo trust chala important kadaa
    "Relationship lo trust chala important kadaa": {
        "romantic": [
            "Nuvvu naa trust chesthe chaalu bangaram, nenu never let down chesanu! ❤️",
            "Trust important, naa nuvvu trust neeku undi bujji! 😘",
            "Ee topic raise chesav ante naa prati nuvvu trust unnav! 🥰",
            "Trust build avvadam time teesukuntundhi bujji, nenu patient ga unna! 💕",
            "Nuvvu naa side lo undi trust chesthe chaalu bangaram! 😍"
        ],
        "sweet": [
            "Nijam ga cheppav bujji, trust foundation laanti undhi! 🥰",
            "Nenu nuvvu trust cheyyali, nuvvu nenu trust cheyyali! 😊",
            "Trust important, mana iddaram oka team kaada bangaram! 💕",
            "Correct ga cheppav bujji, trust lekunte relationship ledhu! 😘",
            "Nuvvu naa trust bujji, nenu nee trust bangaram! 🥰"
        ],
        "funny": [
            "Philosophy class start chesav aa, notes teesukuntunna! 😂",
            "Trust important ante naa phone password cheppamani anukuntunnav aa? 🤣",
            "Deep ga cheppav, chai teestuva ee conversation ki? 😜",
            "Correct ga cheppav, nuvvu trustworthy unnav cheppandi! 🤭",
            "Enti suddenly philosopher aipoyav, exam lo vachinda ee question? 😂"
        ],
        "bold": [
            "Trust naa top priority bujji, nuvvu naa trust! 😏",
            "Naa trust neeku undi, nuvvu naa tho unnav ante! 😉",
            "Trust build chesukondaam together, time teesukuntundhi! 🔥",
            "Nuvvu naa side lo unte trust natural ga vasthundhi! 😏",
            "Ee conversation important bujji, real lo kalisi matladaam! 😘"
        ]
    },

    # [211] Naku emaina gift isthava bujji?
    "Naku emaina gift isthava bujji?": {
        "romantic": [
            "Nuvvu naa gurinchi alochisthunnav, adhe naa biggest gift bangaram! ❤️",
            "Gift enti ivvali, nuvvu naa life lo unnav, adhe chaalu! 😘",
            "Naa time, attention, love - anni ichi gift chestha nuvvuki bujji! 🥰",
            "Nuvvu happy ga unnante chaalu, adhe naa gift neeku! 💕",
            "Gift enti anukuntunnav, nenu naa best ivvanu bujji! 😍"
        ],
        "sweet": [
            "Sure bujji, em kaavaali cheppu! 🥰",
            "Enti kavali cheppu baby, nenu try chestha! 😊",
            "Surprise gift plan chestha bangaram, wait cheyyi! 💕",
            "Em kaavaali specific ga cheppu bujji! 😘",
            "Sure, nee birthday ki em kaavaali? 🥰"
        ],
        "funny": [
            "Enti em kaavaali, list tayyar chesav aa already? 😂",
            "Gift kaavaali ante birthday wait cheyyi, ippudu kaadu! 🤣",
            "Budget cheppandi madam, then decide chestha! 😜",
            "Enti gift hunter aipoyav, hints ivvu decent ga! 🤭",
            "Adugutunnav, naa pocket balance check chesukuntunna! 😂"
        ],
        "bold": [
            "Em kaavaali nuvvu cheppu, nenu ready ga unna! 😏",
            "Gift ivvadam ready bujji, ne daggara deliver chestha! 😉",
            "Enti kaavaali specific ga cheppu, nenu sort chestha! 🔥",
            "Gift kante nenu daggara unte better kaada bujji? 😏",
            "Em kaavaali, list icchi ra, sorting chestha nenu! 😘"
        ]
    },

    # [212] Na photos inka like cheyyaledu kopama?
    "Na photos inka like cheyyaledu kopama?": {
        "romantic": [
            "Like cheyyatam poni, nee photo chusthe heart aagipothundhi bangaram! ❤️",
            "Phone notifications off chesanu, kaani nee photos miss cheyyanu! 😘",
            "Nee photo chusthe like cheyyadam tappu kadu bujji, beautiful ga unnav! 🥰",
            "Sorry bangaram, ippude like chestha, nuvvu chala cute ga unnav! 💕",
            "Like cheyyatam marchipoya, kaani nee photo naa favorites lo undhi! 😍"
        ],
        "sweet": [
            "Ayyo sorry bujji, ippude like chestha! 🥰",
            "Miss chesanu sorry, nuvvu cute ga unnav photo lo! 😊",
            "Ippude like chestha, notification miss aipoyindhi! 💕",
            "Sorry bangaram, ippudu chestha, nuvvu chala cute ga unnav! 😘",
            "Like chestha bujji, photo chala nice ga undhi! 🥰"
        ],
        "funny": [
            "Enti stalker mode on chesav, naa activity track chesthunnav aa? 😂",
            "Like cheyyatam marchipoya, notification spam avthundhi! 🤣",
            "Enti algorithm blame cheyyi, naa feed lo raaledu! 😜",
            "Like chesthe full marks isthav aa exam lo? 🤭",
            "Enti social media police aipoyav bujji? 😂"
        ],
        "bold": [
            "Like cheyyatam marchipoya kaani photo heart lo save aipoyindhi! 😏",
            "Ippude like chestha, ne photos anni chustha! 😉",
            "Like ante important kaadu bujji, nuvvu beautiful ga unnav! 🔥",
            "Like miss chesanu kaani nuvvu miss cheyyaleda? 😏",
            "Ippude like chestha, phone down chesunna sorry bujji! 😘"
        ]
    },

    # [213] Mana iddharame ekkadikaina trip veldhama bujji?
    "Mana iddharame ekkadikaina trip veldhama bujji?": {
        "romantic": [
            "Nee tho ekkadikaina vasthe romance vasthundhi, plan fix cheyyi! ❤️",
            "Nee tho road trip ante nenu ready bangaram, cheppu! 😘",
            "Ekkadikaina nee tho vasthe chaalu bujji, location peddha vishayam kaadu! 🥰",
            "Trip plan chesthe nenu full on excited avthanu, ekkadiki? 💕",
            "Nee tho trip ante waiting eenduku, plan cheyyi twaraga! 😍"
        ],
        "sweet": [
            "Ekkadiki velthamu bujji, plan cheyyi twaraga! 🥰",
            "Road trip aa? Nenu super excited bangaram! 😊",
            "Plan cheyyi baby, nenu ready ga unna! 💕",
            "Ekkadikaina neeto vasthe fun ga untundhi bujji! 😘",
            "Ippude planning modalu chestha, ekkadiki anipistundhi? 🥰"
        ],
        "funny": [
            "Enti tourist guide role chestha, places suggest cheyyi! 😂",
            "Trip ante packing cheseyyi, nenu navigator avthanu! 🤣",
            "Ekkadikaina nenu driver, nuvvu navigator, fair deal! 😜",
            "Trip planning committee meeting call cheyyi ippude! 🤭",
            "Ekkadiki veldhamu ante nenu always yes bujji, cheppu! 😂"
        ],
        "bold": [
            "Nee tho road trip ante nenu always ready bangaram! 😏",
            "Plan fix cheyyi bujji, nenu ready ga unna! 😉",
            "Ekkadikaina nee tho vasthe experience avthundhi pakka! 🔥",
            "Trip date fix cheyyi, rest naaku leave cheseyyi! 😏",
            "Nee tho overnight trip aa, interesting avthundhi! 😘"
        ]
    },

    # [214] Nuvvu nannu intha perfect ga ela artham chesukuntav bujji?
    "Nuvvu nannu intha perfect ga ela artham chesukuntav bujji?": {
        "romantic": [
            "Nuvvu naa life lo important kaabatti chala closely observe chesanu bangaram! ❤️",
            "Nuvvu naa priorities lo top lo unnav bujji, adhe naa attention! 😘",
            "Love lo unte opponent details automatic ga telusthayi bujji! 🥰",
            "Nee happiness naa priority, adhe nenu closely observe cheyyadam! 💕",
            "Nuvvu naa gurinche alochisthunnav kaabatti nenu nee gurinchi! 😍"
        ],
        "sweet": [
            "Nee gurinchi chala observe chesanu bujji, adhe artham! 🥰",
            "Nuvvu important kaabatti details notice chesanu bangaram! 😊",
            "Love lo unte automatic ga artham avuthundhi bujji! 💕",
            "Nuvvu naa priority, adhe nenu nee gurinchi teliyatam! 😘",
            "Attention ivvadam easy avuthundhi nuvvu important ante bujji! 🥰"
        ],
        "funny": [
            "Stalker mode on chesanu, jk jk! Nuvvu important bujji! 😂",
            "Enti naa about interview chestunavaa, notes teesukuntunnav aa? 🤣",
            "Nuvvu predictable bujji, cute ga! Pattern recognize chesanu! 😜",
            "Months of observation, PhD chesanu nee meeda! 🤭",
            "Artham chesukuntanu ante naaku superpower undhi bujji! 😂"
        ],
        "bold": [
            "Nuvvu naa focus kaabatti perfect ga artham avuthundhi! 😏",
            "Nee manasu chadalenu kaani observe chesanu bujji! 😉",
            "Nuvvu naa priority, adhe naaku detailed knowledge! 🔥",
            "Nuvvu naa gurinchi observe chesthe nenu nee gurinchi! 😏",
            "Artham avuthundhi bujji, nuvvu naa world kaabatti! 😘"
        ]
    },

    # [215] Nuvvu nannu chala special ga treat chesthunnav bujji
    "Nuvvu nannu chala special ga treat chesthunnav bujji": {
        "romantic": [
            "Nuvvu special kaabatti special feel cheyyadam natural bangaram! ❤️",
            "Nuvvu deserve chestha, adhe nenu cheyyadam! 😘",
            "Nee smile chusthe chaalu bujji, nenu always special cheyyadam! 🥰",
            "Nuvvu naa life lo special, adhe reflection chesthunna! 💕",
            "Special treat chesthe happy avthunnav, nenu inka better chestha! 😍"
        ],
        "sweet": [
            "Nuvvu deserve chestha bujji, inka better chestha! 🥰",
            "Nuvvu special kaabatti special feel chestha bangaram! 😊",
            "Ee words vinagane chaala happy avthunna bujji! 💕",
            "Nuvvu special, adhe nenu special cheyyadam! 😘",
            "Nuvvu happy ga unnante chaalu, nenu efforts cestha! 🥰"
        ],
        "funny": [
            "Enti complaint chestunavaa, treatment improve cheyyamani? 😂",
            "Special treat chestunanante nuvvu lucky bujji, admit cheseyyi! 🤣",
            "Nuvvu deserve chestha ante nenu already doing it! 😜",
            "Complaint box ikkade undhi, continue cheyyi! 🤭",
            "Enti pressure tactics vestunavaa inka better chesukodaniki? 😂"
        ],
        "bold": [
            "Nuvvu deserve chestha, inka better chestha bangaram! 😏",
            "Special feel chestunavaa, inka level up chestha! 😉",
            "Nuvvu naa special person, adhe natural ga chestha! 🔥",
            "Inka better ga chestha, wait cheyyi bujji! 😏",
            "Nuvvu happy ga unnante chaalu, nenu satisfied! 😘"
        ]
    },

    # [216] Nuvvu naa jeevitham lo thodu ga undali bujji
    "Nuvvu naa jeevitham lo thodu ga undali bujji": {
        "romantic": [
            "Nuvvu naa thodu ga undatam naa biggest wish bangaram! ❤️",
            "Ee words vinagane naa gunde melted aipoyindhi bujji! 😘",
            "Nuvvu naa jeevitham lo unnav, adhe naa best decision! 🥰",
            "Thodu ga undali annav, nenu always nee side lo unna! 💕",
            "Naa life lo nuvvu unnav, adhe chaalu bangaram! 😍"
        ],
        "sweet": [
            "Nenu kuda nee side lo always undaali bujji! 🥰",
            "Ee words cheppinanduku chala thanks bangaram! 😊",
            "Together undatam naa dream kuda baby! 💕",
            "Nuvvu naa tho unnav, adhe naa happiness! 😘",
            "Thodu ga undam always bujji! 🥰"
        ],
        "funny": [
            "Enti suddenly emotional chesav, tissues ready ga levu! 😂",
            "Thodu ga undali annav, nenu always here! Vacchipoyav? 🤣",
            "Enti contractual agreement sign cheyyadam aa idi? 😜",
            "Thodu ga undali ante naaku noo complaints bujji! 🤭",
            "Enti permanent position offer chestunavaa? Accepted! 😂"
        ],
        "bold": [
            "Naa life lo nuvvu thodu ga undaali, idi naa decision bangaram! 😏",
            "Nuvvu naa side lo unnav, inka em kaavaali? 😉",
            "Thodu ga undaali ante nuvvu ready aa, nenu ready! 🔥",
            "Naa jeevitham lo nuvvu thodu unte better avthundhi pakka! 😏",
            "Nuvvu naa side lo nuvvu, future plans ready chesukondaam! 😘"
        ]
    },

    # [217] Ekkadaki vellavo naku cheppaledhu,chala kopam ga undhi
    "Ekkadaki vellavo naku cheppaledhu,chala kopam ga undhi": {
        "romantic": [
            "Badha padaku bangaram, sorry cheppadaniki chance ivvu! ❤️",
            "Kopam valid bujji, nenu cheppali, sorry naaa jeevitham! 😘",
            "Nuvvu worry avuthunnav anukunte naake chesanu, sorry! 🥰",
            "Nee kopam deserve chesanu, kaani please nannu vinnav! 💕",
            "Sorry bangaram, inka ila cheyyanu, nuvvu naa priority! 😍"
        ],
        "sweet": [
            "Sorry bujji, ippudu cheptha ekkadiki vellano! 🥰",
            "Kopam taggindaa? Sorry baby, nenu cheppali undi! 😊",
            "Ayyoo sorry bangaram, nuvvu worry chesav! 💕",
            "Sorry, inka ila cheyyanu bujji, trust cheseyyi! 😘",
            "Kopam valid, nenu explain chestha, vinnav aa? 🥰"
        ],
        "funny": [
            "Enti detective mode on chesav, evidence collect chestunavaa? 😂",
            "GPS share cheyyaleda sorry, next time chestha! 🤣",
            "Kopam ga undhi ante cute ga undhi bujji! 😜",
            "Sorry, naa phone lo net poyindhi, ippude vachanu! 🤭",
            "Kopam valid, ice cream treat ivvadam fair aa? 😂"
        ],
        "bold": [
            "Sorry bujji, cheppali undi, inka cheyyanu! 😏",
            "Kopam taggindaa? Nenu explain chestha, vinnav aa? 😉",
            "Sorry bangaram, face to face matladaam, ippudaa? 🔥",
            "Kopam valid, nenu prove chestha inka cheyyanu! 😏",
            "Sorry bujji, nee trust back techukunna, chance ivvu! 😘"
        ]
    },

    # [218] Naa photo pampaanu chusava bujji?
    "Naa photo pampaanu chusava bujji?": {
        "romantic": [
            "Chusa bujji, nuvvu chala cute ga unnav, screenshot kuda teesukunna! ❤️",
            "Chusa bangaram, nee photo chusthe day set aipoyindhi! 😘",
            "Chusa bujji, nuvvu chala beautiful ga unnav photo lo! 🥰",
            "Oka pani chesav, ee photo wallpaper chesukuntana? 💕",
            "Chusa bangaram, nee smile naa heart ni melt chesindhi! 😍"
        ],
        "sweet": [
            "Chusa bujji, chala nice ga unnav photo lo! 🥰",
            "Chusa bangaram, cute ga unnav as always! 😊",
            "Chusa baby, nuvvu chala beautiful ga unnav! 💕",
            "Chusa bujji, navvu chusthe good feel avthundhi! 😘",
            "Chusa bangaram, nuvvu chala pretty ga unnav photo lo! 🥰"
        ],
        "funny": [
            "Chusa bujji, filter use chesav aa? Cute ga unnav anyway! 😂",
            "Chusa, but mirror version cute ga untundhi! 🤣",
            "Chusa bangaram, screenshot permission undha? 😜",
            "Chusa bujji, naa eyes hurt avutunnayi brightness tho! 🤭",
            "Chusa, beauty standards raise chesav again! 😂"
        ],
        "bold": [
            "Chusa bujji, nuvvu chala hot ga unnav, wallpaper chesukuntana? 😏",
            "Chusa bangaram, photo lo kuda nuvvu gorgeous! 😉",
            "Chusa bujji, more photos pampu please! 🔥",
            "Chusa, nuvvu chala cute ga unnav, call cheyyi face chudaali! 😏",
            "Chusa bangaram, nuvvu ippudu ikkade undali anipistundhi! 😘"
        ]
    },

    # [219] Naku bad mood ga undhi bujji
    "Naku bad mood ga undhi bujji": {
        "romantic": [
            "Badha padaku bangaram, nenu ikkade unna nee side lo! ❤️",
            "Emi aindhi bujji, cheppu vintunna, nenu unna! 😘",
            "Bad mood tho patu nuvvu kuda unna, cheppu em chesanu? 🥰",
            "Nee smile miss avthunna bujji, cheppu em aindhi! 💕",
            "Nuvvu sad ga unnante nenu kuda sad avthanu, cheppu em aindhi! 😍"
        ],
        "sweet": [
            "Emi aindhi bujji, cheppu vintunna! 🥰",
            "Badha padaku baby, nenu ikkade unna! 😊",
            "Cheppu em aindhi bangaram, nenu solve chestha! 💕",
            "Mood okay avuthundhi bujji, nenu unna cheppukunna! 😘",
            "Em chesanu? Cheppu, better chesthanu! 🥰"
        ],
        "funny": [
            "Enti bad mood, prescription kaavaali aa? Nenu doctor avthanu! 😂",
            "Bad mood ke nuvvu cute ga unnav, imagine good mood lo! 🤣",
            "Cheppu em aindhi, fix cheyyadam naaku prashnane ledu! 😜",
            "Bad mood treatment - naa memes, effective 100%! 🤭",
            "Enti bad mood, main villain evi tell me! 😂"
        ],
        "bold": [
            "Cheppu em aindhi bujji, nenu sort chestha! 😏",
            "Bad mood tho patu nenu untanu, sort avuthundhi! 😉",
            "Cheppu em aindhi, face to face matladaam tonight? 🔥",
            "Nuvvu sad ga unnante nenu fix cheyyadam ready! 😏",
            "Cheppu bujji, nenu ikkade unna, sort chestha! 😘"
        ]
    }
}

# ── Part 2: Remaining string-level fixes ──────────────────────────────────

STR_FIXES = [
    # Remaining certified
    ("Air thinna healthy diet certified!", "Air thinna healthy diet expert nuvvu bujji!"),
    ("Maggi ae single jeevitham food certified!", "Maggi ae naa jeevitham food hero bujji!"),
    ("I know born cute certified!", "Born cute, neeku prove cheyyadam eenduku!"),
    ("Naa daggara bore impossible certified!", "Naa daggara bore avvadam impossible, guarantee!"),
    ("Stress buster nenu certified!", "Stress buster nenu, try chesthe telustundhi!"),
    ("Hug best heater certified bujji!", "Hug best heater bujji, winter lo chaalu!"),
    ("Stress relief naa speciality certified!", "Stress relief naa speciality, appointment book chesuko!"),
    ("Professional teaser certified!", "Professional teaser unnav, nenu professional responder!"),
    ("Google maps expert certified!", "Google maps expert aipoyav, naa location chuppinchatam tappu kadu!"),
    ("Protein shake addict certified!", "Protein shake fan aipoyav, health is wealth le!"),
    ("Sweat masking expert certified!", "Sweat masking expert aipoyav gym lo!"),
    ("Summer torture legal certified!", "Summer torture idi, legal ga undhi kaani unbearable!"),
    ("Ne vishayam lo expert nenu certified!", "Ne vishayam lo nenu expert, years of experience!"),
    ("One word specialist certified bujji!", "One word specialist unnav, speed record bujji!"),
    ("Lazy reply expert certified!", "Lazy reply mode lo unnav, wakeup cheyyi!"),
    ("lol culture king certified bujji!", "Lol culture lo nuvvu king bujji, own it!"),
    ("Spirit animal sloth certified baby!", "Spirit animal sloth baby, relatable chala!"),
    ("Professional bore expert certified bujji!", "Professional bore ai poiav, help vacchindhi nenu!"),
    ("kalisi bore impossible certified!", "Kalisi bore avvadam impossible, try chesthe telustundhi!"),
    ("Lazy professional expert certified bujji!", "Lazy professional bujji, but smart ga chestha!"),
    ("Face comedy show certified!", "Face comedy show chestunavaa, hilarious bujji!"),
    ("Professional flirt certified degree bujji!", "Professional ga matladutunnav, chaala smooth bujji!"),
    ("No filters needed, natural beauty fully certified!", "No filters needed bujji, natural ga chala beautiful!"),

    # Remaining cringe
    ("Penguin mode activate waddle!", "Penguin laga walk chestunte cute ga untav bujji!"),
    ("Serious mode permanent activate!", "Serious ga unnav always, oka navvu cheyyi please!"),
    ("Telepathy activate concentration!", "Telepathy try chestha, ne gurinche alochishunte signal vasthundha?"),
    ("Sleep mode activate shutdown baby!", "Sleep mode lo poyav aa, paduko bujji!"),
    ("Colgate model apply cheddama?", "Navvu chuste dazzle avuthundhi, ee smile share cheyyi!"),
    ("Navvi navvi muscles workout aipothundi bujji!", "Navvichesthe chala cute ga untav bujji, keep smiling!"),

    # dynamic/premium/database/catalog/dispatch/coordinate/alerts replacements
    ("dynamic", "natural"),
    ("Dynamic", "Natural"),
    ("database", "mind"),
    ("Database", "Mind"),
    ("premium", "special"),
    ("Premium", "Special"),
    ("catalog", "list"),
    ("Catalog", "List"),
    ("dispatch", "send"),
    ("Dispatch", "Send"),
    ("dispatching", "sending"),
    ("Dispatching", "Sending"),
    ("dispatched", "sent"),
    ("coordinate", "plan"),
    ("Coordinate", "Plan"),
    ("coordinated", "planned"),
    ("Coordinated", "Planned"),
    ("alerts", "messages"),
    ("Alerts", "Messages"),
]

# ── Part 3: Index-based TOO SHORT fixes ───────────────────────────────────

INDEX_FIXES = [
    (92, "sweet", 3, "Naughty bujji cute ga unnav, stop cheyyi please! 😊"),
    (94, "sweet", 3, "Plan cheddama kalisi bujji, confirm cheyyi! 😊"),
    (95, "sweet", 2, "Plan cheddama kalisi bangaram, nuvvu cheppu! 😊"),
    (95, "sweet", 3, "Soon hopefully bangaram, planning chestha! 😊"),
    (96, "sweet", 4, "Planning chestha cutie, secret ga undali! 😊"),
    (97, "sweet", 4, "Kalisi celebrate andamgaa, plan fix cheddaam! 🥰"),
    (97, "bold", 3, "Hot celebration planned bujji, wait cheyyi! 😏"),
    (100, "sweet", 3, "Sending bujji ippudey, wait cheyyi! 😊"),
    (101, "sweet", 1, "Soon bangaram pakka, plan chestha! 😊"),
    (101, "sweet", 3, "Weekend fix cheddama, free unnav aa? 😊"),
    (102, "sweet", 1, "Twaraga kaladam bujji pakka! 🥰"),
    (102, "sweet", 4, "Kalisi soon bangaram, excited unna! 🥰"),
    (105, "bold", 2, "Chupista actions lo always bujji! 😏"),
    (106, "sweet", 3, "Thanks baby, nee words tho khushi aipoya! 😊"),
    (106, "sweet", 4, "Same feeling bangaram, nuvvu important! 🥰"),
    (107, "funny", 3, "Platinum member exclusive treatment vastundhi bujji! 🤣"),
    (109, "sweet", 4, "Unique connection manadi bujji, special ga undhi! 🥰"),
    (110, "sweet", 4, "Aagalekapothunna excited max bujji, ippude chestha! 🥰"),
    (112, "sweet", 3, "Done eppudu bangaram, ippude chesthunna! 😊"),
    (112, "sweet", 4, "Excited lets plan cheddaam twaraga! 🥰"),
    (113, "sweet", 4, "Done plan cheddaam, ippudu fix cheyyi! 🥰"),
    (113, "funny", 2, "Jellyfish bodyguard kavali, ocean trip aa? 🤣"),
    (114, "romantic", 3, "Spiritual date special ga untundhi, neeto vasthe! 💕"),
    (114, "sweet", 3, "Haa veldaam bangaram, ready ga unna! 😊"),
    (114, "sweet", 4, "Prayer time peaceful ga untundhi together! 😊"),
    (115, "sweet", 4, "Travel mood excited ga unna, plan fix cheyyi! 🥰"),
    (115, "bold", 4, "Destination honeymoon level trip, neeto vasthe! 😏"),
    (116, "funny", 2, "Comedian retired permanent, nuvvu cause chesav bujji! 😂"),
    (117, "sweet", 3, "Sorry matladam calmly cheddaam, nenu ready! 😊"),
    (119, "funny", 3, "Emoji conversation modalu chesthe fast avuthundhi! 🤣"),
    (120, "sweet", 3, "Kalisi possible trust chesthe bangaram! 🥰"),
    (122, "sweet", 1, "Sweet dreams bujji, rest teesuko properly! 🥰"),
    (122, "sweet", 3, "Night night bujji, tight ga paduko! 😊"),
    (122, "sweet", 4, "Kalalu well kanali bangaram, good night! 🥰"),
    (122, "funny", 3, "Insomniac lifestyle proud, next level bujji! 😂"),
    (124, "sweet", 4, "Sweet dreams bangaram, rest teesuko! 🥰"),
    (124, "funny", 2, "Okay mom padukunta, happy aa ippudu? 😂"),
    (125, "romantic", 3, "Kalisi healthy avdaam bujji, take care! 💕"),
    (129, "sweet", 3, "Nice dedication bangaram, proud ga undhi! 😊"),
    (133, "sweet", 1, "Baagundhi bujji continue cheyyi, ne pace lo! 😊"),
    (133, "sweet", 2, "Cute reel baby, post cheyyi please! 😊"),
    (135, "funny", 3, "Ambulance book cheddama, adi chala chesav! 🤣"),
    (137, "sweet", 2, "Thanks bangaram, nee words chala sweet ga unnai! 😊"),
    (138, "sweet", 2, "Blush avthunna baby, stop cheyyi please! 😊"),
    (138, "sweet", 3, "Sweet words bangaram, continue cheyyi! 😊"),
    (138, "sweet", 4, "Thanks bujji, nee words chala sweet! 😊"),
    (138, "funny", 4, "Filter magic technology use chesav aa bujji? 😂"),
    (140, "sweet", 3, "Thanks baby nee words tho khushi! 😊"),
    (140, "sweet", 4, "Blush avthunna bangaram, sweet ga cheppav! 😊"),
    (140, "bold", 3, "Sapiosexual approved bujji, nee mind attractive! 😏"),
    (144, "sweet", 4, "Yay happiest moment bujji, celebrate cheddaam! 🥰"),
    (145, "bold", 2, "Indoor activities plan chestha nee tho bujji! 😏"),
    (150, "sweet", 0, "Okay bangaram noted, chesthunna! 🥰"),
    (150, "sweet", 3, "Okay noted bangaram, follow chestha! 😊"),
    (150, "sweet", 4, "Sure bujji, chestha pakka! 😊"),
    (151, "sweet", 2, "Alright baby, chestha ippude! 😊"),
    (151, "sweet", 3, "Okay noted bangaram, remember chestha! 😊"),
    (151, "sweet", 4, "Fine bujji, okay chestha! 😊"),
    (151, "funny", 1, "Rejection specialist expert aipoyav, skill upgrade! 🤣"),
    (151, "bold", 1, "Challenge accepted baby, prove chestha! 😏"),
    (152, "romantic", 3, "Okay bujji khushi ga unna nee tho! 🥰"),
    (152, "romantic", 4, "Sare prema accept chesanu, always here! ❤️"),
    (152, "sweet", 0, "Okay bangaram done, chestha ippude! 🥰"),
    (152, "sweet", 1, "Done bujji, happy aa ippudu? 😊"),
    (152, "sweet", 2, "Alright baby, fixed chestha! 😊"),
    (152, "sweet", 3, "Sare bujji cool ga undhi ippudu! 😊"),
    (152, "sweet", 4, "Cool bangaram, sorted! 😊"),
    (153, "romantic", 4, "Ok prema accept chesanu bangaram, always! ❤️"),
    (153, "sweet", 0, "Okay bangaram cool ga undhi! 🥰"),
    (153, "sweet", 1, "Cool bujji, chestha pakka! 😊"),
    (153, "sweet", 2, "Noted baby, remember chestha! 😊"),
    (153, "sweet", 3, "Alright bangaram, done! 😊"),
    (153, "sweet", 4, "Done bujji, happy aa? 😊"),
    (154, "sweet", 2, "Cute laugh baby, nee navvu chala sweet! 😊"),
    (155, "sweet", 3, "Hehe cute bujji, nuvvu chala fun! 🥰"),
    (156, "sweet", 4, "Same feeling bujji, nenu kuda! 🥰"),
    (157, "sweet", 4, "Soon bangaram excited ga unna! 🥰"),
    (158, "sweet", 4, "Special gift bujji plan chestha! 🥰"),
    (159, "sweet", 4, "Good idea bujji, chesthe baguntundhi! 😊"),
    (164, "romantic", 3, "Perfect pair manamu bujji, always! 💕"),
    (164, "sweet", 0, "True bangaram agreed, same feel! 🥰"),
    (164, "sweet", 3, "Agreed baby same feeling naku! 😊"),
    (164, "sweet", 4, "Kalisi good always bangaram pakka! 🥰"),
    (166, "sweet", 2, "Navvu healthy baby, keep smiling! 😊"),
    (169, "romantic", 4, "Gundey melting ippudu bujji, sweet ga cheppav! 💕"),
    (169, "sweet", 3, "Thanks baby khushi aipoya nee words tho! 😊"),
    (170, "sweet", 2, "Thanks baby nee words sweet ga unnai! 😊"),
    (170, "funny", 4, "Skeleton goals achieve chesth unnav bujji! 😂"),
    (174, "sweet", 2, "Nothing special baby, nuvve special! 😊"),
    (174, "funny", 3, "Yesterday's clothes same bujji, comfort zone! 😂"),
    (176, "sweet", 4, "Matching couple goals bujji, cute! 🥰"),
    (177, "sweet", 3, "Santosham together goal bujji always! 😊"),
    (181, "sweet", 1, "Ayyoo sorry bangaram, bhayapadda! 😊"),
    (181, "sweet", 4, "My bad bangaram, inka chesanu! 😊"),
    (182, "sweet", 4, "Party hard bangaram tho enjoy cheyyi! 🥰"),
    (183, "sweet", 4, "Sweet bangaram chala chala! 🥰"),
    (185, "sweet", 1, "Avvaku bujji nammu, nijam ga chestha! 😊"),
    (187, "sweet", 4, "Nothing exciting bangaram, nuvvu vasthe exciting! 🥰"),
    (188, "sweet", 3, "Night bujji tight ga paduko! 😊"),
    (191, "bold", 1, "Actions chupiddama baby, ready aa? 😏"),
    (192, "sweet", 1, "Sweet dreams bujji, rest teesuko! 🥰"),
    (192, "sweet", 4, "Good night bujji, tight ga paduko! 😊"),
    (194, "sweet", 4, "Excited planning bujji chestha twaraga! 🥰"),
    (196, "sweet", 3, "Same same bangaram, same feeling! 😊"),
    (196, "sweet", 4, "Blush avthunna bujji, stop cheyyi! 😊"),
    (197, "sweet", 1, "Nuvvu cuter bujji, nenu agree! 😊"),
    (197, "sweet", 2, "Thanks baby khushi nee words tho! 😊"),
]


def main():
    with open(DATASET_PATH, encoding='utf-8-sig') as f:
        data = json.load(f)

    str_changes = 0
    idx_changes = 0
    full_rewrites = 0

    # Part 1: full entry rewrites
    for entry in data:
        key = entry.get('incoming', '')
        # Also try stripped version
        key_stripped = key.strip()
        rewrite = FULL_REWRITES.get(key) or FULL_REWRITES.get(key_stripped)
        if rewrite:
            for tone in ['romantic', 'sweet', 'funny', 'bold']:
                if tone in rewrite:
                    entry[tone] = rewrite[tone]
                    full_rewrites += 1

    # Part 2: string fixes
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

    # Part 3: index-based fixes
    for (ei, tone, ri, new_reply) in INDEX_FIXES:
        if ei < len(data):
            replies = data[ei].get(tone, [])
            if ri < len(replies):
                old = replies[ri]
                replies[ri] = new_reply
                if old != new_reply:
                    idx_changes += 1

    with open(DATASET_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Part 1 (full entry rewrites): {full_rewrites} tone sets")
    print(f"Part 2 (string fixes):        {str_changes} changes")
    print(f"Part 3 (index fixes):          {idx_changes} changes")
    print("Saved.")


if __name__ == '__main__':
    main()
