//
//  NegotiationEngine.swift
//  NegotiationDojo
//
//  Phase 2: The Brain - Main negotiation logic orchestrator
//  Created by Claude on 2025-11-19.
//

import Foundation
import Combine

@MainActor
class NegotiationEngine: ObservableObject {
    // MARK: - Published Properties
    @Published var scenario: Scenario
    @Published var messages: [Message] = []
    @Published var currentResistance: Int
    @Published var isProcessing = false
    @Published var errorMessage: String?
    @Published var latestCoachingTip: CoachingTip?

    // MARK: - Services
    private let audioRecorder: AudioRecorder
    private let openAIService: OpenAIService

    // MARK: - State
    private var isVictorious = false

    // MARK: - Initialization
    init(scenario: Scenario, audioRecorder: AudioRecorder = AudioRecorder(), openAIService: OpenAIService = OpenAIService()) {
        self.scenario = scenario
        self.currentResistance = scenario.initialResistance
        self.audioRecorder = audioRecorder
        self.openAIService = openAIService

        // Add initial greeting from opponent
        addOpponentGreeting()
    }

    // MARK: - Initial Greeting
    private func addOpponentGreeting() {
        let greetings = [
            "👔": "Come in. This better be quick - I have a meeting in 10 minutes.",
            "🛍️": "*sighs* What can I help you with today?",
            "🛋️": "Yo, what's up? I was just about to start a new series..."
        ]

        let greeting = greetings[scenario.opponentEmoji] ?? "Hello. How can I help you?"
        let message = Message(content: greeting, isUser: false)
        messages.append(message)
    }

    // MARK: - Main Flow: Record -> Transcribe -> Process -> Respond
    func processUserSpeech() async {
        guard !isProcessing else { return }

        isProcessing = true
        errorMessage = nil

        do {
            // Step 1: Get recording URL
            guard let audioURL = audioRecorder.getRecordingURL() else {
                throw NegotiationError.noRecording
            }

            // Step 2: Transcribe with Whisper
            let transcription = try await openAIService.transcribeAudio(fileURL: audioURL)

            // Add user message to chat
            let userMessage = Message(content: transcription, isUser: true)
            messages.append(userMessage)

            // Step 3: Get AI response from GPT-4o
            let aiResponse = try await openAIService.sendMessage(
                systemPrompt: scenario.systemPrompt,
                userMessage: transcription,
                currentResistance: currentResistance
            )

            // Step 4: Update resistance
            updateResistance(to: aiResponse.resistance_score)

            // Step 5: Add opponent message to chat
            let opponentMessage = Message(content: aiResponse.reply, isUser: false)
            messages.append(opponentMessage)

            // Step 6: Show coaching tip
            if !aiResponse.coach_tip.isEmpty {
                latestCoachingTip = CoachingTip(content: aiResponse.coach_tip)

                // Auto-dismiss tip after 8 seconds
                Task {
                    try? await Task.sleep(nanoseconds: 8_000_000_000)
                    if latestCoachingTip?.id == latestCoachingTip?.id {
                        latestCoachingTip = nil
                    }
                }
            }

            // Step 7: Synthesize and play speech
            let audioData = try await openAIService.synthesizeSpeech(text: aiResponse.reply)
            let audioURL = try openAIService.saveAudioToFile(audioData)
            try await audioRecorder.playAudio(from: audioURL)

            // Step 8: Check for victory
            checkVictoryCondition()

        } catch {
            errorMessage = error.localizedDescription
            print("Error in processUserSpeech: \(error)")
        }

        isProcessing = false
    }

    // MARK: - Resistance Management
    private func updateResistance(to newValue: Int) {
        // Clamp between 0 and 100
        let clampedValue = max(0, min(100, newValue))
        currentResistance = clampedValue
    }

    // MARK: - Victory Check
    private func checkVictoryCondition() {
        if currentResistance <= 0 && !isVictorious {
            isVictorious = true

            // Add victory message
            let victoryMessages = [
                "👔": "Alright, fine. You've made a compelling case. Let's discuss the details.",
                "🛍️": "Okay okay, I'll process the return. Just this once!",
                "🛋️": "You know what? That actually sounds pretty fun. I'm in!"
            ]

            let victoryText = victoryMessages[scenario.opponentEmoji] ?? "You've convinced me!"
            let victoryMessage = Message(content: "🎉 VICTORY! \(victoryText)", isUser: false)
            messages.append(victoryMessage)
        }
    }

    // MARK: - Recording Controls
    func startRecording() async {
        do {
            try await audioRecorder.startRecording()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func stopRecording() {
        audioRecorder.stopRecording()
    }

    // MARK: - Computed Properties
    var isRecording: Bool {
        audioRecorder.isRecording
    }

    var recordingLevel: Float {
        audioRecorder.recordingLevel
    }

    var resistancePercentage: Double {
        Double(currentResistance) / 100.0
    }

    var resistanceColor: String {
        if currentResistance > 70 {
            return "red"
        } else if currentResistance > 30 {
            return "orange"
        } else {
            return "green"
        }
    }

    // MARK: - Reset
    func reset() {
        messages.removeAll()
        currentResistance = scenario.initialResistance
        isVictorious = false
        latestCoachingTip = nil
        addOpponentGreeting()
        audioRecorder.cleanup()
    }

    // MARK: - Cleanup
    deinit {
        audioRecorder.cleanup()
    }
}

// MARK: - Errors
enum NegotiationError: LocalizedError {
    case noRecording

    var errorDescription: String? {
        switch self {
        case .noRecording:
            return "No recording available. Please record your message first."
        }
    }
}
