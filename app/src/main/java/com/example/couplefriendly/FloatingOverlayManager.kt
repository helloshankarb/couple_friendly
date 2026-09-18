package com.couplefriendly.app

import android.content.Context
import android.graphics.PixelFormat
import android.os.Bundle
import android.util.Log
import android.view.Gravity
import android.view.View
import android.view.WindowManager
import android.widget.Toast
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.ComposeView
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.tooling.preview.Preview
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.LifecycleRegistry
import androidx.lifecycle.ViewModelStore
import androidx.lifecycle.ViewModelStoreOwner
import androidx.lifecycle.setViewTreeLifecycleOwner
import androidx.lifecycle.setViewTreeViewModelStoreOwner
import androidx.savedstate.SavedStateRegistry
import androidx.savedstate.SavedStateRegistryController
import androidx.savedstate.SavedStateRegistryOwner
import androidx.savedstate.setViewTreeSavedStateRegistryOwner
import kotlinx.coroutines.launch
import kotlin.math.roundToInt

class FloatingOverlayManager(
    private val context: Context,
    private val onReplySelected: (String) -> Unit
) : LifecycleOwner, ViewModelStoreOwner, SavedStateRegistryOwner {

    private val windowManager = context.getSystemService(Context.WINDOW_SERVICE) as WindowManager
    private var overlayView: ComposeView? = null
    
    // Lifecycle Boilerplate for Compose in Service
    private val lifecycleRegistry = LifecycleRegistry(this)
    private val store = ViewModelStore()
    private val savedStateController = SavedStateRegistryController.create(this)

    override val lifecycle: Lifecycle = lifecycleRegistry
    override val viewModelStore: ViewModelStore = store
    override val savedStateRegistry: SavedStateRegistry = savedStateController.savedStateRegistry

    init {
        savedStateController.performRestore(null)
        lifecycleRegistry.handleLifecycleEvent(Lifecycle.Event.ON_CREATE)
    }

    fun show() {
        if (overlayView != null) return
        
        lifecycleRegistry.handleLifecycleEvent(Lifecycle.Event.ON_START)
        lifecycleRegistry.handleLifecycleEvent(Lifecycle.Event.ON_RESUME)

        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = 100
            y = 150
        }

        overlayView = ComposeView(context).apply {
            setViewTreeLifecycleOwner(this@FloatingOverlayManager)
            setViewTreeViewModelStoreOwner(this@FloatingOverlayManager)
            setViewTreeSavedStateRegistryOwner(this@FloatingOverlayManager)
            
            setContent {
                CouplefriendlyTheme {
                    FloatingOverlayContent(
                        onDrag = { dx, dy ->
                            params.x += dx.roundToInt()
                            params.y += dy.roundToInt()
                            windowManager.updateViewLayout(this, params)
                        },
                        onReplySelected = { reply ->
                            onReplySelected(reply)
                        },
                        onCloseOverlay = {
                            hide()
                        }
                    )
                }
            }
        }

        windowManager.addView(overlayView, params)
    }

    fun hide() {
        overlayView?.let {
            lifecycleRegistry.handleLifecycleEvent(Lifecycle.Event.ON_PAUSE)
            lifecycleRegistry.handleLifecycleEvent(Lifecycle.Event.ON_STOP)
            lifecycleRegistry.handleLifecycleEvent(Lifecycle.Event.ON_DESTROY)
            windowManager.removeView(it)
            overlayView = null
        }
    }

    fun isShowing(): Boolean {
        return overlayView != null
    }
}

