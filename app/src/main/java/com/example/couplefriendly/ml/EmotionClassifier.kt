package com.couplefriendly.app.ml

import android.content.Context

/**
 * Thin wrapper around LinearNgramClassifier for emotion prediction.
 * Uses the exported emotion_classifier.json model asset.
 */
internal class EmotionClassifier {

    private val classifier = LinearNgramClassifier("Emotion")

    val isLoaded: Boolean get() = classifier.isLoaded

    fun loadFromAsset(context: Context, assetPath: String = "ml/emotion_classifier.json") {
        classifier.loadFromAsset(context, assetPath)
    }

    /**
     * Predicts the emotional state for the given normalized text.
     * Returns class label, confidence, and top candidate probabilities.
     */
    fun predict(normalizedText: String): ClassifierOutput {
        return classifier.predict(normalizedText)
    }
}
