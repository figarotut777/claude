# 🥋 Negotiation Dojo — AI Soft Skills Trainer

A native macOS application for training negotiation skills through voice-based AI interactions.

## 📋 Overview

Negotiation Dojo is an AI-powered training platform where users practice persuasion and negotiation skills by engaging in realistic voice conversations with AI opponents. The app simulates various challenging scenarios where users must convince skeptical AI characters to change their mind.

### Key Features

- **Voice-Based Interaction**: Speak naturally using push-to-talk or keyboard shortcuts
- **Real-Time AI Responses**: GPT-4o powered opponents with realistic personalities
- **Live Coaching**: Get instant feedback on your negotiation techniques
- **Resistance Meter**: Visual feedback showing opponent's willingness to agree
- **Multiple Scenarios**: Practice different negotiation contexts
- **Natural Voice Output**: AI responses spoken with OpenAI TTS

## 🎯 Concept

1. Select a negotiation scenario (e.g., "Ask for a Raise")
2. Face an AI opponent with high resistance (80-100%)
3. Use voice to make arguments and persuade them
4. Receive real-time coaching tips on your technique
5. Watch resistance decrease as your arguments improve
6. Win when resistance reaches 0%

## 🛠 Technical Stack

- **Language**: Swift 5.9+
- **UI Framework**: SwiftUI
- **Platform**: macOS 14.0+ (Sonoma)
- **Audio**: AVFoundation
- **AI Services**: OpenAI API
  - **STT**: Whisper API (Speech-to-Text)
  - **LLM**: GPT-4o (Dialog logic and coaching)
  - **TTS**: OpenAI TTS (Voice output)

## 📁 Project Structure

```
NegotiationDojo/
├── NegotiationDojo.xcodeproj/
│   └── project.pbxproj
└── NegotiationDojo/
    ├── NegotiationDojoApp.swift      # App entry point
    ├── ContentView.swift              # Root view controller
    ├── NegotiationDojo.entitlements   # Sandbox & permissions
    ├── Models/
    │   └── Models.swift               # Data models (Scenario, Message, AIResponse)
    ├── Services/
    │   ├── AudioRecorder.swift        # Voice recording with AVFoundation
    │   └── OpenAIService.swift        # API integration (Whisper, GPT-4o, TTS)
    ├── ViewModels/
    │   └── NegotiationEngine.swift    # Main business logic orchestrator
    ├── Views/
    │   ├── DashboardView.swift        # Scenario selection screen
    │   ├── DialogView.swift           # Main negotiation interface
    │   ├── ResistanceBar.swift        # Resistance meter component
    │   └── CoachingTipView.swift      # Live coaching tips display
    └── Assets.xcassets/               # Images and color assets
```

## 🚀 Getting Started

### Prerequisites

- macOS 14.0 (Sonoma) or later
- Xcode 15.0 or later
- OpenAI API key with access to:
  - Whisper API
  - GPT-4o
  - TTS API

### Installation

1. Clone the repository:
```bash
git clone https://github.com/figarotut777/claude.git
cd claude/NegotiationDojo
```

2. Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or add it to your `~/.zshrc` or `~/.bash_profile`:
```bash
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

3. Open the project in Xcode:
```bash
open NegotiationDojo.xcodeproj
```

4. Build and run (⌘R)

### Configuration

The app reads the API key from the `OPENAI_API_KEY` environment variable. For production use, consider storing it securely in the macOS Keychain.

## 🎮 How to Use

### Dashboard

1. Launch the app to see the scenario selection dashboard
2. Choose from three pre-configured scenarios:
   - **Ask for a Raise** - Convince a strict boss (Difficulty: Hard)
   - **Return Without Receipt** - Persuade a tired store clerk (Difficulty: Medium)
   - **Weekend Trip** - Convince a lazy friend (Difficulty: Easy)

### The Ring (Dialog Interface)

1. **Resistance Bar** (Left): Shows opponent's current resistance level
2. **Chat Log** (Center): Displays conversation history
3. **Recording Controls** (Right): Push-to-talk button and controls

### Controls

- **Push-to-Talk Button**: Click and hold to record, release to send
- **Spacebar**: Alternative keyboard shortcut for recording
- **Back Button**: Return to scenario selection
- **Reset Button**: Restart the current scenario

### Tips for Success

1. **Use Data**: Back up claims with specific numbers and facts
2. **Show Empathy**: Acknowledge the other person's position
3. **Stay Confident**: Speak clearly and assertively
4. **Build Arguments**: Layer multiple supporting points
5. **Watch Coaching Tips**: Learn from real-time AI feedback

## 🏗 Architecture

### Phase 1: Audio Foundation

**AudioRecorder** handles all voice recording functionality:
- Requests microphone permissions
- Records audio to temporary .m4a files
- Monitors audio levels during recording
- Plays back AI-generated speech

### Phase 2: The Brain (LLM Integration)

**OpenAIService** manages all API communications:
- Transcribes voice recordings via Whisper API
- Sends messages to GPT-4o with system prompts
- Parses JSON responses containing reply, resistance score, and coaching tips
- Synthesizes AI responses to speech via TTS

**NegotiationEngine** orchestrates the negotiation flow:
- Manages conversation state and message history
- Updates resistance levels based on AI responses
- Coordinates the full pipeline: Record → Transcribe → Process → Respond → Play
- Detects victory conditions

### Phase 3: Voice Output & UI

**SwiftUI Views** provide the user interface:
- **DashboardView**: Scenario cards with hover effects
- **DialogView**: Main negotiation interface with three-panel layout
- **ResistanceBar**: Animated progress bar with color-coded status
- **CoachingTipView**: Toast-style coaching feedback with animations

### Data Flow

```
User Speaks
    ↓