@Composable
fun FloatingOverlayContent(
    onDrag: (Float, Float) -> Unit,
    onReplySelected: (String) -> Unit,
    onCloseOverlay: () -> Unit
) {
    var isExpanded by remember { mutableStateOf(false) }
    var isIdle by remember { mutableStateOf(false) }
    var isLoading by remember { mutableStateOf(false) }
    var incomingMessage by remember { mutableStateOf("") }

    // Suggestion and Tone states
    val scope = rememberCoroutineScope()
    var currentGroup by remember { mutableStateOf<MessageGroupBundle?>(null) }
    var selectedTone by remember { mutableStateOf("Romantic 💘") }
    val tones = listOf("Romantic 💘", "Sweet 🥰", "Funny 🤭", "Bold 🔥")

    val suggestionsList = remember(currentGroup, selectedTone) {
        val g = currentGroup
        if (g == null) {
            emptyList()
        } else {
            when (selectedTone) {
                "Romantic 💘" -> g.romantic
                "Sweet 🥰" -> g.sweet
                "Funny 🤭" -> g.funny
                "Bold 🔥" -> g.bold
                else -> g.sweet
            }
        }
    }

    // Idle Fade animation
    val idleAlpha by animateFloatAsState(
        targetValue = if (isIdle && !isExpanded) 0.4f else 1f,
        animationSpec = spring(stiffness = Spring.StiffnessLow)
    )

    // Expand scaling animation
    val scaleFactor by animateFloatAsState(
        targetValue = if (isExpanded) 1f else 0f,
        animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy, stiffness = Spring.StiffnessMedium)
    )

    // Helper function to generate message group from local dataset
    fun refreshSuggestions() {
        if (incomingMessage.isBlank()) return
        isLoading = true
        scope.launch {
            try {
                val group = AiApiClient.generateMessageGroup(incomingMessage.trim())
                currentGroup = group
            } catch (e: Exception) {
                Log.e("CoupleFriendly", "Error loading suggestions", e)
            } finally {
                isLoading = false
            }
        }
    }

    // Automatically trigger idle state after 5s
    LaunchedEffect(isExpanded) {
        if (!isExpanded) {
            isIdle = false
            kotlinx.coroutines.delay(5000)
            isIdle = true
        }
    }

    Box(
        modifier = Modifier
            .alpha(idleAlpha)
            .pointerInput(Unit) {
                detectDragGestures(
                    onDragStart = { isIdle = false },
                    onDragEnd = { isIdle = true },
                    onDrag = { change, dragAmount ->
                        change.consume()
                        onDrag(dragAmount.x, dragAmount.y)
                    }
                )
            },
        contentAlignment = Alignment.Center
    ) {
        if (!isExpanded) {
            // Tiny Floating Icon: Glowing Cyber-Romance Magic Wand
            Box(
                modifier = Modifier
                    .size(56.dp)
                    .clip(CircleShape)
                    .background(
                        Brush.linearGradient(
                            colors = listOf(Color(0xFFFF2E93), Color(0xFF8A2BE2))
                        )
                    )
                    .clickable { isExpanded = true },
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "✨",
                    fontSize = 24.sp,
                    color = Color.White
                )
            }
        } else {
            // Expanded Premium Glassmorphic Card
            Card(
                modifier = Modifier
                    .width(290.dp)
                    .scale(scaleFactor)
                    .padding(8.dp),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFF1A0F26) // Surface Dark
                ),
                elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "✨ Couple Friendly",
                            fontSize = 18.sp,
                            color = Color.White
                        )
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(12.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            // Minimize button (green-marked concept: collapses card to floating icon)
                            Text(
                                text = "―", // Dash symbol
                                fontSize = 18.sp,
                                fontWeight = androidx.compose.ui.text.font.FontWeight.Bold,
                                color = Color(0xFFA594B8),
                                modifier = Modifier
                                    .clickable { isExpanded = false }
                                    .padding(4.dp)
                            )
                            // Close button (blue-marked concept: completely closes overlay)
                            Text(
                                text = "✕", // Cross symbol
                                fontSize = 18.sp,
                                fontWeight = androidx.compose.ui.text.font.FontWeight.Bold,
                                color = Color(0xFFA594B8),
                                modifier = Modifier
                                    .clickable { onCloseOverlay() }
                                    .padding(4.dp)
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    // Message input field
                    OutlinedTextField(
                        value = incomingMessage,
                        onValueChange = { incomingMessage = it },
                        placeholder = { Text("What did they say?", fontSize = 12.sp, color = Color(0xFF7A6890)) },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = false,
                        maxLines = 3,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Color(0xFFFF2E93),
                            unfocusedBorderColor = Color(0xFF4A3060),
                            focusedTextColor = Color.White,
                            unfocusedTextColor = Color.White,
                            cursorColor = Color(0xFFFF2E93)
                        ),
                        textStyle = androidx.compose.ui.text.TextStyle(fontSize = 13.sp)
                    )

                    Spacer(modifier = Modifier.height(8.dp))

                    if (isLoading) {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(80.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            CircularProgressIndicator(
                                color = Color(0xFFFF2E93)
                            )
                        }
                    } else {
                        Column {
                            if (currentGroup != null && suggestionsList.isNotEmpty()) {
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(bottom = 6.dp),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text(
                                        text = "💬 Reply suggestions",
                                        fontSize = 11.sp,
                                        fontWeight = androidx.compose.ui.text.font.FontWeight.SemiBold,
                                        color = Color(0xFFFF70A6)
                                    )
                                    Text(
                                        text = "Tap to copy",
                                        fontSize = 10.sp,
                                        color = Color(0xFFA594B8)
                                    )
                                }
                            }

                            suggestionsList.forEachIndexed { index, reply ->
                                Box(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(vertical = 4.dp)
                                        .clip(RoundedCornerShape(8.dp))
                                        .background(Color(0xFF2E1A47)) // Premium Purple tint
                                        .clickable {
                                            onReplySelected(reply)
                                        }
                                        .padding(12.dp)
                                ) {
                                    Row(verticalAlignment = Alignment.Top) {
                                        Text(
                                            text = "${index + 1}. ",
                                            color = Color(0xFFFF70A6),
                                            fontSize = 13.sp,
                                            fontWeight = androidx.compose.ui.text.font.FontWeight.Bold
                                        )
                                        Text(
                                            text = reply,
                                            color = Color.White,
                                            fontSize = 13.sp
                                        )
                                    }
                                }
                            }
                        }
                    }
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    // Tone Switcher & Refresh buttons
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        // Horizontal Toggle between tones (Instantaneous)
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(6.dp))
                                .background(Color(0xFF0D0614))
                                .clickable {
                                    val nextIndex = (tones.indexOf(selectedTone) + 1) % tones.size
                                    selectedTone = tones[nextIndex]
                                }
                                .padding(horizontal = 8.dp, vertical = 6.dp)
                        ) {
                            Text(
                                text = selectedTone,
                                fontSize = 11.sp,
                                color = Color(0xFFFF2E93)
                            )
                        }
                        
                        Text(
                            text = "Refresh 🔄",
                            fontSize = 11.sp,
                            color = Color(0xFF00F5D4),
                            modifier = Modifier.clickable {
                                refreshSuggestions()
                            }
                        )
                    }
                }
            }
        }
    }
}

