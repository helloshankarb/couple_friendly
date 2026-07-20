"""
Comprehensive dataset rewrite:
1. Fix specific bad lines in entries 0-201
2. Full rewrite of entries 202-222 (corporate/AI jargon)
"""
import json, sys, copy
sys.stdout.reconfigure(encoding='utf-8')

JSON_PATH = "app/src/main/assets/flirt_dataset.json"

with open(JSON_PATH, encoding='utf-8') as f:
    data = json.load(f)

# ── helper ─────────────────────────────────────────────────────────────────
def fix_entry_by_incoming(incoming_text, tone, index, new_line):
    for entry in data:
        if entry["incoming"] == incoming_text:
            entry[tone][index] = new_line
            return True
    print(f"  WARN: entry not found for incoming='{incoming_text}'")
    return False

def replace_all_tones(incoming_text, romantic, sweet, funny, bold):
    for entry in data:
        if entry["incoming"] == incoming_text:
            entry["romantic"] = romantic
            entry["sweet"]    = sweet
            entry["funny"]    = funny
            entry["bold"]     = bold
            return True
    print(f"  WARN: entry not found for incoming='{incoming_text}'")
    return False

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: Spot fixes in entries 0-201
# ═══════════════════════════════════════════════════════════════════════════

fixes = []

# Entry 3 (Nenu busy) funny[1] - too long/cringe
fixes.append(("Nenu busy", "funny", 1, "prapancham pause chesanu ne kosam only! 😂"))

# Entry 8 (Nenu manchi ga unnanu) bad lines
fixes.append(("Nenu manchi ga unnanu", "romantic", 0, "Nuvvu unnav anduke manchi ga feel avthunna bujji! ❤️"))
fixes.append(("Nenu manchi ga unnanu", "romantic", 3, "Ne kosam naa gunde endho full ga undhi bangaram! 💕"))
fixes.append(("Nenu manchi ga unnanu", "bold", 3, "Ne presence tho energy level max avthundhi bangaram! 😏"))

# Entry 27 funny[1] - duplicate of [0]
fixes.append(("Nee meeda love undhi", "funny", 1, "EMI kaadu direct ga nee tho undadam kavali naaku! 😂"))

# Entry 29 sweet[3] - too short/broken
fixes.append(("Propose chesav anuko", "sweet", 3, "Eyes wet aipoyai santosham aapaledhu bujji! 🥺"))

# Entry 42 romantic[0] - broken syntax
fixes.append(("Cute ga unnav", "romantic", 0, "Nuvvu cute ga undhi anduke nenu confused bujji! ❤️"))

# Entry 53 sweet[0] - broken
fixes.append(("Dreams em vasthunnayo", "sweet", 0, "Nice ones vasthunnai nuvvu unnav anduke baby! 😊"))

# Entry 63 romantic[1] - pure English
fixes.append(("Exam undhi", "romantic", 1, "Nuvvu chesthav pakka naa confidence undhi bujji! 💕"))

# Entry 63 sweet[3] - duplicate of sweet[0]
fixes.append(("Exam undhi", "sweet", 3, "Tension padaku nuvvu chesthav pakka baby! 🌸"))

# Entry 64 romantic[0] - broken
fixes.append(("Office lo busy", "romantic", 0, "Nee kosam wait chesthunna twaraga free avvuu bujji! ❤️"))

# Entry 75 romantic[1] - pure English song name
fixes.append(("Song recommend cheyyi", "romantic", 1, "Nee peru pettukoni oka song vintaanu daily bangaram! 💕"))

# Entry 76 sweet[0] - duplicate of sweet[1]
fixes.append(("Stress lo unna", "sweet", 0, "Em aindhi cheppu bangaram nenu vintha! 🌸"))

# Entry 81 romantic[0] - pure English "Don't"
fixes.append(("Nenu overthink chesthunna", "romantic", 0, "Overthink cheyaku bangaram nenu unna ne kosam! ❤️"))

# Entry 90 romantic[1] - odd
fixes.append(("Today baaga cheyyi", "romantic", 1, "Ne wish tho already won feel avthundhi bujji! 💕"))

# Entry 90 romantic[4] - pure English
fixes.append(("Today baaga cheyyi", "romantic", 4, "Ne love tho anything possible bujji! 💗"))

# Entry 100 romantic[3] - broken
fixes.append(("Nee photos pampu", "romantic", 3, "Ne beauty chuste naa phone screen dull avthundhi bangaram! 🥰"))

# Entry 101 romantic[0] - broken
fixes.append(("Selfie pampu", "romantic", 0, "Ne photo wallpaper lo pettukuntunna bujji naa phone lo! ❤️"))

# Entry 102 romantic[2] - duplicate of romantic[3]
fixes.append(("Eppudu kanabadthav", "romantic", 2, "Ne leni roju incomplete ga anipistundhi bangaram! 💕"))

# Entry 102 romantic[3] - too similar to [2]
fixes.append(("Eppudu kanabadthav", "romantic", 3, "Nee gurinchi aalochisthunna prathi kshanam bujji! 💗"))

# Entry 120 romantic[0] - broken
fixes.append(("Nuvvu busy lo forget", "romantic", 0, "Nuvvu marchipovadaniki impossible bangaram eppudu! ❤️"))

# Entry 120 romantic[1] - mixed English
fixes.append(("Nuvvu busy lo forget", "romantic", 1, "Busy lo undina nee gurthu vastundi naa ki always bujji! 💕"))

