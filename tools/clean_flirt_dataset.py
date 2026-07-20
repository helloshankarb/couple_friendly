#!/usr/bin/env python3
import json
import re
import os

DATASET_PATH = 'app/src/main/assets/flirt_dataset.json'

REPLACEMENTS = {
    # Matching tattoo category
    "Enni janmaalaina mark us permanent bujji! ❤️": "Enni janmaalaina ne peru naa meeda permanent bujji! ❤️",
    "kalalu tattoo kalisi andamga baby! 😘": "Iddaram kalisi matching tattoo select cheddam baby! 😘",
    "Permanent bond symbol bangaram! 🥰": "Mana love ki permanent symbol bangaram! 🥰",
    "kalisi enni janmaalaina literal meaning! 💕": "Enni janmaalaina nuvve natho undali bangaram! 💕",
    "Love mark permanent bujji! 😍": "Mana love epattiki permanent bujji! 😍",
    "Cute idea discuss design bujji! 🥰": "Super idea, matching design chuddam bujji! 🥰",
    "What design aalochisthunna bangaram? 😊": "Em tattoo veyinchukundamo cheppu bangaram! 😊",
    "Interesting concept baby research! 💕": "Chala manchi concept baby, tattoo design select cheddam! 💕",
    "Discuss design kalisi! 😘": "Iddaram kalisi design select cheddam! 😘",
    
    # Nee smile chuste happy category
    "Ne kosam everyday navvu chestha bujji! ❤️": "Ne kosam eppudu navvuthune unta bujji! ❤️",
    "Ne santosham naa mission daily baby! 😘": "Ninnu eppudu navvinchadame naa pani baby! 😘",
    "navvu permanent ne ki bangaram! 🥰": "Mana chemistry permanent bangaram! 🥰",
    "Ne khushi face naa reward! 💕": "Nee andamaina navvu chusthe chalu bangaram! 💕",
    "Born to make you navvu bujji! 😍": "Ninnu navvinchadanike puttane bujji! 😍",
    "Ne navvu better bujji! 😊": "Nee navvu chala andamga untundi bujji! 😊",
    "Mutual santosham baby! 💕": "Iddaram happy ga undham baby! 💕",
    "Ne valla navvu vasthundhi bangaram kuda! 😘": "Nee msg chusi nenu kuda navvuthunna bangaram! 😘",
    "khushi that you're happy bujji! 🥰": "Nuvvu happy ga unte nenu happy bujji! 🥰",
    "navvu muscles workout daily bujji! 😂": "Navvi navvi muscles workout aipothundi bujji! 😂",
    "daggara vasthe bigger navvu bujji! 😏": "Daggara vasthe inka bigger navvu chusthav bujji! 😏",
    "kiss worthy navvu confirmed baby! 😉": "Nee navvu chala kiss worthy ga untundi baby! 😉",
    "navvu seductive mode activate! 🔥": "Navvithe inka seductive ga untav baby! 🔥",
    "Ne lips focus naa not navvu! 😏": "Nee lips paine naa focus antha baby! 😏",
    "navvu plus wink combo try bujji! 😘": "Nee navvu and wink combo super untundi bujji! 😘",

    # Dinner/Lunch category non-natives
    "Remind chesav thanks bangaram! 🥰": "Gurtuchesav thanks bangaram! 🥰",
    "Lunch reminder service modalu chesav aa? 😂": "Lunch reminder duty start chesav aa? 😂",
    "Lunch with you sounds better plan! 😉": "Nee tho lunch chesthe chala baguntundi baby! 😉",
    "Thinna kaani company ledu boring aindhi! 💕": "Thinna kaani nuvvu pakkanunte inka bagundedi! 💕",
    
    # Tension / Sad categories
    "Mood change chestha raa direct! 😏": "Nee mood set chestha raa direct! 😏",
    "Delete cheyyi tension space kavali! 😜": "Tension clear cheyyi space kavali! 😜",
    "Delete cheyyi cache brain lo bujji! 😜": "Clear cheyyi cache brain lo bujji! 😜",
    "Tension delete cheyyi instant relief! 😜": "Tension clear cheyyi instant relief! 😜",
    "Convince chestha challenge accept! 😉": "Sarele oppistha chudu, challenge accept! 😉",
    "Dedicate chestha ne kosam special! 😘": "Song neeku dedicate chestha special ga! 😘",
    "Format cheyyi brain restart! 🤭": "Brain clear cheyyi stress free restart! 🤭",
    "Install cheyyi santosham app phone lo! 😜": "Santosham app download chesko phone lo! 😜",
    "Celebrate cheddama reason cheppu? 🤭": "Party cheskundama reason cheppu? 🤭",
    "Celebrate cheddama special ga bujji! 😘": "Party cheskundama special ga bujji! 😘",

    # Additional highly robotic patterns found in quality checks
    "Sorry never intentional bujji! 😊": "Sorry intentional ga cheyyaledu bujji! 😊",
    "Nuvvu important never pattinchukokunda untanu! 🥰": "Nuvve important bangaram, eppatiki pattinchukokunda undanu! 🥰",
    "Pattinchukoledu kaadu multitasking fail aindhi! 😂": "Multitasking fail aindhi anthe bangaram! 😂",
    "I choosukuntha about you so much baby! 😘": "Nee meeda chala care undi baby! 😘",
    "PPT ready kavala presentation style? 🤭": "PPT presentation range lo details kavala? 🤭",
    "Feelings deep ocean laga endlessly! 😏": "Nee paina feelings deep ocean kante ekkuva baby! 😏",
    "Love undhi ante bank balance laga interest rate entha? 😂": "Interest rate monthy aa yearly aa? 😂",
    "Sudden stock market rise aindhi aa? 😜": "Sudden ga interest perigindi enti stock market la? 😜",
    "Late ga invest chesav better late than never! 😂": "Late ga cheppav kani super bangaram! 😂",
    "jeevitham share cheddama officially permanent ga? 😘": "Naa jeevitham neethone share chesukunta eppatiki! 😘",
    "Proposal without biryani invalid court! 🤣": "Proposal with biryani set cheddam chudu! 🤣",
}

