package com.couplefriendly.app.ml

import android.content.Context

/**
 * Thin wrapper around LinearNgramClassifier for intent prediction.
 * Uses the exported intent_classifier.json model asset.
 */
internal class IntentClassifier {

    private val classifier = LinearNgramClassifier("Intent")

    val isLoaded: Boolean get() = classifier.isLoaded

    fun loadFromAsset(context: Context, assetPath: String = "ml/intent_classifier.json") {
        classifier.loadFromAsset(context, assetPath)
    }

    /**
     * Predicts the conversational intent for the given normalized text.
     * Returns class label, confidence, and top candidate probabilities.
     */
    fun predict(normalizedText: String): ClassifierOutput {
        return classifier.predict(normalizedText)
    }

    /**
     * Extracts sparse TF-IDF features for the given text.
     * Used by SemanticRetriever for cosine similarity computation.
     */
    fun extractSparseFeatures(text: String): Map<Int, Float> {
        return classifier.extractSparseFeatures(text)
    }
}
