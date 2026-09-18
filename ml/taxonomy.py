# -*- coding: utf-8 -*-
"""
CoupleFriendly - Master ML Taxonomy Definition
Defines the canonical 36 intents, 9 emotions, and relational domains.
"""

# 3-Tier Hierarchical Taxonomy: DOMAIN -> INTENT -> SUB_INTENT
HIERARCHICAL_TAXONOMY = {
    "GREETING": {
        "GREETING": ["HI", "HELLO", "HEYY", "MORNING", "NIGHT"]
    },
    "DAILY_RITUALS": {
        "DAILY_CHECKIN": ["WHAT_ARE_YOU_DOING", "WHERE_ARE_YOU", "DID_YOU_EAT", "WORK_CHECK", "TODAY_PLAN", "WAKEUP_CHECK", "BUSY_CHECK"],
        "CALL": ["CALL_REQUEST"]
    },
    "ROMANCE": {
        "ROMANTIC": ["LOVE_EXPRESSION", "MISS_YOU", "AFFECTION", "COMMITMENT", "LOVE_VALIDATION"],
        "INSECURITY": ["ABANDONMENT_FEAR", "REPLACEMENT_FEAR", "PRIORITY_FEAR", "RELATIONSHIP_VALIDATION"]
    },
    "COMPLIMENTS_FLIRT": {
        "COMPLIMENT": ["LOOKS", "SMILE", "OUTFIT", "PHOTO", "EYES", "COMPLIMENT_REQUEST"],
        "FLIRT": ["FLIRTATIOUS_BANTER", "BUTTERFLIES", "BLUSHING"]
    },
    "PLAYFUL_TEASING": {
        "TEASING": ["PLAYFUL_TEASE", "ALLARI", "PRANK", "MISCHIEF"]
    },
    "CONFLICT_DISTRESS": {
        "EMOTIONAL_HURT": ["FEELING_HURT", "CRYING", "SADNESS", "NEGLECT", "IRRITATE"],
        "CONFLICT": ["ANGER", "FRUSTRATION", "ARGUMENT", "STOP_TALKING", "BREAKUP_THREAT"],
        "IGNORING": ["NO_REPLY", "SEEN_IGNORE", "LATE_REPLY", "WAITING"],
        "JEALOUSY": ["OTHER_GIRL_BOY", "CLOSE_FRIEND", "COMPARISON", "CURIOSITY_SUSPICION"],
        "RECONCILIATION": ["APOLOGY", "FORGIVENESS", "PEACE_MAKING"]
    },
    "SHORT_REACTION": {
        "ACKNOWLEDGEMENT": ["HMM", "HAA", "SARE", "OKAY"],
        "QUESTION": ["ENDUKU", "ENTI", "AVUNA", "NIJAMA"],
        "NEGATION": ["LEDU", "ODDU"],
        "REACTION": ["OHH"]
    }
}

DOMAINS = {
    "CONFLICT": [
        "EMOTIONAL_HURT",
        "CONFLICT_FRUSTRATION",
        "ANGER_ARGUMENT",
        "BREAKUP_THREATS",
        "IGNORING",
        "NO_REPLY",
        "APOLOGY_SEEKING",
        "RECONCILIATION"
    ],
    "ROMANCE": [
        "ROMANTIC_STATEMENT",
        "FLIRT_COMPLIMENT",
        "MISSING",
        "JEALOUSY",
        "PROPOSAL",
        "DEEP_BOND"
    ],
    "DAILY_RITUALS": [
        "GREETING_MORNING",
        "GREETING_NIGHT",
        "FOOD_CHECK",
        "HEALTH_CARE",
        "DAILY_ACTIVITY",
        "SLEEP_REST"
    ],
    "PLAYFUL_HUMOR": [
        "TEASING",
        "PLAYFUL_BANTER",
        "JOKING",
        "SARCASM_CUTE"
    ],
    "COMPLIMENTS_MEDIA": [
        "COMPLIMENT_LOOKS",
        "COMPLIMENT_OUTFIT",
        "PHOTO_REQUEST",
        "CALL_REQUEST"
    ],
    "PLANS_OUTINGS": [
        "DATE_REQUEST",
        "MOVIE_TRIP",
        "BOREDOM",
        "GENERAL_CHAT"
    ]
}