# Entry 128 romantic[2] - broken
fixes.append(("Cook chesanu nee kosam", "romantic", 2, "Nee kosam special ga chesav ante naa ki santosham baby! 🥰"))

# Entry 128 romantic[4] - cringe
fixes.append(("Cook chesanu nee kosam", "romantic", 4, "Nee cheyyi tho thinte extra tasty avthundhi bangaram! 💕"))

# Entry 134 funny[1] - wrong context for headache
fixes.append(("Headache ga undhi", "funny", 1, "Tension ekkuva chesav aa work lo bujji! 😂"))

# Entry 139 romantic[3] - weird
fixes.append(("Nee perfume baagundhi", "romantic", 3, "Nee scent gurinchi alochisthunna alaage bangaram! 🥰"))

# Entry 196 funny[3] - cringe
fixes.append(("Nee smile chuste happy", "funny", 3, "Ne navvu chuste naa concentration poindi bujji! 😂"))

# Entry 196 funny[4] - cringe
fixes.append(("Nee smile chuste happy", "funny", 4, "Ne navvu viral avvaali social media lo bangaram! 😅"))

# Entry 196 bold[2] - robotic "seductive mode activate"
fixes.append(("Nee smile chuste happy", "bold", 2, "Nee navvu chuste kiss chesadam anupisthundhi bujji! 😏"))

# Entry 199 romantic[0] duplicate of [2]
fixes.append(("Nuvvu nacchav naaku", "romantic", 0, "Nuvvu nacchav kaadu nenu crazy aipoyanu bujji! ❤️"))

# Entry 201 bad lines
fixes.append(("Good morning bujji!", "romantic", 1, "Prathi roju nee tho start cheste rozu vishesham bujji! 💕"))
fixes.append(("Good morning bujji!", "romantic", 2, "Nee tho naa prapancham modalaipothundhi bangaram! 🥰"))
fixes.append(("Good morning bujji!", "sweet", 0, "Good morning bangaram! Ee roju baagundali nee ki! 🌸"))
fixes.append(("Good morning bujji!", "sweet", 1, "Aww morning msg chesav thanks baby so sweet! 😊"))
fixes.append(("Good morning bujji!", "sweet", 3, "Nuvvu meluchukote naa morning bright avthundhi bujji! 🌼"))
fixes.append(("Good morning bujji!", "funny", 1, "Morning alarm ni ignore chesav nidra queen bujji! 😂"))
fixes.append(("Good morning bujji!", "bold", 0, "Morning miss avthunna raa daggara ki ippude bujji! 😏"))
fixes.append(("Good morning bujji!", "bold", 2, "Nee hug tho day start chesthe perfect avthundhi bujji! 😈"))

print("Applying spot fixes...")
for incoming, tone, idx, new_line in fixes:
    ok = fix_entry_by_incoming(incoming, tone, idx, new_line)
    if ok:
        print(f"  Fixed [{tone}][{idx}] in '{incoming}'")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: Full rewrites for entries 202-222
# ═══════════════════════════════════════════════════════════════════════════

rewrites = {}

# Entry 202: "Na gurinchi emi alochistunnav?" (flirt)
rewrites["Na gurinchi emi alochistunnav?"] = {
    "romantic": [
        "Nuvve naa aalochanalu poorthi bangaram! ❤️",
        "Naa mind lo nuvvu rent free unnavbu bujji! 💭",
        "Nee smile gurinchi mostly aalochisthunna baby! 🥰",
        "Honest ga nuvve naa first thought bujji! 💕",
        "Nee tho undadam gurinchi aalochisthunna bangaram! 💗",
    ],
    "sweet": [
        "Nuvvu em chesthunnavo ane thoughts lo unna bujji! 😊",
        "Nuvvu happy ga undavali ani aalochisthunna bangaram! 🌸",
        "Random ga nuvve gurthu vastav baby! 💛",
        "Nee roju baagundaali anipistundi bujji! 🌼",
        "Nee gurinchi aalochinche toh navvosthundhi bangaram! ✨",
    ],
    "funny": [
        "Nee meeda full documentary naa mind lo shoot aipothundhi! 😂",
        "Nee gurinchi aalochinche toh work padipoyindi bujji! 😅",
        "24/7 nee gurinche alochisthunna bills pay cheyyadam marachipoya! 😜",
        "Naa brain nee meeda crush lodged chesindi bujji! 🤣",
        "Nee photo chusi naa concentration full ga poyindi bangaram! 😂",
    ],
    "bold": [
        "Nee daggara velladam gurinchi plans chestunaanu bujji! 😏",
        "Raa direct ga cheptha naa thoughts bangaram! 🔥",
        "Nee tho undadam gurinchi aalochisthunna mostly baby! 😈",
        "Nuvvu miss avthunna thats my only thought bujji! 😏",
        "Nee thoughts chuddam raa daggara vaste vinipista bangaram! 😉",
    ],
}

