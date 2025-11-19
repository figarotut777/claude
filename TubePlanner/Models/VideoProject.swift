//
//  VideoProject.swift
//  TubePlanner
//
//  Created on 19.11.2025
//  Core data model representing a YouTube video with its action plan
//

import Foundation
import SwiftData

@Model
final class VideoProject {
    // MARK: - Properties

    /// Unique identifier
    var id: UUID

    /// Video title (extracted from YouTube or user-provided)
    var title: String

    /// Original YouTube URL
    var youtubeUrl: String

    /// YouTube video ID (extracted from URL)
    var videoId: String

    /// Thumbnail URL (optional, for future use)
    var thumbnailUrl: String?

    /// Creation timestamp
    var createdAt: Date

    /// Last update timestamp
    var updatedAt: Date

    /// Related tasks (one-to-many relationship)
    @Relationship(deleteRule: .cascade, inverse: \TaskItem.project)
    var tasks: [TaskItem]

    /// Progress percentage (computed property)
    var progressPercentage: Double {
        guard !tasks.isEmpty else { return 0.0 }
        let completed = tasks.filter { $0.isCompleted }.count
        return Double(completed) / Double(tasks.count) * 100.0
    }

    /// Number of completed tasks
    var completedTasksCount: Int {
        tasks.filter { $0.isCompleted }.count
    }

    // MARK: - Initialization

    init(
        id: UUID = UUID(),
        title: String,
        youtubeUrl: String,
        videoId: String,
        thumbnailUrl: String? = nil,
        createdAt: Date = Date(),
        updatedAt: Date = Date(),
        tasks: [TaskItem] = []
    ) {
        self.id = id
        self.title = title
        self.youtubeUrl = youtubeUrl
        self.videoId = videoId
        self.thumbnailUrl = thumbnailUrl
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.tasks = tasks
    }

    // MARK: - Helpers

    /// Update the `updatedAt` timestamp
    func markAsUpdated() {
        self.updatedAt = Date()
    }
}

// MARK: - Preview Helpers

#if DEBUG
extension VideoProject {
    /// Sample project for SwiftUI previews
    static var sample: VideoProject {
        let project = VideoProject(
            title: "How to Make Perfect Sourdough Bread",
            youtubeUrl: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            videoId: "dQw4w9WgXcQ",
            thumbnailUrl: "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg"
        )

        project.tasks = [
            TaskItem(
                title: "Prepare the starter",
                details: "Feed your sourdough starter 4-6 hours before mixing",
                orderIndex: 0,
                project: project
            ),
            TaskItem(
                title: "Mix the dough",
                details: "Combine flour, water, starter, and salt",
                orderIndex: 1,
                project: project
            ),
            TaskItem(
                title: "Bulk fermentation",
                details: "Let it rise for 4-5 hours with periodic stretches",
                orderIndex: 2,
                project: project,
                isCompleted: true
            )
        ]

        return project
    }
}
#endif
