# 🏗 Negotiation Dojo - Architecture Documentation

This document provides an in-depth look at the architecture, design patterns, and implementation details of the Negotiation Dojo app.

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Layer Breakdown](#layer-breakdown)
3. [Data Flow](#data-flow)
4. [Key Components](#key-components)
5. [Design Patterns](#design-patterns)
6. [API Integration](#api-integration)
7. [Performance Considerations](#performance-considerations)
8. [Error Handling](#error-handling)

---

## High-Level Architecture

Negotiation Dojo follows a clean **MVVM (Model-View-ViewModel)** architecture with additional service layers:

```
┌─────────────────────────────────────────────────────────┐
│                     Presentation Layer                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │Dashboard │  │ Dialog   │  │Resistance│  │Coaching │ │
│  │   View   │  │   View   │  │   Bar    │  │Tip View │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                   ViewModel Layer                        │
│               ┌─────────────────────┐                    │
│               │ NegotiationEngine   │                    │
│               │  (Business Logic)   │                    │
│               └─────────────────────┘                    │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                    Service Layer                         │
│  ┌──────────────┐            ┌──────────────┐          │
│  │AudioRecorder │            │OpenAIService │          │
│  │ (AVFoundation)│            │  (Networking)│          │
│  └──────────────┘            └──────────────┘          │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                     Model Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Scenario │  │ Message  │  │AIResponse│             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
```

## Layer Breakdown

### 1. Model Layer (`Models/`)

**Purpose**: Define data structures and business entities

**Files**:
- `Models.swift`

**Key Types**:

#### Scenario
```swift
struct Scenario: Identifiable, Codable {
    let id: UUID
    let title: String
    let opponentName: String
    let opponentEmoji: String
    let initialResistance: Int
    let systemPrompt: String
}
```

Represents a negotiation scenario with:
- Metadata (title, description)
- Opponent configuration (name, emoji, persona)
- AI behavior (system prompt template)
- Initial state (resistance level)

#### Message
```swift
struct Message: Identifiable, Codable {
    let id: UUID
    let content: String
    let isUser: Bool
    let timestamp: Date
}
```

Represents a single message in the conversation history.

#### AIResponse
```swift
struct AIResponse: Codable {
    let reply: String
    let resistance_score: Int
    let coach_tip: String
}
```

Parsed from GPT-4o JSON response, containing:
- AI's spoken reply
- New resistance level
- Coaching feedback

### 2. Service Layer (`Services/`)

**Purpose**: Handle external integrations and system services

#### AudioRecorder (`AudioRecorder.swift`)

**Responsibilities**:
- Manage audio recording permissions
- Record user voice to .m4a files
- Monitor audio input levels
- Play AI-generated speech
- Clean up temporary audio files

**Key Properties**:
```swift
@Published var isRecording: Bool
@Published var isPlaying: Bool
@Published var recordingLevel: Float
@Published var errorMessage: String?
```

**Key Methods**:
```swift
func setupAudioSession() async throws
func startRecording() async throws
func stopRecording()
func playAudio(from url: URL) async throws
func getRecordingURL() -> URL?
```

**Implementation Details**:
- Uses `AVAudioRecorder` for recording
- Uses `AVAudioPlayer` for playback
- Implements `AVAudioRecorderDelegate` and `AVAudioPlayerDelegate`
- Audio settings: MPEG4AAC, 44.1kHz, mono, high quality
- Real-time level monitoring with 50ms updates

#### OpenAIService (`OpenAIService.swift`)

**Responsibilities**:
- Communicate with OpenAI APIs
- Handle authentication
- Process API responses
- Manage rate limiting and errors

**API Endpoints**:
1. **Whisper (STT)**: `https://api.openai.com/v1/audio/transcriptions`
2. **GPT-4o (Chat)**: `https://api.openai.com/v1/chat/completions`
3. **TTS (Speech)**: `https://api.openai.com/v1/audio/speech`

**Key Methods**:
```swift
func transcribeAudio(fileURL: URL) async throws -> String
func sendMessage(systemPrompt: String, userMessage: String, currentResistance: Int) async throws -> AIResponse
func synthesizeSpeech(text: String) async throws -> Data
```

**Configuration**:
```swift
private let whisperModel = "whisper-1"
private let chatModel = "gpt-4o"
private let ttsModel = "tts-1"
private let ttsVoice = "alloy"
```

### 3. ViewModel Layer (`ViewModels/`)

#### NegotiationEngine (`NegotiationEngine.swift`)

**Responsibilities**:
- Orchestrate the entire negotiation flow
- Manage conversation state
- Coordinate between services
- Update resistance levels
- Generate coaching tips
- Detect victory conditions

**Key Properties**:
```swift
@Published var scenario: Scenario
@Published var messages: [Message]
@Published var currentResistance: Int
@Published var isProcessing: Bool
@Published var latestCoachingTip: CoachingTip?
```

**Core Flow** (`processUserSpeech`):
```swift
1. Get audio recording URL
2. Transcribe with Whisper → String
3. Send to GPT-4o → AIResponse
4. Update resistance level
5. Add messages to chat history
6. Show coaching tip (auto-dismiss after 8s)
7. Synthesize reply with TTS
8. Play audio response
9. Check for victory (resistance = 0)
```

**State Management**:
- Uses `@MainActor` for thread-safe UI updates
- Manages audio recorder and OpenAI service instances
- Handles cleanup on deinit

### 4. Presentation Layer (`Views/`)

#### DashboardView (`DashboardView.swift`)

**Purpose**: Scenario selection screen

**Features**:
- Grid layout of scenario cards
- Hover effects with scaling
- Gradient background
- Difficulty indicators

**Key Components**:
```swift
ScenarioCard: View {
    - Emoji avatar
    - Title and opponent name
    - Description
    - Difficulty dots (1-3)
    - "Begin Training" button
    - Hover animations
}
```

#### DialogView (`DialogView.swift`)

**Purpose**: Main negotiation interface

**Layout**:
```
┌─────────────────────────────────────────────────────┐
│  [Back]        Scenario Title           [Reset]     │
├───────┬─────────────────────────────────┬───────────┤
│       │                                 │           │
│Resist │        Chat Log                 │ Recording │
│ ance  │  ┌──────────────────────────┐   │ Controls  │
│ Bar   │  │ User: "I deserve..."     │   │           │
│       │  └──────────────────────────┘   │ ┌───────┐ │
│       │  ┌──────────────────────────┐   │ │  MIC  │ │
│       │  │ Boss: "Why should I..."  │   │ └───────┘ │
│       │  └──────────────────────────┘   │           │
│       │                                 │  [SPACE]  │
├───────┴─────────────────────────────────┴───────────┤
│  💡 Coach Tip: Use specific numbers...              │
└─────────────────────────────────────────────────────┘
```

**Components**:
- Top bar (navigation and reset)
- Left panel (ResistanceBar)
- Center (chat ScrollView with MessageBubbles)
- Right panel (recording controls)
- Bottom (coaching tips, conditional)

**Interactions**:
- Push-to-talk button (mouse drag gesture)
- Spacebar shortcut (future enhancement)
- Auto-scroll to latest message
- Loading overlay during processing

#### ResistanceBar (`ResistanceBar.swift`)

**Purpose**: Visual resistance meter

**Features**:
- Emoji avatar (60pt)
- "RESISTANCE" label
- Animated progress bar (0-100%)
- Color-coded (red > orange > green)
- Status text ("Highly resistant" → "CONVINCED!")
- Spring animations on value change

**Implementation**:
```swift
@State private var animatedResistance: Double = 100

// Smooth transitions
.onChange(of: resistance) { _, newValue in
    animatedResistance = Double(newValue)
}
.animation(.spring(response: 0.6, dampingFraction: 0.7), value: animatedResistance)
```

#### CoachingTipView (`CoachingTipView.swift`)

**Purpose**: Live coaching feedback display

**Features**:
- Brain icon indicator
- "Coach's Insight" label
- Tip content (max 15 words)
- Purple gradient background
- Yellow border accent
- Slide-in animation
- Auto-dismiss after 8s

**Animation**:
```swift
.scaleEffect(isVisible ? 1.0 : 0.8)
.opacity(isVisible ? 1.0 : 0.0)
.offset(y: isVisible ? 0 : 20)
.animation(.spring(response: 0.5, dampingFraction: 0.7), value: isVisible)
```

## Data Flow

### Complete User Journey

```
1. User launches app
   ↓
2. DashboardView displays scenarios
   ↓
3. User selects scenario
   ↓
4. DialogView initializes with NegotiationEngine
   ↓
5. Engine adds initial greeting to messages
   ↓
6. UI displays chat log with greeting
   ↓
7. User presses and holds record button
   ↓
8. AudioRecorder.startRecording() called
   ↓
9. User speaks into microphone
   ↓
10. Audio levels update in real-time
    ↓
11. User releases button
    ↓
12. AudioRecorder.stopRecording() called
    ↓
13. Engine.processUserSpeech() triggered
    ↓
14. Loading overlay appears
    ↓
15. OpenAIService.transcribeAudio() → Whisper API
    ↓
16. Transcription added to messages as user message
    ↓
17. OpenAIService.sendMessage() → GPT-4o API
    ↓
18. GPT-4o returns JSON with reply, resistance, tip
    ↓
19. Engine updates resistance value
    ↓
20. ResistanceBar animates to new value
    ↓
21. AI reply added to messages
    ↓
22. Coaching tip displayed (if not empty)
    ↓
23. OpenAIService.synthesizeSpeech() → TTS API
    ↓
24. TTS returns MP3 audio data
    ↓
25. Audio saved to temp file
    ↓
26. AudioRecorder.playAudio() plays response
    ↓
27. Loading overlay dismissed
    ↓
28. UI updates: chat scrolls, tip shows, resistance bar
    ↓
29. If resistance = 0 → Victory message
    ↓
30. User can continue or reset
```

### Error Flow

```
Any step fails
   ↓
Error thrown
   ↓
Caught in Engine.processUserSpeech()
   ↓
errorMessage property updated
   ↓
Error alert displayed in UI
   ↓
isProcessing = false
   ↓
User can retry
```

## Design Patterns

### 1. MVVM (Model-View-ViewModel)

**Models**: Pure data structures (Scenario, Message, AIResponse)

**Views**: SwiftUI views that observe ViewModels
- Read-only access to ViewModel properties
- Trigger ViewModel methods on user actions

**ViewModels**: Business logic and state management
- NegotiationEngine as the main ViewModel
- Uses `@Published` for reactive updates
- Marked `@MainActor` for UI thread safety

### 2. Dependency Injection

```swift
class NegotiationEngine {
    init(
        scenario: Scenario,
        audioRecorder: AudioRecorder = AudioRecorder(),
        openAIService: OpenAIService = OpenAIService()
    ) {
        // Dependencies injected, allowing for testing
    }
}
```

Benefits:
- Easier unit testing (can inject mocks)
- Flexible configuration
- Clear dependencies

### 3. Repository Pattern

OpenAIService acts as a repository:
- Abstracts API details from ViewModels
- Provides clean interface for data operations
- Handles serialization/deserialization

### 4. Observer Pattern

SwiftUI's Combine framework:
```swift
@Published var currentResistance: Int
// Views automatically update when this changes
```

### 5. Strategy Pattern

System prompts as strategies:
- Different scenarios use different prompts
- AI behavior changes based on prompt
- Easy to add new strategies

## API Integration

### Authentication

```swift
private let apiKey: String = ProcessInfo.processInfo.environment["OPENAI_API_KEY"] ?? ""

var request = URLRequest(url: endpoint)
request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
```

### Whisper API (Speech-to-Text)

**Request**:
```
POST https://api.openai.com/v1/audio/transcriptions
Content-Type: multipart/form-data

{
  file: <audio.m4a>,
  model: "whisper-1",
  language: "en"
}
```

**Response**:
```json
{
  "text": "I believe I deserve a raise because..."
}
```

**Processing Time**: ~500-1500ms

### GPT-4o API (Chat Completion)

**Request**:
```json
POST https://api.openai.com/v1/chat/completions

{
  "model": "gpt-4o",
  "messages": [
    {
      "role": "system",
      "content": "You are a negotiation simulator..."
    },
    {
      "role": "user",
      "content": "I believe I deserve a raise because..."
    }
  ],
  "temperature": 0.8,
  "max_tokens": 500,
  "response_format": { "type": "json_object" }
}
```

**Response**:
```json
{
  "choices": [
    {
      "message": {
        "content": "{\"reply\":\"Why should I give you more money?\",\"resistance_score\":75,\"coach_tip\":\"Good start, but use specific numbers\"}"
      }
    }
  ]
}
```

**Processing Time**: ~1000-2500ms

### TTS API (Text-to-Speech)

**Request**:
```json
POST https://api.openai.com/v1/audio/speech

{
  "model": "tts-1",
  "input": "Why should I give you more money?",
  "voice": "alloy",
  "response_format": "mp3"
}
```

**Response**: Binary MP3 audio data

**Processing Time**: ~500-1500ms

### Total Latency Breakdown

```
User speaks (2-5s user action)
↓
Whisper: ~1s
↓
GPT-4o: ~2s
↓
TTS: ~1s
↓
Total: ~4s + user speaking time
```

Target: < 5 seconds from button release to AI voice starts

## Performance Considerations

### 1. Async/Await

All API calls use Swift concurrency:
```swift
func processUserSpeech() async {
    let transcription = try await openAIService.transcribeAudio(fileURL: audioURL)
    let aiResponse = try await openAIService.sendMessage(...)
    let audioData = try await openAIService.synthesizeSpeech(text: aiResponse.reply)
}
```

Benefits:
- Non-blocking UI
- Clear error handling
- Sequential when needed, concurrent when possible

### 2. @MainActor

ViewModels and Views use `@MainActor`:
```swift
@MainActor
class NegotiationEngine: ObservableObject {
    // All UI updates happen on main thread
}
```

### 3. Lazy Loading

```swift
LazyVStack {
    ForEach(messages) { message in
        MessageBubble(message: message)
    }
}
```

Only renders visible messages.

### 4. Memory Management

- Temporary audio files cleaned up on:
  - App termination
  - Scenario reset
  - Engine deinit
- Audio recorder reuses single AVAudioRecorder instance

### 5. Caching

Future enhancement: Cache TTS responses for repeated phrases.

## Error Handling

### Error Types

#### AudioRecorderError
```swift
enum AudioRecorderError: LocalizedError {
    case permissionDenied
    case invalidURL
    case recordingFailed
    case playbackFailed
}
```

#### OpenAIError
```swift
enum OpenAIError: LocalizedError {
    case missingAPIKey
    case invalidResponse
    case emptyResponse
    case invalidJSON
    case apiError(statusCode: Int, message: String)
}
```

### Error Propagation

```swift
do {
    try await processUserSpeech()
} catch {
    errorMessage = error.localizedDescription
    // UI displays error to user
}
```

### User-Facing Errors

All errors show human-readable messages:
- "Microphone permission denied. Please enable..."
- "OpenAI API key is missing. Please set..."
- "API Error (429): Rate limit exceeded"

### Retry Logic

Currently manual (user can try again).

Future enhancement: Automatic retry with exponential backoff for network errors.

## Security & Privacy

### Sandboxing

App runs in macOS sandbox with limited permissions:
```xml
<key>com.apple.security.app-sandbox</key>
<true/>
<key>com.apple.security.device.audio-input</key>
<true/>
<key>com.apple.security.network.client</key>
<true/>
```

### API Key Storage

Current: Environment variable (development)

Recommended for production:
```swift
import Security

func storeAPIKey(key: String) {
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: "OpenAI-API-Key",
        kSecValueData as String: key.data(using: .utf8)!
    ]
    SecItemAdd(query as CFDictionary, nil)
}
```

### Data Transmission

- All API calls over HTTPS
- No audio or conversation data stored locally beyond session
- Temporary files deleted after use

---

## Future Architecture Improvements

### 1. Offline Mode
- Local Whisper model (whisper.cpp)
- Local LLM (llama.cpp)
- Fallback to cloud when available

### 2. Caching Layer
```swift
protocol CacheService {
    func cache(key: String, value: Data, ttl: TimeInterval)
    func fetch(key: String) -> Data?
}
```

### 3. Analytics Layer
```swift
protocol AnalyticsService {
    func trackEvent(_ name: String, properties: [String: Any])
    func trackSessionEnd(duration: TimeInterval, resistance: Int)
}
```

### 4. Persistence Layer
```swift
protocol PersistenceService {
    func saveSession(_ session: NegotiationSession)
    func fetchHistory() -> [NegotiationSession]
}
```

### 5. Testing Architecture

Current: Manual testing

Needed:
- Unit tests for Models
- Unit tests for Services (with mocked API)
- Unit tests for ViewModels
- UI tests for critical flows

Example:
```swift
class NegotiationEngineTests: XCTestCase {
    func testResistanceDecreases() async {
        let mockOpenAI = MockOpenAIService()
        mockOpenAI.nextResponse = AIResponse(
            reply: "Hmm, interesting...",
            resistance_score: 60,
            coach_tip: "Good point"
        )

        let engine = NegotiationEngine(
            scenario: .scenarios[0],
            audioRecorder: MockAudioRecorder(),
            openAIService: mockOpenAI
        )

        await engine.processUserSpeech()

        XCTAssertEqual(engine.currentResistance, 60)
        XCTAssertEqual(engine.messages.count, 3) // greeting + user + AI
    }
}
```

---

**This architecture enables:**
- ✅ Clear separation of concerns
- ✅ Testable components
- ✅ Easy feature additions
- ✅ Maintainable codebase
- ✅ Scalable design