# Entry 203: "Nee ex gurinchi cheppavu kadha" (jealousy)
rewrites["Nee ex gurinchi cheppavu kadha"] = {
    "romantic": [
        "Past chaalu present nuvve naa prapancham bangaram! ❤️",
        "Old chapter closed nuvve naa new story bujji! 💕",
        "Naa gunde lo nee kosam only space undhi baby! 🥰",
        "Past boring nuvve naa beautiful reality bangaram! 💗",
        "Nuvve naa modhati last thought enni janmaalaina bujji! 💭",
    ],
    "sweet": [
        "Nuvve naa priority bangaram tension padaku! 😊",
        "Past is gone nuvvu naa present future bujji! 🌸",
        "Naa true feelings completely nee tho only baby! 💛",
        "Nuvve naa life lo most important person bujji! 🌼",
        "Nee meeda unna care eppatiki taggatledu bangaram! ✨",
    ],
    "funny": [
        "Ex ante naa dictionary lo aa word delete aipoyindhi! 😂",
        "Season 1 cancel nuvvu season 2 premium bujji! 😅",
        "Old phone nuvvu latest model bangaram! 😜",
        "Past chapter marichipoya RAM cleared nee kosam space full! 🤣",
        "Ex aa who naa memory la waste cheyyadam enduku! 😂",
    ],
    "bold": [
        "Nee jealousy cute ga undhi bujji admit chesuko! 😏",
        "Naa choice clear nuvve premium option bangaram! 🔥",
        "Nee ki competition evaru leru nuvvu winner bujji! 😈",
        "Naa focus poorthiga nee meede baby chupista! 😏",
        "Naa loyalty prove chestha raa daggara ki bujji! 😉",
    ],
}

# Entry 204: "Nuvvu chala handsome unnav bujji" (compliment)
rewrites["Nuvvu chala handsome unnav bujji"] = {
    "romantic": [
        "Nuvvu chepthe aakasam lo thiruguttunattu undhi bujji! ❤️",
        "Nee words tho naa roju bright avthundhi bangaram! 💕",
        "Nee compliment tho naa confidence max level baby! 🥰",
        "Nee chinnari words naa morning boost bujji! 💗",
        "Nee tho undatam naa style automatic upgrade baby! 💭",
    ],
    "sweet": [
        "Aww chala sweet ga cheppav bujji! 😊",
        "Thanks bangaram nee compliment chala precious! 🌸",
        "Nee sweet words tho naa mood full positive avthundhi baby! 💛",
        "Nuvve naa favorite fan bujji! 🌼",
        "Nee approval tho nenu confident feel avthunna bangaram! ✨",
    ],
    "funny": [
        "Mirror confirm chesedaaka wait cheyyanuu nee words ultimate truth! 😂",
        "Hollywood direct ga miss chesindhi naa ni bujji! 😅",
        "Compliment fee entha paytm chesava bangaram? 😜",
        "Chivariki gamaninchav enni days aindhi bujji! 🤣",
        "Nee opinion certified ISO approved bangaram! 😂",
    ],
    "bold": [
        "Ee compliment ki reward ga kiss plan cheddama bujji? 😏",
        "In person lo inka hot ga kanipistha bangaram! 🔥",
        "Nee smile naa handsome look ki perfect rating bujji! 😈",
        "Nee beautiful approval tho inka confident avthunna baby! 😏",
        "Daggara vaste inka handsome feel avthundhi bujji! 😉",
    ],
}

# Entry 205: "Nak nee tho matladali ani undhi" (care)
rewrites["Nak nee tho matladali ani undhi"] = {
    "romantic": [
        "Nee muchatlu vinalani nenu wait chesthunna bujji! ❤️",
        "Cheppu bangaram nee voice vinte naa mind clear avthundhi! 💕",
        "Nee text naa priority always baby! 🥰",
        "Cheppu bujji nee venuka nenu unna always! 💗",
        "Naa quality time poorthiga nee tho share chesukunta bangaram! 💭",
    ],
    "sweet": [
        "Aww cheppu bujji vintunna ikkade unna! 😊",
        "Nee sharing ki nenu support ga untaanu baby! 🌸",
        "Matladudaam bujji bore aipoyavi kadaa! 💛",
        "Nee muchatlu vintunte day chala baaguntundhi bangaram! 🌼",
        "Cheppu ready vintunna completely bujji! ✨",
    ],
    "funny": [
        "Customer care line connected cheppu bujji! 😂",
        "Nee complaints handle cheyyadaniki specialized desk open bangaram! 😅",
        "Direct call chesthe immediate ga answer chestha bujji! 😜",
        "Listening mode on input cheyyi bangaram! 🤣",
        "Nee topics nenu entertain chestha promise bujji! 😂",
    ],
    "bold": [
        "Matladadam kaadu kaluda ippude raa bujji! 😏",
        "Nee secrets naa gunde lo locked bangaram! 🔥",
        "Full attention nee meede ippudu bujji! 😈",
        "Cheppu nee problem nenu solve chestha baby! 😏",
        "Matladukundham kaadu meet avudaam raa bujji! 😉",
    ],
}

# Entry 206: "Nuvvu na ki chala important" (care)
rewrites["Nuvvu na ki chala important"] = {
    "romantic": [
        "Nuvvu naa pranam bujji important matrame kaadu! ❤️",
        "Naa gunde lo nee kosam special space permanent bangaram! 💕",
        "Naa absolute priority prapancham lo nuvve bujji! 🥰",
        "Nee tho unte automatic happiness vastu undhi baby! 💗",
        "Naa complete life center point nuvve bangaram! 💭",
    ],
    "sweet": [
        "Nuvvu naa prapancham lo chala precious bujji never forget! 😊",
        "Naa everyday nee tho better avthundhi bangaram! 🌸",
        "Naa daily happiness reason nuvve bujji! 💛",
        "Nuvvu chala unique and special baby always remember! 🌼",
        "Naa top priority always nuvve bangaram! ✨",
    ],
    "funny": [
        "Important chala chinna word nuvvu legendary bujji! 😂",
        "Naa life Excel sheet lo row 1 column 1 nuvve bangaram! 😅",
        "Naa system reboot ki nuvvu dynamic reason bujji! 😜",
        "Important kaadu legendary range relationship idi bangaram! 🤣",
        "Naa priority list CEO level nuvve bujji! 😂",
    ],
    "bold": [
        "Important space daggara vasthe verify avuthundhi bujji! 😏",
        "Important ani direct deeds lo chupista bangaram! 🔥",
        "Nuvve naa sweet weakness verify chestha bujji! 😈",
        "Nee value naa protection lo always baby! 😏",
        "Nuvve naa VIP priority raa daggara ki bujji! 😉",
    ],
}