AudioRecorder captures audio
    ↓
OpenAI Whisper transcribes to text
    ↓
GPT-4o analyzes argument & generates response
    ↓
NegotiationEngine updates resistance & messages
    ↓
OpenAI TTS synthesizes AI reply
    ↓
AudioRecorder plays speech
    ↓
UI updates (chat, resistance bar, coaching tip)
```

## 🎨 UI/UX Features

### Animations

- Smooth resistance bar transitions with spring animations
- Coaching tip slide-in effects
- Button press feedback
- Message bubble transitions

### Visual Feedback

- Color-coded resistance levels (Red → Orange → Green)
- Audio level visualization during recording
- Loading overlay during AI processing
- Error alerts for API failures

### Accessibility

- Large, clear emoji avatars
- High-contrast text
- Keyboard shortcuts for core functions
- Visual and textual status indicators

## 🔧 Customization

### Adding New Scenarios

Edit `Models/Models.swift` and add to the `Scenario.scenarios` array:

```swift
Scenario(
    title: "Your Scenario Title",
    description: "Brief description",
    opponentName: "Opponent Name",
    opponentPersona: "Personality description",
    opponentEmoji: "🎭",
    initialResistance: 75,
    systemPrompt: """
    Your custom system prompt here...
    """
)
```

### Adjusting AI Behavior

Modify system prompts in `Models.swift` to change:
- Opponent personality traits
- Resistance change sensitivity
- Coaching tip focus areas
- Response style

### Changing Voice

Edit `OpenAIService.swift` and change `ttsVoice`:
- Options: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`

## 🐛 Troubleshooting

### Common Issues

1. **"Microphone permission denied"**
   - Go to System Settings → Privacy & Security → Microphone
   - Enable permission for NegotiationDojo

2. **"OpenAI API key is missing"**
   - Ensure `OPENAI_API_KEY` environment variable is set
   - Restart Xcode after setting the variable

3. **"Invalid response from OpenAI API"**
   - Check your API key validity
   - Verify you have access to GPT-4o
   - Check your OpenAI account credits

4. **High latency (>5 seconds)**
   - Check your internet connection
   - Consider using `tts-1-hd` for better quality but slower speed
   - OpenAI API response times vary by server load

### Debug Mode

Enable verbose logging by adding to `OpenAIService.swift`:

```swift
print("Whisper Response: \(whisperResponse)")
print("GPT Response: \(content)")
```

## 📊 Performance Targets

- **Response Latency**: 3-4 seconds (Whisper + GPT-4o + TTS)
- **UI Responsiveness**: 60 FPS animations
- **Audio Quality**: 44.1kHz recording, high-quality TTS

## 🔐 Security & Privacy

- **Sandbox**: App runs in macOS sandbox with limited permissions
- **Microphone Access**: Required for voice recording
- **Network Access**: Required for OpenAI API calls
- **Data Storage**: Audio files stored temporarily and cleaned up
- **API Key**: Never hardcoded; loaded from environment

## 🚦 Roadmap

### Completed ✅
- [x] Audio recording and playback
- [x] Whisper integration
- [x] GPT-4o integration
- [x] TTS integration
- [x] Dashboard UI
- [x] Dialog UI
- [x] Resistance tracking
- [x] Live coaching tips

### Future Enhancements 🎯
- [ ] Custom scenario creation by users
- [ ] Session history and analytics
- [ ] Progress tracking across scenarios
- [ ] Difficulty levels within scenarios
- [ ] Multi-language support
- [ ] Offline mode with local models
- [ ] Mobile (iOS) version
- [ ] Multiplayer practice mode

## 📄 License

This project is created for educational purposes. Use at your own discretion.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Contact

For questions and suggestions, please create an issue in the repository.

---

**Made with ❤️ using Swift, SwiftUI, and OpenAI APIs**
