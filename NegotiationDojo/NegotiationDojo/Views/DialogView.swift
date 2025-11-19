//
//  DialogView.swift
//  NegotiationDojo
//
//  Main dialog interface (The Ring)
//  Created by Claude on 2025-11-19.
//

import SwiftUI

struct DialogView: View {
    let scenario: Scenario
    @Binding var showDashboard: Bool

    @StateObject private var engine: NegotiationEngine
    @State private var isRecordingPressed = false

    init(scenario: Scenario, showDashboard: Binding<Bool>) {
        self.scenario = scenario
        self._showDashboard = showDashboard
        self._engine = StateObject(wrappedValue: NegotiationEngine(scenario: scenario))
    }

    var body: some View {
        ZStack {
            // Background
            LinearGradient(
                colors: [Color(red: 0.05, green: 0.05, blue: 0.15), Color(red: 0.15, green: 0.1, blue: 0.2)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            VStack(spacing: 0) {
                // Top Bar
                topBar

                HStack(spacing: 20) {
                    // Left Panel: Resistance Bar
                    VStack {
                        ResistanceBar(resistance: engine.currentResistance, emoji: scenario.opponentEmoji)
                        Spacer()
                    }
                    .frame(width: 250)
                    .padding(.leading, 20)

                    // Center: Chat Log
                    chatLog

                    // Right Panel: Controls
                    VStack {
                        recordingControls
                        Spacer()
                    }
                    .frame(width: 200)
                    .padding(.trailing, 20)
                }

                // Bottom: Coaching Tips
                if let tip = engine.latestCoachingTip {
                    CoachingTipView(tip: tip)
                        .padding(.bottom, 20)
                        .transition(.move(edge: .bottom).combined(with: .opacity))
                }
            }

            // Loading overlay
            if engine.isProcessing {
                loadingOverlay
            }

            // Error alert
            if let error = engine.errorMessage {
                errorAlert(error)
            }
        }
        .frame(minWidth: 1000, minHeight: 700)
    }

    // MARK: - Top Bar
    private var topBar: some View {
        HStack {
            Button(action: {
                withAnimation {
                    showDashboard = true
                }
            }) {
                HStack(spacing: 6) {
                    Image(systemName: "chevron.left")
                    Text("Back")
                }
                .foregroundColor(.white)
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(Color.white.opacity(0.15))
                .cornerRadius(8)
            }
            .buttonStyle(.plain)

            Spacer()

            VStack(spacing: 2) {
                Text(scenario.title)
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(.white)

                Text("Convince \(scenario.opponentName) to agree")
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.6))
            }

            Spacer()

            Button(action: {
                engine.reset()
            }) {
                HStack(spacing: 6) {
                    Image(systemName: "arrow.clockwise")
                    Text("Reset")
                }
                .foregroundColor(.white)
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(Color.white.opacity(0.15))
                .cornerRadius(8)
            }
            .buttonStyle(.plain)
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 16)
        .background(Color.black.opacity(0.3))
    }

    // MARK: - Chat Log
    private var chatLog: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(spacing: 12) {
                    ForEach(engine.messages) { message in
                        MessageBubble(message: message)
                            .id(message.id)
                    }
                }
                .padding(20)
            }
            .background(Color.black.opacity(0.2))
            .cornerRadius(12)
            .onChange(of: engine.messages.count) { _, _ in
                if let lastMessage = engine.messages.last {
                    withAnimation {
                        proxy.scrollTo(lastMessage.id, anchor: .bottom)
                    }
                }
            }
        }
    }

    // MARK: - Recording Controls
    private var recordingControls: some View {
        VStack(spacing: 20) {
            // Push-to-Talk Button
            VStack(spacing: 12) {
                Button(action: {}) {
                    ZStack {
                        Circle()
                            .fill(engine.isRecording ? Color.red : Color.blue)
                            .frame(width: 120, height: 120)
                            .scaleEffect(isRecordingPressed ? 0.9 : 1.0)
                            .shadow(color: engine.isRecording ? .red.opacity(0.5) : .blue.opacity(0.3), radius: engine.isRecording ? 20 : 10)

                        Image(systemName: "mic.fill")
                            .font(.system(size: 40))
                            .foregroundColor(.white)
                    }
                }
                .buttonStyle(.plain)
                .simultaneousGesture(
                    DragGesture(minimumDistance: 0)
                        .onChanged { _ in
                            if !isRecordingPressed && !engine.isProcessing {
                                isRecordingPressed = true
                                Task {
                                    await engine.startRecording()
                                }
                            }
                        }
                        .onEnded { _ in
                            if isRecordingPressed {
                                isRecordingPressed = false
                                engine.stopRecording()
                                Task {
                                    await engine.processUserSpeech()
                                }
                            }
                        }
                )
                .disabled(engine.isProcessing)

                Text(engine.isRecording ? "Release to send" : "Hold to speak")
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.7))
                    .fontWeight(.medium)
            }

            // Keyboard shortcut hint
            VStack(spacing: 4) {
                Text("or use")
                    .font(.caption2)
                    .foregroundColor(.white.opacity(0.5))

                HStack(spacing: 4) {
                    Text("SPACE")
                        .font(.caption2)
                        .fontWeight(.bold)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.white.opacity(0.2))
                        .cornerRadius(4)
                }
                .foregroundColor(.white.opacity(0.7))
            }

            // Audio level indicator
            if engine.isRecording {
                VStack(spacing: 8) {
                    Text("Recording...")
                        .font(.caption)
                        .foregroundColor(.red)

                    ProgressView(value: Double(engine.recordingLevel))
                        .progressViewStyle(LinearProgressViewStyle(tint: .red))
                        .frame(width: 150)
                }
                .transition(.opacity)
            }
        }
        .padding(20)
        .background(Color.black.opacity(0.3))
        .cornerRadius(12)
    }

    // MARK: - Loading Overlay
    private var loadingOverlay: some View {
        ZStack {
            Color.black.opacity(0.6)
                .ignoresSafeArea()

            VStack(spacing: 20) {
                ProgressView()
                    .scaleEffect(1.5)
                    .progressViewStyle(CircularProgressViewStyle(tint: .white))

                Text("AI is thinking...")
                    .font(.headline)
                    .foregroundColor(.white)
            }
            .padding(40)
            .background(Color.black.opacity(0.8))
            .cornerRadius(16)
        }
    }

    // MARK: - Error Alert
    private func errorAlert(_ error: String) -> some View {
        VStack {
            HStack {
                Image(systemName: "exclamationmark.triangle.fill")
                    .foregroundColor(.yellow)
                Text(error)
                    .foregroundColor(.white)
                    .font(.caption)
            }
            .padding()
            .background(Color.red.opacity(0.8))
            .cornerRadius(8)
            .padding()

            Spacer()
        }
    }
}

// MARK: - Message Bubble
struct MessageBubble: View {
    let message: Message

    var body: some View {
        HStack {
            if message.isUser {
                Spacer()
            }

            Text(message.content)
                .font(.body)
                .foregroundColor(.white)
                .padding(12)
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(message.isUser ? Color.blue.opacity(0.7) : Color.gray.opacity(0.5))
                )
                .frame(maxWidth: 500, alignment: message.isUser ? .trailing : .leading)

            if !message.isUser {
                Spacer()
            }
        }
    }
}

#Preview {
    DialogView(
        scenario: Scenario.scenarios[0],
        showDashboard: .constant(false)
    )
}
