package com.couplefriendly.app.ml

/**
 * Multi-Angle Colloquial Tanglish Reply Generator.
 * Generates 3 distinct, purpose-driven replies:
 *   Angle 1: Empathy & Direct Validation
 *   Angle 2: Reassurance & Constructive Action
 *   Angle 3: Affectionate Softening
 *
 * Delegates safety filtering to SafetyFilter and diversity to DiversityFilter.
 */
internal class LocalReplyGenerator(
    private val retriever: SemanticRetriever,
    private val intentClassifier: IntentClassifier,
    private val emotionClassifier: EmotionClassifier
) {

    private val unnaturalTranslations = mapOf(
        ".*don't feel sad please.*" to "Ayyoo bujji, ala baadha padaku please... nenu unna kadha neetho! 🥰",
        ".*ninnu miss avuthunna too.*" to "nenu kuda ninnu chala miss avuthunna bujji! 🥰",
        ".*i miss you too.*" to "nenu kuda ninnu chala miss avuthunna bujji ❤️",
        ".*don't cry please.*" to "please edavaku bujji, naaku chala baadha ga undi 🥰",
        ".*take care please.*" to "baga care theesuko bujji ❤️"
    )

    private val phoneticCorrections = mapOf(
        "alochichadame" to "alochinchadame",
        "puri munigipoyanu" to "poorthiga munigipoya",
        "upiri theesukuntunna" to "nee dhyasa lo unna",
        "oopiri theeskuntunna" to "nee dhyasa lo unna",
        "vunta" to "unta",
        "vuntunna" to "untunna",
        "cheshanu" to "chesa",
        "chesthunnau" to "chesthunna",
        "eduru choostunna" to "wait chesthunna",
        "eduruchoostunna" to "wait chesthunna",
        "badha ga undhi" to "baadhaga undi",
        "badhaga undhi" to "baadhaga undi",
        "vintha" to "vinta",
        "kopam ga" to "kopamga",
        "matladaku" to "matladoddu",
        "vadiley" to "vadilei",
        "cehpthe" to "chepthe",
        "ceyyaku" to "cheyyaku"
    )

    fun cleanupSyntax(text: String): String {
        if (text.isBlank()) return ""
        var clean = text.trim().removeSurrounding("\"").removeSurrounding("'")
        clean = clean.replace("(?i)\\b(ayithe|chesthe|unte|kani|kuda)\\s+([.,!?])".toRegex(), "$1")
        clean = clean.replace("\\s+([,!?.:;])".toRegex(), "$1")
        clean = clean.replace("([,!?])\\1+".toRegex(), "$1")
        clean = clean.replace(",\\s*,+".toRegex(), ",")
        clean = clean.replace("(?i)\\b(Aww|Ayyoo)\\s+\\w+,\\s*Ayyoo\\s+".toRegex(), "Ayyoo ")
        clean = clean.replace("([🥰❤️😊💕😘])\\s*\\1+".toRegex(), "$1")
        clean = clean.replace("\\s+".toRegex(), " ").trim()
        clean = clean.replace("([.,!?])(?=[a-zA-Z])".toRegex(), "$1 ")
        return clean
    }

    fun sanitizeTanglish(text: String): String {
        if (text.isBlank()) return ""
        var clean = cleanupSyntax(text)
        for ((badPat, goodRep) in unnaturalTranslations) {
            clean = clean.replace(badPat.toRegex(RegexOption.IGNORE_CASE), goodRep)
        }
        for ((wrong, right) in phoneticCorrections) {
            val pattern = "(?i)\\b${Regex.escape(wrong)}\\b".toRegex()
            clean = clean.replace(pattern, right)
        }
        clean = clean.replace("(?i)\\bmeeru\\b".toRegex(), "nuvvu")
        clean = clean.replace("(?i)\\bela unnaru\\b".toRegex(), "ela unnav")
        return cleanupSyntax(clean)
    }

    /**
     * Core generation pipeline:
     * Normalization -> Classification -> Retrieval -> Multi-Angle Synthesis
     * -> Safety Filter -> Diversity Filter -> Top 3
     */
    fun generate(userMessage: String, tone: ReplyTone = ReplyTone.SWEET, numReplies: Int = 3): ReplyGroup {
        val normalized = TanglishNormalizer.normalize(userMessage)
        val lowerMsg = normalized.lowercase()

        val intentResult = intentClassifier.predict(normalized)
        val emotionResult = emotionClassifier.predict(normalized)
        val intent = intentResult.label
        val emotion = emotionResult.label

        // --- Contextual overrides for emotionally sensitive grievances ---

        // #032 Crying & emotional distress override
        if (TanglishNormalizer.cryingTokens.any { lowerMsg.contains(it) } &&
            intent in listOf("EMOTIONAL_HURT", "CONFLICT_FRUSTRATION", "CONFLICT")
        ) {
            return ReplyGroup(userMessage, listOf(
                "Nijanga chala sorry bujji, ninnu baadha pettalani asalu anukoledhu... na valla baadha padaku please ❤️",
                "Nee side enti anipinchindo cheppu bangaram, poorthiga vintanu... calm ga matladukundam 🥺",
                "Nuvvu edisthe naaku chala baadha ga untundhi ra... nuvve na bangaram, please smile cheyyi 🥰"
            ), tone)
        }

        // Ignored feelings override
        if (TanglishNormalizer.feelingsTokens.any { lowerMsg.contains(it) } &&
            intent in listOf("EMOTIONAL_HURT", "CONFLICT_FRUSTRATION", "CONFLICT")
        ) {
            return ReplyGroup(userMessage, listOf(
                "Nee feelings naaku chala important bujji, ninnu alochinchakunda hurt chesi unte nijanga sorry. ❤️",
                "Ala anukoku please... nenu epudu nee side eh untanu, nee manasulo emundo cheppu poorthiga vintanu bujji. 🥺",
                "Nuvvu naa life lo entha special oo naaku telusu bangaram, inko sari ila feel avvanivvanu. 🥰"
            ), tone)
        }

        // --- Standard retrieval pipeline ---

        val topScenarios = retriever.retrieve(normalized, intent, emotion, topK = 5)

        // Harvest candidates for the requested tone
        val toneKey = tone.key
        val candidatePool = mutableListOf<String>()
        for (scored in topScenarios) {
            val toneList = scored.scenario.responses[toneKey] ?: emptyList()
            for (text in toneList) {
                if (text.isNotBlank()) {
                    candidatePool.add(sanitizeTanglish(text))
                }
            }
        }

        // Multi-angle fallback pools
        val angleDefaults = getAngleDefaults(intent)

        // Diversity selection via DiversityFilter
        val diverse = DiversityFilter.selectDiverse(
            candidates = candidatePool,
            fallbacks = angleDefaults.map { sanitizeTanglish(it) },
            maxReplies = numReplies
        )

        // Safety gate via SafetyFilter
        val safe = SafetyFilter.filter(diverse, intent, tone)

        // Final syntax polish
        val finalReplies = safe.take(numReplies).map { cleanupSyntax(it) }

        return ReplyGroup(
            query = userMessage,
            replies = finalReplies,
            tone = tone
        )
    }

    private fun getAngleDefaults(intent: String): List<String> {
        return when {
            intent in listOf("EMOTIONAL_HURT", "CONFLICT_FRUSTRATION", "ANGER_ARGUMENT", "BREAKUP_THREATS") -> listOf(
                "Hurt ayithe nijanga sorry bujji. Nee side enti anipinchindo cheppu, poorthiga vinta. ❤️",
                "Ninnu hurt cheyyalani assalu ledu bangaram, manam calm ga matladukundama? 🥺",
                "Ala baadha padaku ra, nuvvu lekunda naaku em tochadu... cool avvu please. 🥰"
            )
            intent == "TEASING" -> listOf(
                "Ninnu tease cheyyadam lo unde kick eh veru bangaram! 😂",
                "Mari intha mudhuga unte evaraina aatapattinchakunda ela untaru bujji? 😜",
                "Nee cute reactions chusthe smile aagadu mari, anthe na tappu em ledu! 🥰"
            )
            intent in listOf("MISSING", "ROMANTIC_STATEMENT", "DEEP_BOND") -> listOf(
                "Nuvvu lekunda unte naaku kuda asalu roju gadavadu bangaram. ❤️",
                "Chala miss avthunna bujji, free ayyaka ventane call chesthava? 🥰",
                "Nee gundello, nee prathi alochana lonae unna chitti, eppatiki neethone unta! 😘"
            )
            else -> listOf(
                "Nee message chusthe chaalu bangaram, naa roju super ga start avuthundhi! ❤️",
                "Cheppu bujji, ivala em plans unnayi neeku? 🥰",
                "Eppudu msg chesthava ani wait chesthunna chitti! 😘"
            )
        }
    }
}