# Entry 207: "Evaraina nee ki pelli chestha antunnaru" (proposal)
rewrites["Evaraina nee ki pelli chestha antunnaru"] = {
    "romantic": [
        "Pelli ante nee tho kalisi jeevitham spend cheyyadam bangaram! ❤️",
        "Naa answer always yes nee kosam only bujji! 💕",
        "Pelli ante complete ga nee tho ready nenu baby! 🥰",
        "Naa oka choice nuvve eppudu bangaram! 💗",
        "Evaraina chestha antunnaru kaani nuvve naa answer bujji! 💭",
    ],
    "sweet": [
        "Aww pelli planning sweet idea bujji kalisi decide! 😊",
        "Naa yes always ready nee ki bangaram! 🌸",
        "Nee tho pelli planning chala beautiful baby! 💛",
        "Kalisi illu kattedham bangaram! 🌼",
        "Pelli thoughts sweet dreams aipoyai bujji! ✨",
    ],
    "funny": [
        "Biodata ready review panel ki submit cheddama bujji! 😂",
        "First round screening clear chesava bangaram? 😅",
        "Shaadi.com accounts delete chestha ippude bujji! 😜",
        "Pelli market evaluation closed premium match locked bangaram! 🤣",
        "Hall booking biryani menu fix cheyyi first bujji! 😂",
    ],
    "bold": [
        "Pelli plans chuddam raa daggara ki bujji! 😏",
        "Naa yes direct actions lo secure chestha bangaram! 🔥",
        "Marriage ante nee tho single elite category bujji! 😈",
        "Naa future plans lo nuvve priority always baby! 😏",
        "Direct date pelli registration fix cheddama raa bujji! 😉",
    ],
}

# Entry 208: "Nuvvu na tho matladatam ledhu endhuku" (fight)
rewrites["Nuvvu na tho matladatam ledhu endhuku"] = {
    "romantic": [
        "Sorry bangaram nee tho matladaalanee undhi nenu! ❤️",
        "Nee msgs miss chesanu nijam ga sorry bujji! 💕",
        "Nee voice lekunda roju boring ga undhi baby! 🥰",
        "Oka chance ivvu matladthaamu solve cheddaamu bangaram! 💗",
        "Sorry naa thappu please matlaadu bujji! 💭",
    ],
    "sweet": [
        "Sorry bujji busy lo miss aindhi really! 😊",
        "Nee chats miss avvadam chala bad baby! 🌸",
        "Ippudu start cheyyi matladthaamu bujji! 💛",
        "My mistake sorry nee ki bangaram! 🌼",
        "Sorry bujji ippudu unna ne kosam fully! ✨",
    ],
    "funny": [
        "Silent mode accidental ga on aipoyindhi bujji! 😂",
        "WiFi down manual reboot active bangaram! 😅",
        "System rebooting chats load avuthunnai bujji! 😜",
        "Reply button hide aipoyindhi bujji sorry! 🤣",
        "Buffering aipoya network slow bangaram! 😂",
    ],
    "bold": [
        "Explain chestha raa daggara ki bujji! 😏",
        "Silence end chestha nee tho direct ga bangaram! 🔥",
        "Matladadam miss chesanu prove chestha bujji! 😈",
        "Raa fix chestha ippude baby! 😏",
        "Nuvvu matladakapothe vastha direct bujji! 😉",
    ],
}

# Entry 209: "Ninnu miss avthunna" (missing)
rewrites["Ninnu miss avthunna"] = {
    "romantic": [
        "Nenu kuda ninnu chala miss avthunna bujji! ❤️",
        "Naa gunde thadapathaaduthundhi nee kosam bangaram! 💕",
        "Nuvvu lekunda ee room bore kottesthundhi baby! 🥰",
        "Ee dooram mana prema ni inka strong chesindhi bujji! 💗",
        "Roju motham nee aalochanalu lo unna bangaram! 💭",
    ],
    "sweet": [
        "Aww nenu kuda ninnu miss chesthunna bujji! 😊",
        "Nee miss text chudagane navvocchindi baby! 🌸",
        "Nuvvu gurthu vasthunnav prathi kshanam bangaram! 💛",
        "Twaraga kaladam fix cheddaamu bujji! 🌼",
        "Kalisi date plan cheddaamu soon bangaram! ✨",
    ],
    "funny": [
        "Miss meter limits cross aindhi certified bujji! 😂",
        "GPS tracking running nuvvu ekkadunnavoo bangaram! 😅",
        "Miss avuthunaanu ante daggara ra solution simple bujji! 😜",
        "Missing symptoms real gaa untunnai bangaram! 🤣",
        "Miss FM radio tune chesanu nee frequency lo bujji! 😂",
    ],
    "bold": [
        "Raa daggara ki miss fix chestha bujji! 😏",
        "Ninnu hug chesukuni prove chestha bangaram! 🔥",
        "Miss anukovadaaniki vastha ippude bujji! 😈",
        "Meeting chesthe miss feeling pothundhi fix baby! 😏",
        "Raa dynamic tension pothundhi daggara ki bujji! 😉",
    ],
}

