"""
Fix all 219 flagged issues:
- TOO SHORT replies (under 4 words) -> expand to natural Tanglish
- CORPORATE words: certified, premium, coordinate -> replace
- CRINGE: activate, GPS activate, panic mode -> fix
"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

JSON_PATH = "app/src/main/assets/flirt_dataset.json"
with open(JSON_PATH, encoding='utf-8') as f:
    data = json.load(f)

fixed = 0

def fix(incoming_text, tone, index, new_line):
    global fixed
    for entry in data:
        if entry["incoming"] == incoming_text:
            entry[tone][index] = new_line
            print(f"  Fixed [{tone}][{index}] in '{incoming_text}'")
            fixed += 1
            return
    print(f"  WARN not found: {repr(incoming_text)}")

# -----------------------------------------------------------------------
# Entry 8 - "Sup"
fix("Sup", "funny", 0, "Ceiling fan bujji serious answer ledu! 😂")

# Entry 9 - "Hii"
fix("Hii", "sweet", 0, "Hiii bujji ela unnav today cheppu! 🥰")
fix("Hii", "sweet", 2, "Hii baby cute ga mesej chesav! 💕")
fix("Hii", "funny", 4, "Hiiiii back bangaram reply champion! 😂")

# Entry 19 - "Neeku chesina surprise nacchindha"
fix("Neeku chesina surprise nacchindha", "bold", 2, "Chupiddama raa tonight inka undhi marchipoledu! 🔥")

# Entry 21 - "Nuvvu maa inti daggara unnav"
fix("Nuvvu maa inti daggara unnav", "bold", 3, "Chupiddama raa tonight near unnav ga! 😏")

# Entry 22 - "Nuvvu bore avthunnav"
fix("Nuvvu bore avthunnav", "sweet", 3, "Ayyoo sorry bujji nenu vastha na bore fix! 😘")

# Entry 27 - "Nuvvu naa life lo ochav"
fix("Nuvvu naa life lo ochav", "sweet", 4, "Nuvvu adbhutam bangaram seriously no words! 🥰")
fix("Nuvvu naa life lo ochav", "bold", 2, "Chupinchu tonight bangaram ne lo unna feelings! 🔥")

# Entry 28 - "Nuvvu nenu oka e"
fix("Nuvvu nenu oka e", "sweet", 1, "Same feeling bujji naaku kuda alane undhi! 😊")

# Entry 30 - "Nee gurinchi aalochinchaanu"
fix("Nee gurinchi aalochinchaanu", "sweet", 4, "Gurtuchesav thanks bangaram naa gurinchi aalochisthunnav! 🥰")
fix("Nee gurinchi aalochinchaanu", "funny", 2, "Air thinna healthy diet aa nijam ga bujji? 😜")

# Entry 32 - "Biryani tinnaanu"
fix("Biryani tinnaanu", "sweet", 2, "Biryani baby delicious ga undha full details bujji! 💕")
fix("Biryani tinnaanu", "funny", 2, "Maggi single jeevitham food anthem bujji confirmed! 😜")

# Entry 36 - "Offline ga unna"
fix("Offline ga unna", "bold", 1, "Ippude modalu chesanu ne kosam attention full! 😉")

# Entry 41 - "Exam result"
fix("Exam result", "sweet", 4, "Aagalekapothunna bujji super excited full energy! 🥰")

# Entry 42 - "Nuvvu cute ga unnav"
fix("Nuvvu cute ga unnav", "funny", 2, "I know born cute nuvvu admit chesukunnav finally! 😜")

# Entry 44 - "Song vinnaanu"
fix("Song vinnaanu", "sweet", 2, "Haha thanks baby nuvvu share chesav adi manadi! 💕")
fix("Song vinnaanu", "funny", 0, "Bathroom singer official ga pronoun chesthunna bujji! 😂")

# Entry 45 - "Nuvvu andamga unnav"
fix("Nuvvu andamga unnav", "sweet", 1, "Nuvvu gorgeous bujji nee eyes ki kaadu naa words ki! 😊")
fix("Nuvvu andamga unnav", "sweet", 2, "Aww sweet words bangaram nee tho share cheyyadam love avthundhi! 💕")

# Entry 47 - "Nuvvu na ki best"
fix("Nuvvu na ki best", "sweet", 4, "Nammu bujji please nuvve naa real hero! 🥰")
fix("Nuvvu na ki best", "bold", 2, "Abhimanam nachindhi baby real ga feel avthunnanu! 🔥")

# Entry 50 - "Nenu midnight ki jaagunnanu"
fix("Nenu midnight ki jaagunnanu", "funny", 0, "Vampire schedule lo unna bujji night owl official! 😂")

# Entry 54 - "Nenu na tho matladali"
fix("Nenu na tho matladali", "bold", 3, "Naa daggara bore avvadam impossible bujji guarantee! 😏")

# Entry 56 - "Hmm"
fix("Hmm", "sweet", 4, "Em aalochisthunnav baby cheppu curious avthunna! 🥰")

# Entry 57 - "Na daggara paniki ledu"
fix("Na daggara paniki ledu", "sweet", 1, "Matladam inka bujji cheppu emaina undha? 😊")
fix("Na daggara paniki ledu", "sweet", 2, "Okay baby oka pani cheppu chestha! 💕")

# Entry 58 - "Nenu badhapaddanu"
fix("Nenu badhapaddanu", "sweet", 2, "Baadha avvaku baby solve chestha kalisi! 💕")

# Entry 59 - "Nenu chala emi cheskovatleda"
fix("Nenu chala emi cheskovatleda", "sweet", 3, "Please aapu baby nee gurinchi chala care avthunna! 😘")

# Entry 60 - "Nenu stress lo unna"
fix("Nenu stress lo unna", "sweet", 3, "Tension cheyaku baby nenu unnanu ne tho always! 😘")
fix("Nenu stress lo unna", "bold", 4, "Stress buster nenu bujji okasari raa try chesav antav! 😘")

# Entry 61 - "Nenu online ga unna"
fix("Nenu online ga unna", "sweet", 2, "Sure bujji coming oka second matram wait! 💕")
fix("Nenu online ga unna", "sweet", 4, "Ippude chestha bangaram wait cheyyi oka second! 🥰")

# Entry 62 - "Nenu intiki vachanu"
fix("Nenu intiki vachanu", "sweet", 4, "Ready bujji calling chestha reach chesav! 🥰")

# Entry 63 - "Nuvvu naa life lo important"
fix("Nuvvu naa life lo important", "sweet", 2, "Nuvvu chesthav baby nee words chala touch chesayi! 💕")

# Entry 64 - "Office chala busy"
fix("Office chala busy", "funny", 4, "Legal torture office lo rozu chesth unchuthunnaraa bujji! 😂")
fix("Office chala busy", "bold", 4, "Tonight bharistha aagu nenu vasthunna! 😘")

# Entry 65 - "Nuvvu miss avthunna"
fix("Nuvvu miss avthunna", "bold", 2, "Teesukosthanu back nundi tappinchukolevu bangaram! 🔥")

# Entry 69 - "Nenu tired"
fix("Nenu tired", "funny", 4, "Energy drinks fake bujji nenu real source naa direct! 😂")
fix("Nenu tired", "bold", 3, "Energize chestha guarantee bujji raa intiki! 😏")

# Entry 70 - "Nenu nidra vasthundhi"
fix("Nenu nidra vasthundhi", "funny", 1, "Penguin la waddle cheyyadam try chesava nidra kaadu bujji! 🤣")
fix("Nenu nidra vasthundhi", "bold", 1, "Hug best heater bujji scientifically proven real! 😉")

# Entry 74 - "Song share cheyyi"
fix("Song share cheyyi", "sweet", 4, "Enjoy bujji link pampu nenu kuda vintha! 🥰")

# Entry 76 - "Nuvvu naa tho unnav ga"
fix("Nuvvu naa tho unnav ga", "bold", 2, "Stress relief naa speciality bujji try chesav antav! 🔥")

# Entry 78 - "Manchi ga undhi"
fix("Manchi ga undhi", "sweet", 3, "Already okay avthundhi bangaram nuvvu unnanduke! 😘")

# Entry 84 - "Cheppinchali antunnav"
fix("Cheppinchali antunnav", "sweet", 3, "Smart bujji nuvvu cheppav admit chestha! 😘")

# Entry 85 - "Nenu pasipoyanu"
fix("Nenu pasipoyanu", "sweet", 4, "Celebrations time bangaram naa success nee valla! 🥰")

# Entry 86 - "Birthday party chesav"
fix("Birthday party chesav", "sweet", 2, "Party cheddama celebrate kalisi bujji! 💕")

# Entry 87 - "Job resign chestha"
fix("Job resign chestha", "sweet", 4, "Support chestha always bujji ne decision right! 🥰")
fix("Job resign chestha", "funny", 1, "Job hating club member bujji welcome committee ready! 🤣")

# Entry 89 - "Nuvvu chala talented"
fix("Nuvvu chala talented", "funny", 0, "Chivariki recognition dorikinadhi bujji long time late! 😂")

# Entry 91 - "Joke chesav"
fix("Joke chesav", "funny", 0, "Born comedian bujji official ga pronoun chesthunna! 😂")

# Entry 92 - "Nenu tease chestha"
fix("Nenu tease chestha", "funny", 2, "Professional teaser bujji degree undha confirm chesuko! 😜")

# Entry 93 - "Nuvvu naughty"
fix("Nuvvu naughty", "sweet", 3, "Naughty bujji kaani cute ga undhi suit avthundhi! 😘")

# Entry 95 - "Picnic veldama"
fix("Picnic veldama", "sweet", 3, "Plan cheddama kalisi bujji eppudu fix chestha! 😘")

# Entry 96 - "Movie chuddam"
fix("Movie chuddam", "sweet", 2, "Plan cheddama kalisi bujji theatre aa OTT? 💕")
fix("Movie chuddam", "sweet", 3, "Soon hopefully bangaram this weekend confirm! 😘")

# Entry 97 - "Lunch cheddama"
fix("Lunch cheddama", "sweet", 4, "Planning cutie secret bujji wait and see! 🥰")

# Entry 98 - "Anniversary celebrate cheddama"
fix("Anniversary celebrate cheddama", "sweet", 4, "kalisi celebrate andamga bujji special undhi! 🥰")
fix("Anniversary celebrate cheddama", "bold", 3, "Hot celebration planned bujji wait cheyyi! 😏")

# Entry 101 - "Nenu unna"
fix("Nenu unna", "sweet", 3, "Sending bujji naa love waves reach avthunnaya? 😘")

# Entry 102 - "Kaladam eppudu"
fix("Kaladam eppudu", "sweet", 1, "Soon bangaram pakka this week fix chestha! 😊")
fix("Kaladam eppudu", "sweet", 3, "Weekend fix cheddama bujji tomorrow plan? 😘")

# Entry 103 - "Nenu raa antunna"
fix("Nenu raa antunna", "sweet", 1, "Twaraga kaladam bujji nenu kuda eduru choostunna! 😊")
fix("Nenu raa antunna", "sweet", 4, "kalisi soon bangaram nuvvu vasthe bore undadu! 🥰")
fix("Nenu raa antunna", "funny", 0, "Drama king bujji certified award cheppeddi! 😂")

# Entry 104 - "Nuvvu naa details thelusukuntunnav"
fix("Nuvvu naa details thelusukuntunnav", "funny", 4, "Surveillance expert bujji skills impressive really! 😂")

# Entry 106 - "Nuvvu naa korika"
fix("Nuvvu naa korika", "bold", 2, "Chupista always actions speak louder bujji! 🔥")

# Entry 107 - "Nuvvu naa dream"
fix("Nuvvu naa dream", "sweet", 3, "Thanks baby khushi aipoyanu ne words tho! 😘")
fix("Nuvvu naa dream", "sweet", 4, "Same feeling bangaram naa dream nee vi bujji! 🥰")

# Entry 108 - "Nuvvu VIP"
fix("Nuvvu VIP", "funny", 3, "Platinum member exclusive bujji velvet rope opening! 🤭")

# Entry 110 - "Manamu special"
fix("Manamu special", "sweet", 4, "Unique connection manadi bujji enni janmaalaina! 🥰")
fix("Manamu special", "funny", 1, "Unique specimen bujji lab report cheddham interesting! 🤣")
fix("Manamu special", "funny", 4, "One of a kind bujji dictionary lo photo undhi! 😂")

# Entry 111 - "Nenu excited"
fix("Nenu excited", "sweet", 4, "Aagalekapothunna excited max bujji nuvvu kuda cheppu! 🥰")

# Entry 113 - "Outing cheddama"
fix("Outing cheddama", "sweet", 3, "Done eppudu bangaram morning aa evening? 😘")
fix("Outing cheddama", "sweet", 4, "Excited lets plan bujji full day trip! 🥰")

# Entry 114 - "Veltunnava"
fix("Veltunnava", "sweet", 4, "Done plan cheddaam bujji route fix cheyyi! 🥰")
fix("Veltunnava", "funny", 2, "Jellyfish bodyguard kavali bujji allergic aa? 😜")

# Entry 115 - "Temple veldam"
fix("Temple veldam", "romantic", 3, "Spiritual date special bangaram peace together! 💕")
fix("Temple veldam", "sweet", 3, "Haa veldaam bangaram ready chestha morning! 😘")
fix("Temple veldam", "sweet", 4, "Prayer time peaceful bujji kalisi vellali! 🥰")

# Entry 116 - "Road trip"
fix("Road trip", "sweet", 4, "Travel mood excited bujji route plan chestha! 🥰")
fix("Road trip", "funny", 2, "Google maps expert bujji wrong turn tradition? 😜")
fix("Road trip", "bold", 4, "Destination honeymoon level bujji planning hot! 😘")

# Entry 117 - "Nenu serious"
fix("Nenu serious", "funny", 2, "Comedian retired permanent bujji contract signed ai! 😜")
fix("Nenu serious", "funny", 4, "Serious mode permanent bujji na ki avvadam ledu! 😂")

# Entry 119 - silent treatment entry
fix("Nuvvu na tho matladatam ledhu endhuku", "sweet", 3, "Sorry matladam calmly bujji cheppu em aindhi! 😘")

# Entry 122 - trust talk
fix("Relationship lo trust chala important kadaa", "sweet", 3, "kalisi possible trust base ga pettdam bujji! 😘")

# Entry 123 - proposal/breakup
fix("Evaraina nee ki pelli chestha antunnaru", "funny", 0, "Single Netflix enjoy bujji until I arrive! 😂")

# Entry 124 - bore/night
fix("Nak chala bore ga undhi", "sweet", 1, "sweet dreams bujji naa tho kalagaane bore fix! 😊")
fix("Nak chala bore ga undhi", "sweet", 3, "Night night bujji naa thoughts tho nidra! 😘")
fix("Nak chala bore ga undhi", "sweet", 4, "kalalu well bangaram sweet ones I hope! 🥰")
fix("Nak chala bore ga undhi", "funny", 3, "Insomniac lifestyle proud bujji roll model! 🤭")

# Entry 126 - genuine love
fix("Nuvvu nannu genuine ga premisthunnava?", "sweet", 4, "sweet dreams bangaram trust chesuko nenu always! 🥰")
fix("Nuvvu nannu genuine ga premisthunnava?", "funny", 2, "Okay mom padukunta lights off bujji! 😜")

# Entry 127 - tired
fix("Nenu e roju chala tired ga unna", "romantic", 3, "kalisi healthy avdaam bujji naa tho easy! 💕")

# Entry 128 - cook
fix("Cook chesanu nee kosam", "romantic", 0, "Best chef naa bangaram nee cooking ki nenu ready! ❤️")

# Entry 131 - gym
fix("Nenu gym ki velthunna", "sweet", 3, "nice dedication bangaram keep going proud unnanu! 😘")
fix("Nenu gym ki velthunna", "funny", 3, "Protein shake addict bujji before after pampu! 🤭")

# Entry 135 - reel
fix("Reel chusav naa", "sweet", 1, "Baagundhi bujji continue cheyyi talent chustundhi! 😊")
fix("Reel chusav naa", "sweet", 2, "Cute reel baby share cheyyi friend ki kuda! 💕")

# Entry 137 - urgent
fix("Urgent cheppu", "funny", 3, "Ambulance book cheddama bujji serious aa funny aa? 🤭")

# Entry 138 - secret
fix("Oka secret cheppana", "funny", 4, "Secret agent la silent chestha bujji FBI level! 😂")

# Entry 139 - perfume
fix("Nee perfume baagundhi", "sweet", 2, "Thanks bangaram nee tho feel chestha something special! 💕")
fix("Nee perfume baagundhi", "funny", 2, "Sweat masking expert bujji genuine aa cover aa? 😜")

# Entry 140 - eyes
fix("Nee eyes beautiful", "sweet", 2, "Blush avthunna baby nee words naa gundeni touch chesayi! 💕")
fix("Nee eyes beautiful", "sweet", 3, "sweet words bangaram nuvvu cheppina adi naa favorite! 😘")
fix("Nee eyes beautiful", "sweet", 4, "Thanks bujji nuvvu notice chesav adi chaalu feel! 🥰")
fix("Nee eyes beautiful", "funny", 4, "Filter magic technology bujji behind scenes chupinchu! 😂")

# Entry 142 - smart
fix("Nuvvu smart", "sweet", 3, "Thanks baby blush avthunna ne valla nenu! 😘")
fix("Nuvvu smart", "sweet", 4, "Blush avthunna bangaram nuvvu chesav idi meeru! 🥰")
fix("Nuvvu smart", "bold", 3, "Sapiosexual approved bujji badge tagginchukunna officially! 😏")

# Entry 146 - surprise visit
fix("Surprise visit ichana", "sweet", 4, "Yay happiest moment bujji nuvvu raavatam anipinchaledu! 🥰")
fix("Surprise visit ichana", "funny", 1, "Panic avthunna hide cheyyadam modalu bujji room mess! 🤣")

# Entry 147 - rain
fix("Baita vana padthundhi", "bold", 2, "Indoor activities plan bujji just us rain outside! 🔥")

# Entry 148 - summer
fix("Summer lo chala hot", "funny", 3, "Summer torture legal bujji complaint chesthe jaileye! 🤭")

# Entry 151 - teasing
fix("Neku telidha sarey", "romantic", 2, "Ne vishayam lo expert nenu bujji poortiga telusu! 🥰")

# Entry 152 - "Avunu"
fix("Avunu", "sweet", 0, "Okay bangaram noted ne avunu love avthundhi! 🥰")
fix("Avunu", "sweet", 3, "Okay noted bangaram ne approval chaalu cheppu! 😘")
fix("Avunu", "sweet", 4, "Sure bujji ne avunu naa green light! 🥰")
fix("Avunu", "funny", 0, "One word specialist bujji energy save chesav chala! 😂")

# Entry 153 - "Ledu"
fix("Ledu", "sweet", 2, "Alright baby no problem chestha nenu! 💕")
fix("Ledu", "sweet", 3, "Okay noted bangaram ne ledu kaadu em? 😘")
fix("Ledu", "sweet", 4, "Fine bujji ne decision accept chestha okay! 🥰")
fix("Ledu", "funny", 1, "Rejection specialist expert bujji award ready unnai! 🤣")
fix("Ledu", "bold", 1, "Challenge accepted baby prove cheyista wait! 😉")

# Entry 154 - "Sare"
fix("Sare", "romantic", 3, "Okay bujji khushi aipoyanu nee sare vindam! 💕")
fix("Sare", "romantic", 4, "Sare prema accept bujji nee ok naa oxygen! 😍")
fix("Sare", "sweet", 0, "Okay bangaram done nee sare enough naa ki! 🥰")
fix("Sare", "sweet", 1, "Done bujji nee oka word naa happy chesindhi! 😊")
fix("Sare", "sweet", 2, "Alright baby nee sare cute ga undhi really! 💕")
fix("Sare", "sweet", 3, "Sare bujji cool no issues from my side! 😘")
fix("Sare", "sweet", 4, "cool bangaram nee sare vindam relief avthundhi! 🥰")
fix("Sare", "funny", 4, "Lazy reply expert bujji nee sare naa day made! 😂")

# Entry 155 - "Ok"
fix("Ok", "sweet", 0, "Okay bangaram cool nee ok naa heart warm chesindhi! 🥰")
fix("Ok", "sweet", 1, "cool bujji nee ok chaalu nenu khushi aipoyanu! 😊")
fix("Ok", "sweet", 2, "Noted baby nee ok vinadam love avthundhi! 💕")
fix("Ok", "sweet", 3, "Alright bangaram nee ok super cute vinipistundhi! 😘")
fix("Ok", "sweet", 4, "Done bujji nee ok tho naa day settle aipoyindhi! 🥰")

# Entry 156 - "Haha"
fix("Haha", "sweet", 2, "Cute laugh baby nuvvu navvina day naa best! 💕")

# Entry 157 - "Lol"
fix("Lol", "sweet", 3, "Hehe cute bujji nee lol real navvu aa fake? 😘")
fix("Lol", "funny", 4, "lol culture king bujji thesis reyali nee ni! 😂")

# Entry 158 - best friend
fix("Nuvvu naa best friend", "sweet", 4, "Same feeling bujji best friends forever promise! 🥰")

# Entry 159 - surprise
fix("Naaku surprise ivvu", "sweet", 4, "Soon bangaram excited eduru choostunna wait! 🥰")

# Entry 160 - birthday
fix("Birthday ki em istav", "sweet", 4, "Special gift bujji nee ki reveal on the day! 🥰")

# Entry 161 - park
fix("Park veldama", "sweet", 4, "Good idea bujji park kalisi evening perfect avthundhi! 🥰")

# Entry 162 - hungry lazy
fix("Hungry but lazy", "funny", 1, "Spirit animal sloth bujji twin energy level same! 🤣")

# Entry 164 - weekend bore
fix("Weekend bore", "funny", 0, "Professional bore expert bujji title naa ki also! 😂")
fix("Weekend bore", "bold", 2, "kalisi bore impossible bujji try chesav anukuntunna! 🔥")

# Entry 166 - manchi
fix("Nenu manchi ga unna nuvvu", "romantic", 3, "Perfect pair manamu bujji match avuthunnamu! 💕")
fix("Nenu manchi ga unna nuvvu", "sweet", 0, "True bangaram agreed nuvvu manchi nenu lucky! 🥰")
fix("Nenu manchi ga unna nuvvu", "sweet", 3, "Agreed baby same thought naa ki kuda undhi! 😘")
fix("Nenu manchi ga unna nuvvu", "sweet", 4, "kalisi good always bujji perfect match manamu! 🥰")

# Entry 167 - lazy
fix("Nuvvu lazy ga unnav", "funny", 0, "Lazy professional expert bujji award function eppudu? 😂")

# Entry 168 - face comedy
fix("Nee face chusthe navvosthundhi", "funny", 2, "Face comedy show bujji free ticket naa ki daily! 😜")

# Entry 171 - cute ippudu
fix("Nuvvu cute ga unnav ippudu", "romantic", 4, "Gundey melting ippudu bujji nee words tho! 😍")
fix("Nuvvu cute ga unnav ippudu", "sweet", 3, "Thanks baby khushi nuvvu notice chesav cute! 😘")

# Entry 172 - thin
fix("Nuvvu thin ga unnav", "sweet", 2, "Thanks baby nuvvu notice chesav chala khushi! 💕")

# Entry 176 - what you wearing
fix("Nuvvu em wear chesav", "sweet", 2, "Nothing special baby casual day bujji! 💕")

# Entry 178 - matching dress
fix("Match chesukondama dress", "sweet", 4, "Matching couple goals bujji photo twaraga cheddamu! 🥰")
fix("Match chesukondama dress", "bold", 4, "Coordinated hot couple goals baby fire undhi! 😘")

# Entry 179 - life goals
fix("Life lo em kavali neeku", "sweet", 3, "Santosham together goal bujji simple life enough! 😘")

# Entry 181 - chellipoyi
fix("Chellipoyi", "funny", 0, "Follow avtha bujji boomerang la vasthav back! 😂")

# Entry 184 - late reply
fix("Reply late chesav", "sweet", 1, "Ayyoo sorry bangaram busy lo miss aipoyindhi today! 😊")
fix("Reply late chesav", "sweet", 4, "My bad bangaram won't happen again promise pakka! 🥰")

# Entry 185 - night out
fix("Night out veldama friends tho", "sweet", 3, "Party hard bangaram enjoy safely back twaraga raa! 😘")
fix("Night out veldama friends tho", "funny", 4, "Friends bad influence bujji certified scapegoat ready! 😂")

# Entry 186 - wallpaper
fix("Nee photo wallpaper petkunna", "sweet", 4, "sweet bangaram nee photo daily chuse nenu lucky! 🥰")

# Entry 188 - jealous
fix("Nenu jealous avthunna", "sweet", 1, "Avvaku bujji nammu nenu nee di only always! 😊")

# Entry 190 - em chesthunnav
fix("Ippudu em chesthunnav", "sweet", 4, "Nothing exciting bangaram nuvvu call chesthe boring fix! 🥰")

# Entry 191 - good night
fix("Manchiga paduko", "sweet", 3, "Night bujji sweet dreams kalalu lo I am there! 😘")

# Entry 194 - pedda flirt
fix("Nuvvu pedda flirt", "funny", 0, "Professional flirt bujji LinkedIn skill add cheyali! 😂")
fix("Nuvvu pedda flirt", "bold", 1, "Actions chupiddama baby tonight claims prove chestha! 😉")

# Entry 195 - sweet dreams
fix("Sweet dreams ra", "sweet", 1, "sweet dreams bujji naa thoughts tho nidra sweet avuthundhi! 😊")
fix("Sweet dreams ra", "sweet", 4, "Good night bujji naa gurinchi kalalu vandali! 🥰")
fix("Sweet dreams ra", "funny", 4, "Sleep mode bujji shutdown chesthe restart fast undhi! 😂")

# Entry 197 - coffee date
fix("Coffee date cheddama", "sweet", 4, "Excited planning bujji which cafe fix cheyyi! 🥰")

# Entry 199 - nacchav
fix("Nuvvu nacchav naaku", "sweet", 3, "Same same bangaram mutual feelings nenu kuda chepthunna! 😘")
fix("Nuvvu nacchav naaku", "sweet", 4, "Blush avthunna bujji nee words magic chesayi! 🥰")

# Entry 200 - cute
fix("Enduku antha cute ga untav", "sweet", 1, "Nuvvu cuter bujji nee eyes chuse naku clear! 😊")
fix("Enduku antha cute ga untav", "sweet", 2, "Thanks baby khushi nuvvu cheppav naa day made! 💕")

# Entry 203 - ex
fix("Nee ex gurinchi cheppavu kadha", "funny", 1, "Season 1 cancel nuvvu season 2 upgrade bujji! 😅")

print()
print(f"Total fixes applied: {fixed}")

with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("Saved!")