# Alias mapping to guarantee robust domain resolution for all test & canonical labels
INTENT_TO_DOMAIN_ALIAS = {
    "MISS_YOU": "ROMANCE",
    "LOVE": "ROMANCE",
    "AFFECTION": "ROMANCE",
    "COMMITMENT": "ROMANCE",
    "INSECURITY": "ROMANCE",
    "LOVE_VALIDATION": "ROMANCE",
    "RELATIONSHIP_VALIDATION": "ROMANCE",
    "BUSY": "DAILY_RITUALS",
    "CALL": "DAILY_RITUALS",
    "DAILY_CHECKIN": "DAILY_RITUALS",
    "FOOD_CHECK": "DAILY_RITUALS",
    "HEALTH_CARE": "DAILY_RITUALS",
    "DAILY_ACTIVITY": "DAILY_RITUALS",
    "COMPLIMENT": "COMPLIMENTS_FLIRT",
    "COMPLIMENT_LOOKS": "COMPLIMENTS_FLIRT",
    "COMPLIMENT_OUTFIT": "COMPLIMENTS_FLIRT",
    "COMPLIMENT_REQUEST": "COMPLIMENTS_FLIRT",
    "FLIRT": "COMPLIMENTS_FLIRT",
    "FLIRT_COMPLIMENT": "COMPLIMENTS_FLIRT",
    "TEASING": "PLAYFUL_TEASING",
    "TEASING/CONFLICT": "CONFLICT_DISTRESS",
    "CONFLICT": "CONFLICT_DISTRESS",
    "CONFLICT_FRUSTRATION": "CONFLICT_DISTRESS",
    "ANGER_ARGUMENT": "CONFLICT_DISTRESS",
    "ANGRY": "CONFLICT_DISTRESS",
    "EMOTIONAL_HURT": "CONFLICT_DISTRESS",
    "NEGLECT": "CONFLICT_DISTRESS",
    "IGNORING": "CONFLICT_DISTRESS",
    "NO_REPLY": "CONFLICT_DISTRESS",
    "WAITING": "CONFLICT_DISTRESS",
    "JEALOUSY": "CONFLICT_DISTRESS",
    "CURIOSITY": "CONFLICT_DISTRESS",
    "APOLOGY": "CONFLICT_DISTRESS",
    "APOLOGY_SEEKING": "CONFLICT_DISTRESS",
    "RECONCILIATION": "CONFLICT_DISTRESS",
    "FORGIVENESS": "CONFLICT_DISTRESS",
    "BREAKUP_THREATS": "CONFLICT_DISTRESS",
    "GREETING": "GREETING",
    "GREETING_MORNING": "GREETING",
    "GREETING_NIGHT": "GREETING",
    "UNKNOWN/NEUTRAL": "SHORT_REACTION",
    "ACKNOWLEDGEMENT": "SHORT_REACTION",
    "NEGATION": "SHORT_REACTION",
    "QUESTION/UNKNOWN": "SHORT_REACTION",
    "QUESTION": "SHORT_REACTION",
    "VALIDATION": "SHORT_REACTION",
    "REACTION": "SHORT_REACTION"
}

def get_hierarchical_domain(intent: str) -> str:
    """Returns the top-level Domain for a given intent or sub-intent recursively."""
    if not intent:
        return "GENERAL"
    i_upper = intent.upper()

    # 1. Direct alias dictionary lookup (O(1))
    if i_upper in INTENT_TO_DOMAIN_ALIAS:
        return INTENT_TO_DOMAIN_ALIAS[i_upper]

    # 2. Check if it's directly a domain name
    for dom in HIERARCHICAL_TAXONOMY:
        if i_upper == dom.upper() or i_upper in dom.upper():
            return dom

    # 3. Recursive check across HIERARCHICAL_TAXONOMY (Intent keys & Sub-Intent arrays)
    for dom, intents_dict in HIERARCHICAL_TAXONOMY.items():
        for int_key, sub_list in intents_dict.items():
            if i_upper == int_key.upper() or i_upper in int_key.upper():
                return dom
            if any(i_upper == sub.upper() or i_upper in sub.upper() for sub in sub_list):
                return dom

    # 4. Fallback to classical DOMAINS list
    for dom, intents in DOMAINS.items():
        if i_upper in [x.upper() for x in intents]:
            # Map classical domain name to hierarchical domain name
            mapping = {
                "CONFLICT": "CONFLICT_DISTRESS",
                "ROMANCE": "ROMANCE",
                "DAILY_RITUALS": "DAILY_RITUALS",
                "PLAYFUL_HUMOR": "PLAYFUL_TEASING",
                "COMPLIMENTS_MEDIA": "COMPLIMENTS_FLIRT",
                "PLANS_OUTINGS": "DAILY_RITUALS"
            }
            return mapping.get(dom, dom)

    return "GENERAL"