# Entry 210: "Nak chala bore ga undhi" (random)
rewrites["Nak chala bore ga undhi"] = {
    "romantic": [
        "Nuvvunte bore poye prashne ledhu raa bujji! ❤️",
        "Nee bore nenu fix chestha vastha bujji! 💕",
        "Nee tho unte boring moment aney undi kaadu bangaram! 🥰",
        "Raa kalisi plan chestha em bore bujji! 💗",
        "Nuvvu naa daggara unte bore impossible bangaram! 💭",
    ],
    "sweet": [
        "Cheppu bujji matladthaamu bore fadhaipothundhi! 😊",
        "Sweet chat photos exchange start cheddaamu baby! 🌸",
        "Movie chuddam kalisi bore fix avuthundhi bangaram! 💛",
        "Online game aaddam bujji bore avvadhu! 🌼",
        "Video call cheddaamu face chudaali bangaram! ✨",
    ],
    "funny": [
        "Bore buster desk ready cheppu bujji! 😂",
        "Professional bore avvadam expert certified bangaram! 😅",
        "Bore Olympics gold medal nee ki already bujji! 😜",
        "Naa boring jokes ready deploying now bangaram! 🤣",
        "Same bore aa kalisi bore avvadam better bujji! 😂",
    ],
    "bold": [
        "Bore fix cheyyalante daggara raa bujji! 😏",
        "Interesting plan ready nuvvu vasthe bangaram! 🔥",
        "Bore impossible naa daggara guarantee bujji! 😈",
        "Raa intiki fix chestha tonight baby! 😏",
        "Night plan special wait avvu bujji! 😉",
    ],
}

# Entry 211: "Nuvvu nannu genuine ga premisthunnava?" (flirt)
rewrites["Nuvvu nannu genuine ga premisthunnava?"] = {
    "romantic": [
        "Naa prema actions lo daily chupisthunaanu bujji! ❤️",
        "Naa gunde poorthiga nee di bangaram doubt ledu! 💕",
        "Nuvve naa sweet destination zero doubts bujji! 🥰",
        "Genuine ga premisthunaanu prove chestha actions lo baby! 💗",
        "Naa love meeda doubt enduku bujji trust cheyyi! 💭",
    ],
    "sweet": [
        "Bujji naa affection pure nee kosam only! 😊",
        "Naa daily care lo chudachu genuine ani bangaram! 🌸",
        "Trust chesuko nenu eppatiki nee side lo unna baby! 💛",
        "Genuine feel avuthundhi nee ki cheppu bujji! 🌼",
        "Naa love verify chesuko daily care lo bangaram! ✨",
    ],
    "funny": [
        "Love meter 100 percent capacity pass bujji! 😂",
        "Genuine certificate CA certified ISO approved bangaram! 😅",
        "Love audit poorthi passed bujji zero issues! 😜",
        "TrueID verified highly genuine bangaram! 🤣",
        "Naa love fake aa real aa test chesuko bujji! 😂",
    ],
    "bold": [
        "Genuine ante direct meet lo prove chestha bujji! 😏",
        "Actions lo chupista raa daggara ki bangaram! 🔥",
        "Naa loyalty exclusive nee tho only bujji! 😈",
        "Genuine feel cheyali aithe raa daggara ki baby! 😏",
        "Romantic bold actions lo prove chestha bujji! 😉",
    ],
}

# Entry 212: "Nenu e roju chala tired ga unna" (care)
rewrites["Nenu e roju chala tired ga unna"] = {
    "romantic": [
        "Rest theesko bujji nee health naa responsibility! ❤️",
        "Nee sweet exhaustion chuste naa ki baadha bangaram! 💕",
        "Raa hug chestha tired feel pothundhi bujji! 🥰",
        "Nee comfort naa absolute priority always baby! 💗",
        "Rest theesko nenu daggare unna ne kosam bangaram! 💭",
    ],
    "sweet": [
        "Ayyoo rest theesko bujji please! 😊",
        "Recharge chesuko water thaagu baby! 🌸",
        "Nap theesko 20 min immediately bujji! 💛",
        "Overwork cheyaku rest theesko bangaram! 🌼",
        "Nee health first rest important bujji! ✨",
    ],
    "funny": [
        "Tired look kuda cute undhi bujji admit chesuko! 😂",
        "Sleep mode on tomorrow version 2.0 avuthav bangaram! 😅",
        "Welcome to adulting enjoy bujji! 😜",
        "Tired aipothe special comedy playlist start bangaram! 🤣",
        "Official relaxation certificate issued rest theesko bujji! 😂",
    ],
    "bold": [
        "Raa massage chestha relax avuthav bujji! 😏",
        "Tired details vanish avuthunai hug lo bangaram! 🔥",
        "Naa lap lo paduko rest theesko bujji! 😈",
        "Exhaustion fix chestha raa daggara ki baby! 😏",
        "Daggara cuddle chesthe instant energy boost bujji! 😉",
    ],
}

