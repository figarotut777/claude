//
//  TaskItem.swift
//  TubePlanner
//
//  Created on 19.11.2025
//  Represents a single actionable task within an action plan
//

import Foundation
import SwiftData

@Model
final class TaskItem {
    // MARK: - Properties

    /// Unique identifier
    var id: UUID

    /// Task title (main action description)
    var title: String

    /// Optional detailed description or notes
    var details: String?

    /// Completion status
    var isCompleted: Bool

    /// Order index for sorting tasks
    var orderIndex: Int

    /// Completion timestamp (optional)
    var completedAt: Date?

    /// Parent project (inverse relationship)
    var project: VideoProject?

    // MARK: - Initialization

    init(
        id: UUID = UUID(),
        title: String,
        details: String? = nil,
        orderIndex: Int,
        project: VideoProject? = nil,
        isCompleted: Bool = false,
        completedAt: Date? = nil
    ) {
        self.id = id
        self.title = title
        self.details = details
        self.orderIndex = orderIndex
        self.project = project
        self.isCompleted = isCompleted
        self.completedAt = completedAt
    }

    // MARK: - Methods

    /// Toggle completion status
    func toggleCompletion() {
        isCompleted.toggle()
        completedAt = isCompleted ? Date() : nil
        project?.markAsUpdated()
    }

    /// Mark as completed
    func complete() {
        isCompleted = true
        completedAt = Date()
        project?.markAsUpdated()
    }

    /// Mark as incomplete
    func uncomplete() {
        isCompleted = false
        completedAt = nil
        project?.markAsUpdated()
    }
}

// MARK: - Comparable

extension TaskItem: Comparable {
    static func < (lhs: TaskItem, rhs: TaskItem) -> Bool {
        lhs.orderIndex < rhs.orderIndex
    }
}

// MARK: - Preview Helpers

#if DEBUG
extension TaskItem {
    /// Sample task for SwiftUI previews
    static var sample: TaskItem {
        TaskItem(
            title: "Preheat the oven to 230°C",
            details: "Use a Dutch oven if available for better steam",
            orderIndex: 0,
            isCompleted: false
        )
    }

    /// Sample completed task
    static var sampleCompleted: TaskItem {
        TaskItem(
            title: "Mix flour and water",
            details: "Use a wooden spoon for initial mixing",
            orderIndex: 1,
            isCompleted: true,
            completedAt: Date().addingTimeInterval(-3600)
        )
    }
}
#endif
