package com.couplefriendly.app.ml

import android.content.Context
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * 100% Offline, On-Device CoupleFriendly ML Engine Facade.
 *
 * Exposes a clean, encapsulated public API:
 *   ReplyEngine.generateReplies(rawText, tone)
 *
 * Pipeline:
 *   raw input -> sanitizer -> normalizer -> intent classifier
 *   -> emotion classifier -> hierarchy/prior logic -> semantic retrieval
 *   -> re-ranking -> multi-angle generation -> safety filter
 *   -> diversity filter -> top 3
 *
 * All internal ML terminology (DOMAIN, INTENT, SUB_INTENT, EMOTION,
 * TF-IDF, RETRIEVAL SCORE) is strictly hidden from UI callers.
 */
object ReplyEngine {

    private const val TAG = "CoupleFriendlyMLEngine"

    private val intentClassifier = IntentClassifier()
    private val emotionClassifier = EmotionClassifier()
    private val retriever = SemanticRetriever(intentClassifier)
    private val generator = LocalReplyGenerator(retriever, intentClassifier, emotionClassifier)

    @Volatile
    private var isInitialized = false
    private val initLock = Any()

    /**
     * Initializes all production ML model assets asynchronously on a background thread.
     * Assets are loaded once and cached in memory for the app lifetime.
     */
    fun init(context: Context) {
        if (isInitialized) return

        CoroutineScope(Dispatchers.IO).launch {
            synchronized(initLock) {
                if (isInitialized) return@synchronized
                try {
                    val startMs = System.currentTimeMillis()
                    TanglishNormalizer.init(context)
                    intentClassifier.loadFromAsset(context, "ml/intent_classifier.json")
                    emotionClassifier.loadFromAsset(context, "ml/emotion_classifier.json")
                    retriever.loadFromAsset(context, "ml/scenarios_index.json")

                    isInitialized = true
                    val elapsedMs = System.currentTimeMillis() - startMs
                    Log.i(TAG, "Native ML Engine initialized in ${elapsedMs}ms " +
                        "(intent=${intentClassifier.isLoaded}, " +
                        "emotion=${emotionClassifier.isLoaded}, " +
                        "retriever=${retriever.isLoaded})")
                } catch (e: Exception) {
                    Log.e(TAG, "Failed to initialize ML Engine assets", e)
                }
            }
        }
    }

    private val fallbackReplies = listOf(
        "Nee msg chusthe chaalu bangaram, naa roju perfect ga aipothundhi! ❤️",
        "Cheppu bujji, vintunna! 🥰",
        "Nenu unna ga neetho, eppatiki! 😘"
    )

    /**
     * Synchronous reply generation. Safe to call before async init completes
     * (returns safe fallbacks if models are not yet loaded).
     */
    fun generateRepliesSync(rawText: String, tone: ReplyTone = ReplyTone.SWEET): List<String> {
        if (rawText.isBlank()) return emptyList()
        return try {
            val bundle = generator.generate(rawText, tone)
            if (bundle.replies.isEmpty()) fallbackReplies else bundle.replies
        } catch (e: Exception) {
            Log.e(TAG, "Error in generateRepliesSync", e)
            fallbackReplies
        }
    }

    /**
     * Coroutine-based reply generation for Compose UI callers.
     */
    suspend fun generateReplies(
        rawText: String,
        tone: ReplyTone = ReplyTone.SWEET
    ): List<String> = withContext(Dispatchers.Default) {
        generateRepliesSync(rawText, tone)
    }
}
