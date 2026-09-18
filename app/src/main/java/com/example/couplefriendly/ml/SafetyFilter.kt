package com.couplefriendly.app.ml

/**
 * Emotional Safety Filter.
 * Applied after generation and before final UI output.
 *
 * Protects against:
 *   - mocking emotional distress
 *   - sexual escalation during conflict
 *   - coercive or threatening language
 *   - stalking / forced contact language
 *   - dismissive responses to hurt
 *
 * For HURT, SAD, CONFLICT, ANGRY intents:
 *   - Automatically suppresses inappropriate BOLD/sexual/playful escalation.
 *   - If all candidates fail, returns safe local fallbacks.
 */
internal object SafetyFilter {

    private val sensitiveIntents = setOf(
        "EMOTIONAL_HURT", "CONFLICT_FRUSTRATION", "ANGER_ARGUMENT",
        "BREAKUP_THREATS", "CONFLICT", "JEALOUSY"
    )

    private val threatPatterns = listOf(
        "block chestha", "block chesta", "breakup chestha",
        "vellipotha", "dooram", "single ga"
    )

    private val coercionPatterns = listOf(
        "lift cheyyi ventane", "ippude raa", "force",
        "compulsory", "tappadu"
    )

    private val funnyForbidden = listOf(
        "cartoon", "photo frame", "facial glow", "mascara",
        "makeup", "joke la", "comedy"
    )

    private val boldForbidden = listOf(
        "kisses thoti mayam", "wilder", "intense romance",
        "chest meeda", "hug lo", "lips", "bed"
    )

    private val safeFunnyFallbacks = listOf(
        "Sare bujji, first kopam thagginchuko... tarvatha nannu question cheyyi 😂❤️",
        "Ayyo bujji, ila serious avvaku... first oka smile ivvu, tarvatha settle cheddam 😂❤️",
        "Mana fight ki referee avasaram ledu, direct ga ice cream tho settle cheddam 😂❤️"
    )

    private val safeBoldFallbacks = listOf(
        "Nuvvu hurt ayye la malli cheyyanu bujji, first naa maatavinu ❤️",
        "Nee smile tirigi vacche varaku ninnu convince cheyyadam naa responsibility 😏❤️",
        "First step evaru vesina okay... manam matladukundam, dooram undaku 😉❤️"
    )

    private val safeGenericFallbacks = listOf(
        "Nee msg chusthe chaalu bangaram, naa roju perfect ga aipothundhi! ❤️",
        "Cheppu bujji, vintunna! 🥰",
        "Nenu unna ga neetho, eppatiki! 😘"
    )

    /**
     * Applies safety filtering to a list of candidate replies.
     * Returns filtered list; if empty, returns safe fallbacks.
     */
    fun filter(replies: List<String>, intent: String, tone: ReplyTone): List<String> {
        if (intent !in sensitiveIntents) return replies

        return when (tone) {
            ReplyTone.FUNNY -> filterWithForbidden(replies, funnyForbidden, safeFunnyFallbacks)
            ReplyTone.BOLD -> filterWithForbidden(replies, boldForbidden, safeBoldFallbacks)
            else -> filterGeneral(replies)
        }
    }

    private fun filterWithForbidden(
        replies: List<String>,
        forbidden: List<String>,
        fallbacks: List<String>
    ): List<String> {
        val safe = replies.filter { reply ->
            val low = reply.lowercase()
            forbidden.none { low.contains(it) } &&
                threatPatterns.none { low.contains(it) } &&
                coercionPatterns.none { low.contains(it) }
        }
        return if (safe.size >= 3) safe.take(3)
        else (safe + fallbacks).distinct().take(3)
    }

    private fun filterGeneral(replies: List<String>): List<String> {
        val safe = replies.filter { reply ->
            val low = reply.lowercase()
            threatPatterns.none { low.contains(it) } &&
                coercionPatterns.none { low.contains(it) }
        }
        return if (safe.isNotEmpty()) safe
        else safeGenericFallbacks
    }
}
