//
//  SidebarView.swift
//  TubePlanner
//
//  Created on 19.11.2025
//  Sidebar with list of video projects
//

import SwiftUI
import SwiftData

struct SidebarView: View {
    // MARK: - Environment

    @Environment(\.modelContext) private var modelContext

    // MARK: - Properties

    let projects: [VideoProject]
    @Binding var selectedProject: VideoProject?
    @Binding var showingAddVideoSheet: Bool

    // MARK: - State

    @State private var searchText = ""

    // MARK: - Computed Properties

    private var filteredProjects: [VideoProject] {
        if searchText.isEmpty {
            return projects
        } else {
            return projects.filter { project in
                project.title.localizedCaseInsensitiveContains(searchText)
            }
        }
    }

    // MARK: - Body

    var body: some View {
        VStack(spacing: 0) {
            // MARK: Header
            headerView

            // MARK: Project List
            if filteredProjects.isEmpty {
                emptyStateView
            } else {
                projectListView
            }
        }
        .navigationTitle("Projects")
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button {
                    showingAddVideoSheet = true
                } label: {
                    Label("New Project", systemImage: "plus")
                }
            }
        }
        .searchable(text: $searchText, prompt: "Search projects")
    }

    // MARK: - Subviews

    private var headerView: some View {
        HStack {
            Text("\(projects.count) project\(projects.count == 1 ? "" : "s")")
                .font(.caption)
                .foregroundStyle(.secondary)

            Spacer()
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
        .background(.ultraThinMaterial)
    }

    private var projectListView: some View {
        List(selection: $selectedProject) {
            ForEach(filteredProjects) { project in
                ProjectRowView(project: project)
                    .tag(project)
                    .contextMenu {
                        Button("Delete", systemImage: "trash", role: .destructive) {
                            deleteProject(project)
                        }
                    }
            }
            .onDelete(perform: deleteProjects)
        }
        .listStyle(.sidebar)
    }

    private var emptyStateView: some View {
        ContentUnavailableView {
            Label("No Projects", systemImage: "video.slash")
        } description: {
            if searchText.isEmpty {
                Text("Create your first project to get started")
            } else {
                Text("No projects match '\(searchText)'")
            }
        } actions: {
            if searchText.isEmpty {
                Button {
                    showingAddVideoSheet = true
                } label: {
                    Label("New Project", systemImage: "plus")
                }
                .buttonStyle(.borderedProminent)
            }
        }
    }

    // MARK: - Actions

    private func deleteProjects(at offsets: IndexSet) {
        for index in offsets {
            let project = filteredProjects[index]
            deleteProject(project)
        }
    }

    private func deleteProject(_ project: VideoProject) {
        withAnimation {
            if selectedProject?.id == project.id {
                selectedProject = nil
            }
            modelContext.delete(project)
        }
    }
}

// MARK: - Project Row View

struct ProjectRowView: View {
    let project: VideoProject

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(project.title)
                .font(.headline)
                .lineLimit(2)

            HStack(spacing: 8) {
                // Task count badge
                Label("\(project.tasks.count)", systemImage: "checkmark.circle")
                    .font(.caption)
                    .foregroundStyle(.secondary)

                // Progress indicator
                if !project.tasks.isEmpty {
                    ProgressView(value: project.progressPercentage, total: 100)
                        .frame(maxWidth: 60)

                    Text("\(Int(project.progressPercentage))%")
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                }
            }

            Text(project.createdAt.formatted(date: .abbreviated, time: .omitted))
                .font(.caption2)
                .foregroundStyle(.tertiary)
        }
        .padding(.vertical, 4)
    }
}

// MARK: - Preview

#Preview("Sidebar with Projects") {
    NavigationSplitView {
        SidebarView(
            projects: [
                VideoProject.sample,
                VideoProject(
                    title: "Short Title",
                    youtubeUrl: "https://youtube.com/watch?v=test",
                    videoId: "test"
                )
            ],
            selectedProject: .constant(nil),
            showingAddVideoSheet: .constant(false)
        )
    } detail: {
        Text("Detail")
    }
    .modelContainer(for: [VideoProject.self, TaskItem.self], inMemory: true)
}

#Preview("Empty Sidebar") {
    NavigationSplitView {
        SidebarView(
            projects: [],
            selectedProject: .constant(nil),
            showingAddVideoSheet: .constant(false)
        )
    } detail: {
        Text("Detail")
    }
    .modelContainer(for: [VideoProject.self, TaskItem.self], inMemory: true)
}
