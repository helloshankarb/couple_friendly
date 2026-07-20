import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('app/src/main/assets/flirt_dataset.json','r',encoding='utf-8') as f:
    data = json.load(f)

# Find user's specific examples
print('=== Checking user examples ===')
targets = ['nacchinadhi naa adrushtam', 'taste ochindhi', 'sleep aavatle']
for entry in data:
    for tone in ['romantic','sweet','funny','bold']:
        if tone in entry:
            for s in entry[tone]:
                for t in targets:
                    if t in s.lower():
                        print(f'  FOUND: {s}')

# Find "naa [English_word]" patterns (translated feel like "naa luck", "naa dream")
print('\n=== "naa [English]" patterns (translated feel) ===')
eng_nouns = ['luck','dream','strength','weakness','addiction','obsession','priority',
    'mission','goal','treasure','motivation','inspiration','reason','purpose',
    'reward','gift','blessing','surprise','favorite','achievement','trophy',
    'crown','kingdom','territory','property','energy','power','magic',
    'miracle','secret','reality','fantasy','destiny','fate','choice',
    'chance','hope','pride','legacy','adventure','journey']
count = 0
for entry in data:
    for tone in ['romantic','sweet','funny','bold']:
        if tone in entry:
            for s in entry[tone]:
                for n in eng_nouns:
                    if re.search(r'naa\s+' + n, s, re.IGNORECASE):
                        if count < 20:
                            print(f'  {s[:80]}')
                        count += 1
                        break
print(f'  Total: {count}')

# Find "ne/nee [English_noun]" patterns 
print('\n=== "ne/nee [English]" patterns ===')
count2 = 0
for entry in data:
    for tone in ['romantic','sweet','funny','bold']:
        if tone in entry:
            for s in entry[tone]:
                for n in eng_nouns:
                    if re.search(r'(ne|nee)\s+' + n, s, re.IGNORECASE):
                        if count2 < 15:
                            print(f'  {s[:80]}')
                        count2 += 1
                        break
print(f'  Total: {count2}')

# Find "English_word + aipoy/vasth/ochindhi" (translated verb constructions)
print('\n=== "[English] aipoy/vasth/ochindhi" translated constructions ===')
translated_verbs = re.compile(r'\b(luck|taste|peace|patience|happiness|sadness|anger|pride|shame|guilt|fear|courage|confidence|hope|faith|trust|respect|love|hate|jealousy|envy|greed|desire|passion|pleasure|pain|comfort|relief|satisfaction|joy|sorrow|grief|regret|remorse|nostalgia|longing|yearning|craving|hunger|thirst|fatigue|exhaustion|boredom|excitement|anticipation|curiosity|wonder|awe|surprise|shock|horror|disgust|contempt|pity|sympathy|empathy|compassion|gratitude|appreciation|admiration|affection|devotion|loyalty|commitment|dedication|determination|ambition|motivation|inspiration|creativity|imagination|intelligence|wisdom|knowledge|understanding|awareness|consciousness|intuition|instinct|impulse|urge|temptation|obsession|addiction|dependency|attachment|bond|connection|relationship|friendship|partnership|alliance|rivalry|competition|conflict|tension|stress|pressure|burden|responsibility|obligation|duty|honor|dignity|integrity|virtue|morality|ethics|justice|fairness|equality|freedom|liberty|independence|autonomy|sovereignty|authority|power|control|dominance|influence|impact|effect|consequence|result|outcome|success|failure|achievement|accomplishment|progress|growth|development|improvement|advancement|innovation|revolution|transformation|change|transition|evolution|adaptation|survival|existence|reality|truth|honesty|sincerity|authenticity|genuineness|originality|uniqueness|individuality|identity|personality|character|nature|essence|spirit|soul|heart|mind|body|health|wellness|fitness|beauty|grace|elegance|charm|charisma|appeal|attraction|magnetism|chemistry|spark|flame|fire|heat|warmth|light|glow|shine|brilliance|radiance|splendor|glory|majesty|grandeur|magnificence|excellence|perfection|quality|standard|class|style|fashion|trend|culture|tradition|heritage|legacy|history|memory|nostalgia|sentiment|emotion|feeling|sensation|experience|adventure|journey|voyage|expedition|quest|mission|purpose|meaning|significance|importance|value|worth|merit|potential|possibility|opportunity|chance|luck|fortune|fate|destiny|providence|miracle|wonder|mystery|enigma|puzzle|riddle|paradox|dilemma|challenge|obstacle|barrier|hurdle|setback|difficulty|hardship|struggle|fight|battle|war|conflict|crisis|emergency|disaster|catastrophe|tragedy|loss|defeat|surrender|retreat|escape|refuge|sanctuary|haven|paradise|heaven|utopia|dream|fantasy|illusion|delusion|hallucination|vision|prophecy|prediction|forecast|expectation|anticipation|suspense|tension|drama|comedy|tragedy|irony|sarcasm|humor|wit|satire|parody|mockery|ridicule|criticism|judgment|opinion|perspective|viewpoint|standpoint|position|stance|attitude|approach|method|technique|strategy|tactic|plan|scheme|plot|conspiracy|intrigue|scandal|controversy|debate|argument|discussion|conversation|dialogue|monologue|speech|address|lecture|sermon|presentation|performance|show|spectacle|display|exhibition|demonstration|ceremony|ritual|celebration|festival|party|gathering|meeting|conference|summit|forum|assembly|congress|parliament|senate|council|board|committee|panel|jury|court|tribunal|hearing|trial|case|lawsuit|prosecution|defense|verdict|sentence|punishment|penalty|fine|fee|charge|cost|price|expense|budget|investment|profit|loss|revenue|income|salary|wage|payment|reward|bonus|tip|donation|contribution|gift|present|offering|sacrifice|tribute|homage|respect|honor|recognition|acknowledgment|appreciation|gratitude|thanks|praise|compliment|flattery|admiration|adoration|worship|devotion|loyalty|allegiance|commitment|dedication|passion|enthusiasm|zeal|fervor|intensity|urgency|desperation|determination|resolution|perseverance|persistence|tenacity|resilience|endurance|stamina|strength|power|force|energy|vitality|vigor)\s+(aipoy|vasth|ochindhi|undhi|avth|ledu)', re.IGNORECASE)
count3 = 0
for entry in data:
    for tone in ['romantic','sweet','funny','bold']:
        if tone in entry:
            for s in entry[tone]:
                if translated_verbs.search(s):
                    if count3 < 15:
                        print(f'  {s[:80]}')
                    count3 += 1
print(f'  Total: {count3}')
