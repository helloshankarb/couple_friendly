package com.couplefriendly.app.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext

private val DarkColorScheme = darkColorScheme(
    primary = Color(0xFFFF2E93),     // Accent Rose
    secondary = Color(0xFF8A2BE2),   // Accent Violet
    tertiary = Color(0xFF00F5D4),    // Success Emerald
    background = Color(0xFF0D0614),  // Primary Midnight
    surface = Color(0xFF1A0F26),     // Surface Dark
    onBackground = Color(0xFFFFFFFF),
    onSurface = Color(0xFFFFFFFF),
    onPrimary = Color(0xFFFFFFFF)
)

private val LightColorScheme = lightColorScheme(
    primary = Color(0xFFFF2E93),
    secondary = Color(0xFF8A2BE2),
    tertiary = Color(0xFF00F5D4),
    background = Color(0xFF0D0614),
    surface = Color(0xFF1A0F26),
    onBackground = Color(0xFFFFFFFF),
    onSurface = Color(0xFFFFFFFF)
)

@Composable
fun CouplefriendlyTheme(
    darkTheme: Boolean = true, // Default to Dark mode first
    dynamicColor: Boolean = false, // Set dynamic color default to false for premium custom look
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}