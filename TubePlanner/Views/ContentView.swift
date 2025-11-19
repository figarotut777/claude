//
//  ContentView.swift
//  TubePlanner
//
//  Created on 19.11.2025
//  Main split view container
//

import SwiftUI
import SwiftData

struct ContentView: View {
    // MARK: - Environment

    @Environment(\.modelContext) private var modelContext

    // MARK: - State

    @State private var selectedProject: VideoProject?
    @State private var showingAddVideoSheet = false
    @State private var columnVisibility: NavigationSplitViewVisibility = .all

    // MARK: - Queries

    @Query(sort: \VideoProject.createdAt, order: .reverse)
    private var projects: [VideoProject]

    // MARK: - Body

    var body: some View {
        NavigationSplitView(columnVisibility: $columnVisibility) {
            // MARK: Sidebar
            SidebarView(
                projects: projects,
                selectedProject: $selectedProject,
                showingAddVideoSheet: $showingAddVideoSheet
            )
        } detail: {
            // MARK: Detail
            if let selectedProject {
                DetailView(project: selectedProject)
            } else {
                // Empty state
                ContentUnavailableView {
                    Label("No Project Selected", systemImage: "video.slash")
                } description: {
                    Text("Select a video from the sidebar or create a new one")
                } actions: {
                    Button {
                        showingAddVideoSheet = true
                    } label: {
                        Label("New Video Project", systemImage: "plus.circle.fill")
                    }
                    .buttonStyle(.borderedProminent)
                }
            }
        }
        .sheet(isPresented: $showingAddVideoSheet) {
            AddVideoView(isPresented: $showingAddVideoSheet)
        }
        .onReceive(NotificationCenter.default.publisher(for: NSNotification.Name("ShowAddVideoSheet"))) { _ in
            showingAddVideoSheet = true
        }
    }
}

// MARK: - Preview

#Preview("With Projects") {
    ContentView()
        .modelContainer(previewContainer)
        .frame(width: 1000, height: 700)
}

#Preview("Empty State") {
    ContentView()
        .modelContainer(emptyPreviewContainer)
        .frame(width: 1000, height: 700)
}

// MARK: - Preview Containers

@MainActor
private var previewContainer: ModelContainer {
    do {
        let schema = Schema([VideoProject.self, TaskItem.self])
        let configuration = ModelConfiguration(schema: schema, isStoredInMemoryOnly: true)
        let container = try ModelContainer(for: schema, configurations: [configuration])

        // Insert sample data
        let project1 = VideoProject(
            title: "How to Make Sourdough Bread",
            youtubeUrl: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            videoId: "dQw4w9WgXcQ"
        )
        project1.tasks = [
            TaskItem(title: "Prepare starter", orderIndex: 0, project: project1, isCompleted: true),
            TaskItem(title: "Mix dough", orderIndex: 1, project: project1),
            TaskItem(title: "Bulk fermentation", orderIndex: 2, project: project1)
        ]

        let project2 = VideoProject(
            title: "SwiftUI Animation Tutorial",
            youtubeUrl: "https://www.youtube.com/watch?v=abc123",
            videoId: "abc123"
        )
        project2.tasks = [
            TaskItem(title: "Create basic animation", orderIndex: 0, project: project2),
            TaskItem(title: "Add spring effect", orderIndex: 1, project: project2)
        ]

        container.mainContext.insert(project1)
        container.mainContext.insert(project2)

        return container
    } catch {
        fatalError("Failed to create preview container: \(error)")
    }
}

@MainActor
private var emptyPreviewContainer: ModelContainer {
    do {
        let schema = Schema([VideoProject.self, TaskItem.self])
        let configuration = ModelConfiguration(schema: schema, isStoredInMemoryOnly: true)
        return try ModelContainer(for: schema, configurations: [configuration])
    } catch {
        fatalError("Failed to create preview container: \(error)")
    }
}