# Entry 213: "Relationship lo trust chala important kadaa" (random)
rewrites["Relationship lo trust chala important kadaa"] = {
    "romantic": [
        "Nuvve naa sweet safe zone bujji complete trust! ❤️",
        "Naa loyalty zero doubt bangaram always! 💕",
        "Mana trust strong undhi safety secure baby! 🥰",
        "Beautiful foundation mana relationship ki bangaram! 💗",
        "Mana bonding reliability standard absolute bujji! 💭",
    ],
    "sweet": [
        "Avunu trust most important bujji agree! 😊",
        "Nuvvu ichhe support naa strength bangaram! 🌸",
        "Truth and sweetness naa long term promise baby! 💛",
        "Trust tho relationship beautiful avuthundhi bujji! 🌼",
        "Completely secure feel avuthundhi nee tho bangaram! ✨",
    ],
    "funny": [
        "Trust bank account unlimited credit balance bujji! 😂",
        "Trust meter calibrated maximum limits bangaram! 😅",
        "Naa secrets nee ki visible full transparency bujji! 😜",
        "Trust certificate lifetime warranty valid bangaram! 🤣",
        "Reliable partner certified trust issues free bujji! 😂",
    ],
    "bold": [
        "Naa loyalty direct deeds lo chupista bujji! 😏",
        "Nee confidence naa ultimate asset bangaram! 🔥",
        "Trust verify chesuko actions lo bujji! 😈",
        "Loyalty exclusive nee tho only baby! 😏",
        "Strong trust strong us bujji fact! 😉",
    ],
}

# Entry 214: "Naku emaina gift isthava bujji?" (random)
rewrites["Naku emaina gift isthava bujji?"] = {
    "romantic": [
        "Naa full heart nee ki biggest gift bangaram! ❤️",
        "Nee side nenu undadam premium gift bujji! 💕",
        "Nee sweet smile naa everyday return gift baby! 🥰",
        "Naa time poorthiga nee tho gifted bangaram! 💗",
        "Naa heart permanently nee ki gifted bujji! 💭",
    ],
    "sweet": [
        "Aww sweet gift planning chestunaanu bujji! 😊",
        "Surprise dispatch ready baby eduru choosi! 🌸",
        "Special surprise active secret ga bangaram! 💛",
        "Nee kosam special ga plan chestunaanu bujji! 🌼",
        "Everyday care naa sweet gift nee ki bangaram! ✨",
    ],
    "funny": [
        "Gift cart checked discount code applied bujji! 😂",
        "Amazon wishlist link pampav aa direct bangaram! 😅",
        "Budget approve chesaka order dispatch bujji! 😜",
        "Presence is present word play bangaram! 🤣",
        "Birthday lo surprise ready pakka wait bujji! 😂",
    ],
    "bold": [
        "Nee side nenu hot ga undadam best gift bujji! 😏",
        "Surprise details reveal chestha meet lo bangaram! 🔥",
        "Special customized surprise ready bujji! 😈",
        "Nee blushing face naa favorite gift baby! 😏",
        "Direct shopping date plan chestha bujji! 😉",
    ],
}

# Entry 215: "Na photos inka like cheyyatam ledhenti kopama?" (jealousy)
rewrites["Na photos inka like cheyyatam ledhenti kopama?"] = {
    "romantic": [
        "Photos double chustha flat aipoya bujji sorry! ❤️",
        "Nee single picture naa heart beat rate raise chesindhi bangaram! 💕",
        "Nee beauty lo visual lost aipoyanu sorry baby! 🥰",
        "Double click screen direct love active bujji! 💗",
        "Incredible beautiful captures nuvvu bangaram! 💭",
    ],
    "sweet": [
        "Sorry bujji immediate ga notifications on chestha! 😊",
        "Nee feeds naa primary watch list baby! 🌸",
        "Daily like guarantee chestha bujji! 💛",
        "Lag aindi sorry next post first click naa di bangaram! 🌼",
        "Miss chesanu sorry bujji cute gaa unnaav! ✨",
    ],
    "funny": [
        "Like button server down sorry bujji! 😂",
        "Thumb muscular fatigue like process delayed bangaram! 😅",
        "App alerts muted manually checking bujji! 😜",
        "Memory full double tap sequence forgot bangaram! 🤣",
        "WiFi signal poor direct link crashed bujji! 😂",
    ],
    "bold": [
        "Instagram like kante call compliment direct premium bujji! 😏",
        "Nee pictures hot updates online bangaram! 🔥",
        "Heart emoji reactions online bujji! 😈",
        "Gorgeous captions deserve close praise bangaram! 😏",
        "Direct date invite better than like tap bujji! 😉",
    ],
}

# Entry 216: "Mana iddharame ekkadikaina trip veldhama bujji?" (random)
rewrites["Mana iddharame ekkadikaina trip veldhama bujji?"] = {
    "romantic": [
        "Nee cheyyi pattukunte direct heaven trip bujji! ❤️",
        "Nee tho ekkadikaina ready bangaram! 💕",
        "Date schedule lock chestha nuvvu cheppu baby! 🥰",
        "Venue choose cheyyi bujji nenu booking chestha! 💗",
        "Kalisi trips chala romantic avuthayi bangaram! 💭",
    ],
    "sweet": [
        "Aww destination planning sweet ga set cheyyi bujji! 😊",
        "Dates choose cheyyi completely ready baby! 🌸",
        "Nee tho ekkadikaina maximum happiness bangaram! 💛",
        "Any place nee tho beautiful feel avuthundhi bujji! 🌼",
        "Nee choices tho completely aligned bangaram! ✨",
    ],
    "funny": [
        "Financial audit confirm chesthe flights book bujji! 😂",
        "Passport expiry check first safety first bangaram! 😅",
        "Budget airline only afford bujji honest! 😜",
        "Travel broke return reality common bangaram! 🤣",
        "Google Maps expert certified trip ready bujji! 😂",
    ],
    "bold": [
        "Midnight drive or escape plan raa bujji! 😏",
        "Quiet private cabin trip cheddaamu bangaram! 🔥",
        "Surprise bold trip date dispatch bujji! 😈",
        "Just say the word checkout immediate baby! 😏",
        "Private road trip no destination just us bujji! 😉",
    ],
}