def clean_dataset():
    if not os.path.exists(DATASET_PATH):
        print(f"Error: Dataset not found at {DATASET_PATH}")
        return

    with open(DATASET_PATH, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    print(f"Loaded {len(data)} entries from flirt_dataset.json")

    sentence_fixes = 0
    pattern_fixes = 0

    for entry in data:
        for tone in ['romantic', 'sweet', 'funny', 'bold']:
            if tone not in entry:
                continue
            for i, sentence in enumerate(entry[tone]):
                # 1. Direct replacements
                clean_sent = sentence.strip()
                if clean_sent in REPLACEMENTS:
                    entry[tone][i] = REPLACEMENTS[clean_sent]
                    sentence_fixes += 1
                else:
                    # Try fuzzy matching without emoji
                    clean_no_emoji = re.sub(r'\s*[\U0001F600-\U0001FAFF\u2764\u2728\uFE0F]+\s*$', '', clean_sent).strip()
                    for old_phrase, new_phrase in REPLACEMENTS.items():
                        old_no_emoji = re.sub(r'\s*[\U0001F600-\U0001FAFF\u2764\u2728\uFE0F]+\s*$', '', old_phrase).strip()
                        if clean_no_emoji == old_no_emoji:
                            # Preserve original emoji if new doesn't have one
                            emoji_match = re.search(r'[\U0001F600-\U0001FAFF\u2764\u2728\uFE0F]+\s*$', clean_sent)
                            suffix = ' ' + emoji_match.group().strip() if emoji_match else ''
                            entry[tone][i] = re.sub(r'\s*[\U0001F600-\U0001FAFF\u2764\u2728\uFE0F]+\s*$', '', new_phrase).strip() + suffix
                            sentence_fixes += 1
                            break

                # 2. General cleanup of weird english leftover words
                original_text = entry[tone][i]
                
                # Replace literal meaning -> andamga
                entry[tone][i] = entry[tone][i].replace("literal meaning", "nijamga")
                entry[tone][i] = entry[tone][i].replace("concept baby research", "concept design select")
                entry[tone][i] = entry[tone][i].replace("discuss design", "design chuddam")
                entry[tone][i] = entry[tone][i].replace("mark us permanent", "permanent ga undipothundi")
                
                if entry[tone][i] != original_text:
                    pattern_fixes += 1

    print(f"Dataset cleaning finished:")
    print(f"  Sentence-level replacements: {sentence_fixes}")
    print(f"  Word/pattern replacements:   {pattern_fixes}")

    with open(DATASET_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved cleaned dataset back to {DATASET_PATH}")

if __name__ == '__main__':
    clean_dataset()