ALL_INTENTS = []
for dom, intents in DOMAINS.items():
    ALL_INTENTS.extend(intents)

ALL_EMOTIONS = [
    "HURT",
    "ANGRY",
    "SAD",
    "JEALOUS",
    "MISSING",
    "PLAYFUL",
    "ROMANTIC",
    "EXCITED",
    "NEUTRAL"
]

REPLY_TONES = [
    "ROMANTIC",
    "SWEET",
    "FUNNY",
    "BOLD"
]

# Hard-negative contrast pairs for training & discrimination
HARD_NEGATIVE_PAIRS = [
    {
        "pair_id": "HN_01",
        "intent_a": "TEASING",
        "intent_b": "EMOTIONAL_HURT",
        "shared_tokens": ["enduku", "nannu", "ila"],
        "differentiating_keywords": (["teas", "allari", "prank"], ["edip", "edav", "yedus", "hurt", "kallalo neellu"]),
        "example_a": "Nannu enduku tease chesthunnav?",
        "example_b": "Enduku nannu ila edipisthunnav?"
    },
    {
        "pair_id": "HN_02",
        "intent_a": "NO_REPLY",
        "intent_b": "IGNORING",
        "shared_tokens": ["enduku", "cheyyatledu"],
        "differentiating_keywords": (["reply", "late", "seen", "msg"], ["ignore", "pattinchu", "care ledu", "maripoyav"]),
        "example_a": "Enduku reply ivvatledu?",
        "example_b": "Nuvvu nannu ignore chesthunnav."
    },
    {
        "pair_id": "HN_03",
        "intent_a": "ANGER_ARGUMENT",
        "intent_b": "CONFLICT_FRUSTRATION",
        "shared_tokens": ["kopam", "ardham"],
        "differentiating_keywords": (["kopam", "gussa", "fight"], ["oka sari chepthe", "enni sarlu", "ardham kaada", "chepthe vinava"]),
        "example_a": "Naa meeda enduku kopam?",
        "example_b": "Neeku oka sari chepthe ardham kaada?"
    },
    {
        "pair_id": "HN_04",
        "intent_a": "BREAKUP_THREATS",
        "intent_b": "ANGER_ARGUMENT",
        "shared_tokens": ["matladaku", "vaddu"],
        "differentiating_keywords": (["inkeppudu", "block", "breakup", "dooram undu", "call cheyyaku"], ["kopam ga unna", "fight ayyam", "matladatam ledu"]),
        "example_a": "Inkeppudu naku call or message cheyyaku.",
        "example_b": "Nuvvu natho enduku ila matladuthunnav?"
    },
    {
        "pair_id": "HN_05",
        "intent_a": "MISSING",
        "intent_b": "ROMANTIC_STATEMENT",
        "shared_tokens": ["nuvvu", "love", "prema"],
        "differentiating_keywords": (["miss", "gurthosth", "ontari", "daggara levu"], ["premisthunna", "love you", "pranam", "prapancham"]),
        "example_a": "Chala miss avthunna bujji, eppudu vasthav?",
        "example_b": "Nuvve naa pranam bangaram, chala premisthunna."
    },
    {
        "pair_id": "HN_06",
        "intent_a": "COMPLIMENT_LOOKS",
        "intent_b": "FLIRT_COMPLIMENT",
        "shared_tokens": ["bagunnav", "chala"],
        "differentiating_keywords": (["cute", "beautiful", "handsome", "photo lo"], ["hot", "sexy", "tempting", "attraction", "fidaa"]),
        "example_a": "Ee photo lo chala cute ga unnav bujji.",
        "example_b": "Nee kallaloki chusthe tempt aipothunna baby."
    }
]