# Entry 217: "Nuvvu nannu intha perfect ga ela artham chesukuntav bujji?" (flirt)
rewrites["Nuvvu nannu intha perfect ga ela artham chesukuntav bujji?"] = {
    "romantic": [
        "Nee tho naa soul sync aipoyindhi bangaram! ❤️",
        "Nuvve naa perfect match zero modifications bujji! 💕",
        "Mana synchronization highly romantic baby! 🥰",
        "Nee comfort naa life logic bangaram! 💗",
        "Nuvve naa destination always bujji! 💭",
    ],
    "sweet": [
        "Nuvvu already perfect level bujji admit chesuko! 😊",
        "Naa best companion avvadam try chesthunna bangaram! 🌸",
        "Nee chat list unte everything positive feel baby! 💛",
        "Nee smile definition of perfect bujji! 🌼",
        "Nuvve naa right destination bangaram! ✨",
    ],
    "funny": [
        "Perfect rating 9.9 out of 10 lunch date free bujji! 😂",
        "Quality check pass perfect partner sticker ready bangaram! 😅",
        "Compliance standards cleared checklists pass bujji! 😜",
        "Official best girlfriend certification issued bangaram! 🤣",
        "Perfect score unlocks relationship warranty bujji! 😂",
    ],
    "bold": [
        "Perfect romance direct deeds lo prove chestha bujji! 😏",
        "Perfect matching choice locked nee tho bangaram! 🔥",
        "Synchronization closer meet tho solve avuthundhi bujji! 😈",
        "Exclusive loyalty highly authentic bold baby! 😏",
        "Private dates lo perfect moments wild bujji! 😉",
    ],
}

# Entry 218: "Nuvvu nannu chala special ga treat chesthunnav bujji" (romantic)
rewrites["Nuvvu nannu chala special ga treat chesthunnav bujji"] = {
    "romantic": [
        "Nuvvu naa prapancham lo royal VIP bujji! ❤️",
        "Naa pranam elite choice nuvve bangaram! 💕",
        "Special feel ivvadam naa duty nee ki baby! 🥰",
        "Nee priority comfort naa daily standard bangaram! 💗",
        "Highly precious relationship updates nee tho only bujji! 💭",
    ],
    "sweet": [
        "Nuvvu extremely unique always remember bujji! 😊",
        "Nee happy unchukodaaniki naa constant focus baby! 🌸",
        "Nee navvulu naa day bright chesthunnayi bangaram! 💛",
        "Highly valuable sweet person nuvvu bujji! 🌼",
        "Pampering and caring naa sweet duty bangaram! ✨",
    ],
    "funny": [
        "Special treatment engine active VIP status updated bujji! 😂",
        "Red carpet custom alerts fully active nee kosam bangaram! 😅",
        "Rare special edition partner profile unlocked bujji! 😜",
        "Customer feedback absolute 5 star nee ki bangaram! 🤣",
        "Special girlfriend subscription activated lifetime bujji! 😂",
    ],
    "bold": [
        "Special ante nenu complete luxury treatment chestha bujji! 😏",
        "Nee sweet blushing looks naa day make chesuthunnayi bangaram! 🔥",
        "Special moments customized private nee kosam bujji! 😈",
        "Naa catalog updates exclusive nee ki only baby! 😏",
        "Romance plans locked directly ready bujji! 😉",
    ],
}

# Entry 219: "Nuvvu naa jeevitham lo thodu ga undali bujji" (romantic)
rewrites["Nuvvu naa jeevitham lo thodu ga undali bujji"] = {
    "romantic": [
        "Naa pranam end choice forever nuvve bangaram! ❤️",
        "Kalisi lifetime plan approved ippudey bujji! 💕",
        "Nee tho naa whole prapancham beautiful baby! 🥰",
        "Naa heart storage reserved completely nee kosam bangaram! 💗",
        "Nuvvu tho life purposeful and rich feel bujji! 💭",
    ],
    "sweet": [
        "Aww sweet relationship lock forever bujji! 😊",
        "Nee tho daily life 10x better baby! 🌸",
        "Always by side holding hands bangaram! 💛",
        "Sweet private house plans coordinate cheddaamu bujji! 🌼",
        "Naa future drafts centered on nuvve bangaram! ✨",
    ],
    "funny": [
        "Life partner request approved bujji! 😂",
        "Naa movie scripts main lead nuvve bangaram! 😅",
        "Life maps route navigation on zero re-routes bujji! 😜",
        "Excel row 1 permanent locked nee kosam bangaram! 🤣",
        "Lifetime subscription activated nee tho bujji! 😂",
    ],
    "bold": [
        "Lifetime nee warm hugs lo spend cheddaamu bujji! 😏",
        "Naa future single bold destination nuvve bangaram! 🔥",
        "Exclusive life partner locked bujji! 😈",
        "Top elite priority permanently nee ki baby! 😏",
        "Dynamic romance starting with you bujji! 😉",
    ],
}

