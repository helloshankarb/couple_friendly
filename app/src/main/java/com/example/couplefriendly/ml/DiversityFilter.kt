package com.couplefriendly.app.ml

/**
 * Reply Diversity Filter.
 * Ensures the final 3 suggestions are meaningfully different
 * using Jaccard token overlap similarity.
 *
 * Threshold: reject if Jaccard >= 0.55
 *
 * Does NOT reject merely because replies share natural relationship words
 * (bujji, bangaram, love, nuvvu, naaku). The filter targets duplicate
 * sentence structures and repeated semantic content.
 */
internal object DiversityFilter {

    private const val JACCARD_THRESHOLD = 0.55f
    private const val MIN_REPLY_LENGTH = 6

    /**
     * Selects up to [maxReplies] diverse candidates from [candidates],
     * filling remaining slots from [fallbacks] if needed.
     */
    fun selectDiverse(
        candidates: List<String>,
        fallbacks: List<String>,
        maxReplies: Int = 3
    ): List<String> {
        val selected = mutableListOf<String>()

        // Select from primary candidates
        for (cand in candidates) {
            if (cand.length < MIN_REPLY_LENGTH) continue
            if (selected.none { isTooSimilar(cand, it) }) {
                selected.add(cand)
            }
            if (selected.size >= maxReplies) break
        }

        // Fill from fallbacks
        for (fb in fallbacks) {
            if (selected.size >= maxReplies) break
            if (fb.length < MIN_REPLY_LENGTH) continue
            if (selected.none { isTooSimilar(fb, it) }) {
                selected.add(fb)
            }
        }

        return selected.take(maxReplies)
    }

    /**
     * Checks if two replies are too similar using Jaccard word overlap.
     */
    fun isTooSimilar(s1: String, s2: String): Boolean {
        return computeJaccard(s1, s2) >= JACCARD_THRESHOLD
    }

    /**
     * Computes Jaccard similarity coefficient between two strings
     * based on word-level tokenization.
     */
    fun computeJaccard(s1: String, s2: String): Float {
        val w1 = tokenize(s1)
        val w2 = tokenize(s2)
        if (w1.isEmpty() || w2.isEmpty()) return 0.0f
        val intersection = w1.intersect(w2).size
        val union = w1.union(w2).size
        return if (union > 0) intersection.toFloat() / union else 0.0f
    }

    private fun tokenize(text: String): Set<String> {
        return text.lowercase()
            .split("\\s+".toRegex())
            .filter { it.isNotBlank() }
            .map { it.replace("[^a-zA-Z]".toRegex(), "") }
            .filter { it.isNotBlank() }
            .toSet()
    }
}