// Temporary Fallback Theme just in case com.couplefriendly.app.ui.theme isn't configured
@Composable
fun CouplefriendlyTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = darkColorScheme(
            background = Color(0xFF0D0614),
            surface = Color(0xFF1A0F26),
            primary = Color(0xFFFF2E93),
            secondary = Color(0xFF8A2BE2)
        ),
        content = content
    )
}

@Preview(showBackground = true, backgroundColor = 0x00000000)
@Composable
fun FloatingOverlayCollapsedPreview() {
    CouplefriendlyTheme {
        Box(
            modifier = Modifier.padding(16.dp),
            contentAlignment = Alignment.Center
        ) {
            Box(
                modifier = Modifier
                    .size(56.dp)
                    .clip(CircleShape)
                    .background(
                        Brush.linearGradient(
                            colors = listOf(Color(0xFFFF2E93), Color(0xFF8A2BE2))
                        )
                    ),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "✨",
                    fontSize = 24.sp,
                    color = Color.White
                )
            }
        }
    }
}

@Preview(showBackground = true, backgroundColor = 0xFF0D0614)
@Composable
fun FloatingOverlayExpandedPreview() {
    CouplefriendlyTheme {
        Card(
            modifier = Modifier
                .width(290.dp)
                .padding(8.dp),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(
                containerColor = Color(0xFF1A0F26)
            ),
            elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "✨ Couple Friendly",
                        fontSize = 18.sp,
                        color = Color.White
                    )
                    Text(
                        text = "✕",
                        fontSize = 16.sp,
                        color = Color(0xFFA594B8)
                    )
                }

                Spacer(modifier = Modifier.height(12.dp))

                Column {
                    Text(
                        text = "Suggestions for latest message:",
                        fontSize = 11.sp,
                        color = Color(0xFFA594B8),
                        modifier = Modifier.padding(bottom = 6.dp)
                    )

                    listOf(
                        "Hii baby, chala gurthu vasthunnav ninnati nundi! 💕",
                        "Ne hi tho na gunde gatiga kottukuntundhi baby! 💕",
                        "Hi antu distance maintain cheyyaku bangaram! 🤭"
                    ).forEach { reply ->
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 4.dp)
                                .clip(RoundedCornerShape(8.dp))
                                .background(Color(0xFF2E1A47))
                                .padding(12.dp)
                        ) {
                            Text(
                                text = reply,
                                color = Color.White,
                                fontSize = 13.sp
                            )
                        }
                    }
                }
                
                Spacer(modifier = Modifier.height(12.dp))
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(6.dp))
                            .background(Color(0xFF0D0614))
                            .padding(horizontal = 8.dp, vertical = 6.dp)
                    ) {
                        Text(
                            text = "Romantic 💘",
                            fontSize = 11.sp,
                            color = Color(0xFFFF2E93)
                        )
                    }
                    
                    Text(
                        text = "Refresh 🔄",
                        fontSize = 11.sp,
                        color = Color(0xFF00F5D4)
                    )
                }
            }
        }
    }
}

