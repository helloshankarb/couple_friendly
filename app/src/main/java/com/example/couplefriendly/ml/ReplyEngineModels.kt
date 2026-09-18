package com.couplefriendly.app.ml

/**
 * Clean UI-facing tone enum for CoupleFriendly.
 * Exposes only the 4 conversational styles without any internal ML terms.
 */
enum class ReplyTone(val key: String) {
    SWEET("sweet"),
    ROMANTIC("romantic"),
    FUNNY("funny"),
    BOLD("bold");

    companion object {
        fun fromString(value: String): ReplyTone {
            return when (value.lowercase().trim()) {
                "romantic" -> ROMANTIC
                "funny" -> FUNNY
                "bold" -> BOLD
                else -> SWEET
            }
        }
    }
}

/**
 * Result bundle returned by ReplyEngine.
 * Contains only user-facing reply strings.
 */
data class ReplyGroup(
    val query: String,
    val replies: List<String>,
    val tone: ReplyTone
)

/**
 * Internal classification result.
 */
internal data class ClassifierOutput(
    val label: String,
    val confidence: Float,
    val probabilities: Map<String, Float>
)

/**
 * Internal scenario representation from indexed assets.
 */
internal data class ScenarioVector(
    val id: Int,
    val incoming: String,
    val category: String,
    val domain: String,
    val intent: String,
    val emotion: String,
    val sparseIndices: IntArray,
    val sparseValues: FloatArray,
    val responses: Map<String, List<String>>
)

/**
 * Scored scenario candidate during retrieval and re-ranking.
 */
internal data class ScoredScenario(
    val scenario: ScenarioVector,
    val score: Float,
    val rawSimilarity: Float
)
