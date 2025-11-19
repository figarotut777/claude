//
//  DetailView.swift
//  TubePlanner
//
//  Created on 19.11.2025
//  Detail view showing action plan checklist
//

import SwiftUI
import SwiftData

struct DetailView: View {
    // MARK: - Environment

    @Environment(\.modelContext) private var modelContext

    // MARK: - Properties

    @Bindable var project: VideoProject

    // MARK: - State

    @State private var showingExportAlert = false
    @State private var exportedText = ""

    // MARK: - Computed Properties

    private var sortedTasks: [TaskItem] {
        project.tasks.sorted { $0.orderIndex < $1.orderIndex }
    }

    // MARK: - Body

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // MARK: Header Section
                headerSection

                // MARK: Progress Section
                progressSection

                // MARK: Tasks List
                tasksSection

                Spacer()
            }
            .padding()
        }
        .navigationTitle(project.title)
        .toolbar {
            toolbarContent
        }
        .alert("Action Plan Exported", isPresented: $showingExportAlert) {
            Button("Copy to Clipboard") {
                NSPasteboard.general.clearContents()
                NSPasteboard.general.setString(exportedText, forType: .string)
            }
            Button("OK", role: .cancel) { }
        } message: {
            Text("The action plan has been prepared. Would you like to copy it to clipboard?")
        }
    }

    // MARK: - Subviews

    private var headerSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Video info
            HStack {
                Image(systemName: "play.rectangle.fill")
                    .font(.title2)
                    .foregroundStyle(.red.gradient)

                VStack(alignment: .leading, spacing: 2) {
                    Text(project.title)
                        .font(.title2)
                        .fontWeight(.bold)

                    Link(destination: URL(string: project.youtubeUrl)!) {
                        HStack(spacing: 4) {
                            Text("Watch on YouTube")
                            Image(systemName: "arrow.up.forward")
                        }
                        .font(.caption)
                    }
                }

                Spacer()
            }

            Divider()

            // Metadata
            HStack(spacing: 16) {
                Label("\(project.tasks.count) tasks", systemImage: "list.bullet")
                Label("Created \(project.createdAt.formatted(.relative(presentation: .named)))", systemImage: "calendar")
            }
            .font(.caption)
            .foregroundStyle(.secondary)
        }
        .padding()
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
    }

    private var progressSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text("Progress")
                    .font(.headline)

                Spacer()

                Text("\(project.completedTasksCount) of \(project.tasks.count)")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }

            ProgressView(value: project.progressPercentage, total: 100) {
                Text("\(Int(project.progressPercentage))% Complete")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            .tint(progressColor)
        }
        .padding()
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
    }

    private var tasksSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Action Plan")
                .font(.headline)

            if sortedTasks.isEmpty {
                emptyTasksView
            } else {
                ForEach(sortedTasks) { task in
                    TaskRowView(task: task)
                }
            }
        }
    }

    private var emptyTasksView: some View {
        ContentUnavailableView {
            Label("No Tasks Yet", systemImage: "list.bullet.clipboard")
        } description: {
            Text("Tasks will appear here after processing the video")
        }
        .frame(maxWidth: .infinity)
        .padding()
    }

    @ToolbarContentBuilder
    private var toolbarContent: some ToolbarContent {
        ToolbarItem(placement: .primaryAction) {
            Menu {
                Button {
                    exportToClipboard()
                } label: {
                    Label("Copy to Clipboard", systemImage: "doc.on.clipboard")
                }

                Button {
                    exportToNotes()
                } label: {
                    Label("Export to Notes", systemImage: "note.text")
                }

                Divider()

                Button {
                    openInYouTube()
                } label: {
                    Label("Open in YouTube", systemImage: "play.rectangle")
                }
            } label: {
                Label("Export", systemImage: "square.and.arrow.up")
            }
        }
    }

    // MARK: - Computed Colors

    private var progressColor: Color {
        switch project.progressPercentage {
        case 0..<25:
            return .red
        case 25..<50:
            return .orange
        case 50..<75:
            return .yellow
        case 75..<100:
            return .blue
        default:
            return .green
        }
    }

    // MARK: - Actions

    private func exportToClipboard() {
        exportedText = generateExportText()
        NSPasteboard.general.clearContents()
        NSPasteboard.general.setString(exportedText, forType: .string)
        showingExportAlert = true
    }

    private func exportToNotes() {
        let text = generateExportText()
        // This will be implemented in Phase 4
        // For now, just copy to clipboard
        NSPasteboard.general.clearContents()
        NSPasteboard.general.setString(text, forType: .string)
    }

    private func openInYouTube() {
        if let url = URL(string: project.youtubeUrl) {
            NSWorkspace.shared.open(url)
        }
    }

    private func generateExportText() -> String {
        var text = "# \(project.title)\n\n"
        text += "YouTube: \(project.youtubeUrl)\n\n"
        text += "## Action Plan\n\n"

        for (index, task) in sortedTasks.enumerated() {
            let checkbox = task.isCompleted ? "[x]" : "[ ]"
            text += "\(index + 1). \(checkbox) \(task.title)\n"
            if let details = task.details, !details.isEmpty {
                text += "   \(details)\n"
            }
        }

        text += "\n---\n"
        text += "Progress: \(project.completedTasksCount)/\(project.tasks.count) (\(Int(project.progressPercentage))%)\n"
        text += "Generated by TubePlanner on \(Date().formatted())\n"

        return text
    }
}

// MARK: - Task Row View

struct TaskRowView: View {
    @Bindable var task: TaskItem

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            // Checkbox
            Button {
                withAnimation(.spring(response: 0.3)) {
                    task.toggleCompletion()
                }
            } label: {
                Image(systemName: task.isCompleted ? "checkmark.circle.fill" : "circle")
                    .font(.title3)
                    .foregroundStyle(task.isCompleted ? .green : .secondary)
            }
            .buttonStyle(.plain)

            VStack(alignment: .leading, spacing: 4) {
                // Title
                Text(task.title)
                    .font(.body)
                    .strikethrough(task.isCompleted, color: .secondary)
                    .foregroundStyle(task.isCompleted ? .secondary : .primary)

                // Details
                if let details = task.details, !details.isEmpty {
                    Text(details)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                // Completion timestamp
                if task.isCompleted, let completedAt = task.completedAt {
                    Text("Completed \(completedAt.formatted(.relative(presentation: .named)))")
                        .font(.caption2)
                        .foregroundStyle(.tertiary)
                }
            }

            Spacer()
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(task.isCompleted ? Color.green.opacity(0.05) : Color.clear)
        )
        .overlay {
            RoundedRectangle(cornerRadius: 8)
                .strokeBorder(task.isCompleted ? Color.green.opacity(0.3) : Color.secondary.opacity(0.2), lineWidth: 1)
        }
    }
}

// MARK: - Preview

#Preview("Detail View") {
    NavigationStack {
        DetailView(project: VideoProject.sample)
    }
    .modelContainer(for: [VideoProject.self, TaskItem.self], inMemory: true)
}
