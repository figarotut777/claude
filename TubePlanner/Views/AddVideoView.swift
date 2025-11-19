//
//  AddVideoView.swift
//  TubePlanner
//
//  Created on 19.11.2025
//  Sheet for adding new YouTube video projects
//

import SwiftUI
import SwiftData

struct AddVideoView: View {
    // MARK: - Environment

    @Environment(\.modelContext) private var modelContext
    @Environment(\.dismiss) private var dismiss

    // MARK: - Properties

    @Binding var isPresented: Bool

    // MARK: - State

    @State private var youtubeUrl = ""
    @State private var isProcessing = false
    @State private var errorMessage: String?
    @State private var showingError = false

    // MARK: - Focus State

    @FocusState private var isURLFieldFocused: Bool

    // MARK: - Body

    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                // MARK: Header
                headerView

                // MARK: URL Input
                urlInputSection

                // MARK: Instructions
                instructionsSection

                Spacer()

                // MARK: Action Buttons
                actionButtonsSection
            }
            .padding()
            .frame(width: 500, height: 400)
            .navigationTitle("New Video Project")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
            }
            .alert("Error", isPresented: $showingError) {
                Button("OK", role: .cancel) { }
            } message: {
                Text(errorMessage ?? "An unknown error occurred")
            }
        }
        .onAppear {
            isURLFieldFocused = true
        }
    }

    // MARK: - Subviews

    private var headerView: some View {
        VStack(spacing: 8) {
            Image(systemName: "video.badge.plus")
                .font(.system(size: 48))
                .foregroundStyle(.blue.gradient)

            Text("Add YouTube Video")
                .font(.title2)
                .fontWeight(.semibold)

            Text("Paste a YouTube URL to generate an action plan")
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
        }
    }

    private var urlInputSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("YouTube URL")
                .font(.headline)

            TextField("https://www.youtube.com/watch?v=...", text: $youtubeUrl)
                .textFieldStyle(.roundedBorder)
                .focused($isURLFieldFocused)
                .onSubmit {
                    processVideo()
                }

            HStack(spacing: 4) {
                Image(systemName: "info.circle")
                    .font(.caption)
                Text("Supports youtube.com and youtu.be links")
                    .font(.caption)
            }
            .foregroundStyle(.secondary)
        }
    }

    private var instructionsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("How it works:")
                .font(.headline)

            VStack(alignment: .leading, spacing: 8) {
                InstructionRow(
                    number: 1,
                    icon: "link",
                    text: "Paste your YouTube video URL"
                )

                InstructionRow(
                    number: 2,
                    icon: "text.quote",
                    text: "We extract the video transcript"
                )

                InstructionRow(
                    number: 3,
                    icon: "cpu",
                    text: "AI analyzes and creates action plan"
                )

                InstructionRow(
                    number: 4,
                    icon: "checkmark.circle",
                    text: "Track your progress as you complete tasks"
                )
            }
        }
        .padding()
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
    }

    private var actionButtonsSection: some View {
        HStack {
            Button("Cancel") {
                dismiss()
            }
            .keyboardShortcut(.escape)

            Spacer()

            Button {
                processVideo()
            } label: {
                HStack {
                    if isProcessing {
                        ProgressView()
                            .scaleEffect(0.7)
                            .frame(width: 16, height: 16)
                    } else {
                        Image(systemName: "sparkles")
                    }
                    Text(isProcessing ? "Processing..." : "Generate Action Plan")
                }
            }
            .buttonStyle(.borderedProminent)
            .disabled(youtubeUrl.isEmpty || isProcessing)
            .keyboardShortcut(.return, modifiers: .command)
        }
    }

    // MARK: - Actions

    private func processVideo() {
        guard !youtubeUrl.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            showError("Please enter a YouTube URL")
            return
        }

        guard let videoId = extractVideoId(from: youtubeUrl) else {
            showError("Invalid YouTube URL. Please check and try again.")
            return
        }

        isProcessing = true

        // MARK: Phase 1 MVP - Create mock project
        // In Phase 2-3, this will be replaced with actual API calls

        Task { @MainActor in
            do {
                // Simulate network delay
                try await Task.sleep(for: .seconds(1.5))

                // Create a new project with mock data
                let newProject = VideoProject(
                    title: "Untitled Video", // Will be fetched in Phase 3
                    youtubeUrl: youtubeUrl,
                    videoId: videoId
                )

                // Add mock tasks (will be replaced by AI-generated tasks in Phase 2)
                newProject.tasks = [
                    TaskItem(
                        title: "Task 1: Getting started",
                        details: "This is a placeholder task. Real tasks will be generated by AI.",
                        orderIndex: 0,
                        project: newProject
                    ),
                    TaskItem(
                        title: "Task 2: Main content",
                        details: "Another placeholder task.",
                        orderIndex: 1,
                        project: newProject
                    ),
                    TaskItem(
                        title: "Task 3: Conclusion",
                        orderIndex: 2,
                        project: newProject
                    )
                ]

                modelContext.insert(newProject)
                try modelContext.save()

                isProcessing = false
                dismiss()
            } catch {
                isProcessing = false
                showError("Failed to create project: \(error.localizedDescription)")
            }
        }
    }

    private func extractVideoId(from url: String) -> String? {
        let trimmedUrl = url.trimmingCharacters(in: .whitespacesAndNewlines)

        // Pattern 1: youtube.com/watch?v=VIDEO_ID
        if let range = trimmedUrl.range(of: #"(?:youtube\.com/watch\?v=)([a-zA-Z0-9_-]+)"#, options: .regularExpression) {
            let match = trimmedUrl[range]
            return String(match.split(separator: "=").last ?? "")
        }

        // Pattern 2: youtu.be/VIDEO_ID
        if let range = trimmedUrl.range(of: #"(?:youtu\.be/)([a-zA-Z0-9_-]+)"#, options: .regularExpression) {
            let match = trimmedUrl[range]
            return String(match.split(separator: "/").last ?? "")
        }

        // Pattern 3: youtube.com/embed/VIDEO_ID
        if let range = trimmedUrl.range(of: #"(?:youtube\.com/embed/)([a-zA-Z0-9_-]+)"#, options: .regularExpression) {
            let match = trimmedUrl[range]
            return String(match.split(separator: "/").last ?? "")
        }

        return nil
    }

    private func showError(_ message: String) {
        errorMessage = message
        showingError = true
    }
}

// MARK: - Instruction Row

struct InstructionRow: View {
    let number: Int
    let icon: String
    let text: String

    var body: some View {
        HStack(spacing: 12) {
            ZStack {
                Circle()
                    .fill(.blue.gradient)
                    .frame(width: 24, height: 24)

                Text("\(number)")
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundStyle(.white)
            }

            Image(systemName: icon)
                .foregroundStyle(.blue)

            Text(text)
                .font(.subheadline)

            Spacer()
        }
    }
}

// MARK: - Preview

#Preview("Add Video View") {
    AddVideoView(isPresented: .constant(true))
        .modelContainer(for: [VideoProject.self, TaskItem.self], inMemory: true)
}