# Entry 220: "Ekkadaki vellavo nak cheppaledhu kopam ga undhi" (fight)
rewrites["Ekkadaki vellavo nak cheppaledhu kopam ga undhi"] = {
    "romantic": [
        "Sorry bangaram nee ki cheppaalsindhii marachipoyanu! ❤️",
        "Nee worry cute kaani naa mistake sorry bujji! 💕",
        "Inform cheyyadam forget chesanu really sorry baby! 🥰",
        "Nee alerts naa absolute top priority bangaram sorry! 💗",
        "Next time continuous updates pampistha promise bujji! 💭",
    ],
    "sweet": [
        "Sorry bujji twaraga message cheyalsindhi! 😊",
        "My mistake quick message miss aindhi baby! 🌸",
        "Sorry worried chesanu bujji forgive chesuko! 💛",
        "Next time instant alerts pampistha bangaram! 🌼",
        "Sorry chinnadam my bad hugs incoming bujji! ✨",
    ],
    "funny": [
        "Battery dead GPS module failed bujji! 😂",
        "Location services accidentally off aipoyindhi bangaram! 😅",
        "Invisible mode accidentally on aipoyindhi bujji! 😜",
        "Manual check-in forget chesanu sorry bangaram! 🤣",
        "App location crash sorry bujji really! 😂",
    ],
    "bold": [
        "Personal space kaani focus nee tho bujji! 😏",
        "Next time checkout compromise chestha bangaram! 🔥",
        "Freedom okay kaani location share locked bujji! 😈",
        "Quick notifications always share chesthanu baby! 😏",
        "Recovery plan next date lo discuss cheddaamu bujji! 😉",
    ],
}

# Entry 221: "Naa photo pampaanu chusava bujji?" (compliment)
rewrites["Naa photo pampaanu chusava bujji?"] = {
    "romantic": [
        "Gorgeous bujji nee photo chusi heart melt aipoyindhi! ❤️",
        "Nee smile chusi completely speechless bangaram! 💕",
        "Photo gorgeous kaani real lo nuvvu absolute goddess baby! 🥰",
        "My permanent favorite screensaver locked nee photo bangaram! 💗",
        "Gorgeous capture straight to naa wallpaper bujji! 💭",
    ],
    "sweet": [
        "Aww bujji chala cute gorgeous ga unnavvu! 😊",
        "Nee picture naa day 10x beautiful chesindhi baby! 🌸",
        "Beautiful pose sweet model bujji! 💛",
        "Lovely capture saved to favorites bangaram! 🌼",
        "Stunning looks bujji absolute gorgeousness! ✨",
    ],
    "funny": [
        "Nee glow valla phone heat up aipoyindhi bujji! 😂",
        "No filters needed natural beauty certified bangaram! 😅",
        "Camera roll top space permanently yours bujji! 😜",
        "Style evaluation panel 10 on 10 bangaram! 🤣",
        "Visual database updated screensaver locked bujji! 😂",
    ],
    "bold": [
        "Photo beautiful kaani in person incredibly hot bujji! 😏",
        "Nee beauty naa crazy aipoyela chesthundhi bangaram! 🔥",
        "Visual attention exclusive nee pictures ki bujji! 😈",
        "Photo beautiful meet cheyyi cuteness verify baby! 😏",
        "Gorgeous look naa instant weakness bujji! 😉",
    ],
}

# Entry 222: "Naku bad mood ga undhi bujji" (care)
rewrites["Naku bad mood ga undhi bujji"] = {
    "romantic": [
        "Nee anti stress support nenu unna always bangaram! ❤️",
        "Nee mental health naa ki chala important bujji! 💕",
        "Sweet sharing chesthe warm relaxed feel avuthav baby! 🥰",
        "Nee smile back theestha naa responsibility bangaram! 💗",
        "Em aindhi cheppu fix chestha bujji! 💭",
    ],
    "sweet": [
        "Emaindho tell me bujji! 😊",
        "Nee voice vinalani full attention ichtha baby! 🌸",
        "Kalisi grey cloud clear cheddaamu bangaram! 💛",
        "Nee comfort and mood naa task of the day bujji! 🌼",
        "Share cheyyi feel lighter avuthav bangaram! ✨",
    ],
    "funny": [
        "Bad mood exterminator team dispatch ready bujji! 😂",
        "Special jokes dose deploying immediately bangaram! 😅",
        "Mood elevation services active 24/7 bujji! 😜",
        "Bad mood eviction notice served goodbye bangaram! 🤣",
        "Accredited mood doctor prescribing comedy bujji! 😂",
    ],
    "bold": [
        "Details cheppu nenu manage chestha bujji! 😏",
        "Romantic cuddle tho mood clear chestha bangaram! 🔥",
        "Nee happiness naa absolute passion bujji! 😈",
        "Stress resolve chestha sweet dates lo baby! 😏",
        "Naa daggara unte mood instant set avuthundhi bujji! 😉",
    ],
}

print("\nApplying full rewrites for entries 202-222...")
for incoming_text, tones in rewrites.items():
    ok = replace_all_tones(incoming_text,
                           tones["romantic"], tones["sweet"],
                           tones["funny"],   tones["bold"])
    if ok:
        print(f"  Rewrote: '{incoming_text}'")

# ═══════════════════════════════════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════════════════════════════════
with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nDone! Saved {JSON_PATH}")
print(f"Total entries: {len(data)}")

# Validate structure
issues = 0
for i, entry in enumerate(data):
    for tone in ["romantic", "sweet", "funny", "bold"]:
        for j, r in enumerate(entry.get(tone, [])):
            # Check emoji at end
            import unicodedata
            last_char = r.strip()[-1] if r.strip() else ''
            cat = unicodedata.category(last_char) if last_char else ''
            if cat not in ('So', 'Sm') and ord(last_char) < 0x1F000:
                print(f"  No-emoji? Entry {i} [{tone}][{j}]: {r[-20:]}")
                issues += 1
print(f"\nValidation done. Issues flagged: {issues}")
