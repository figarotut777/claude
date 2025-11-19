//
//  Category.swift
//  QuickSpend
//
//  Created by Claude on 19.11.2025.
//

import Foundation
import SwiftData

@Model
final class Category {
    @Attribute(.unique) var name: String
    var icon: String // SF Symbol name
    var colorHex: String

    @Relationship(deleteRule: .cascade, inverse: \Transaction.category)
    var transactions: [Transaction]?

    init(name: String, icon: String = "cart", colorHex: String = "#007AFF") {
        self.name = name
        self.icon = icon
        self.colorHex = colorHex
    }

    /// Returns a default color based on common category names
    static func defaultColor(for categoryName: String) -> String {
        let lowercased = categoryName.lowercased()

        switch lowercased {
        case _ where lowercased.contains("еда") || lowercased.contains("food") || lowercased.contains("кофе") || lowercased.contains("coffee"):
            return "#FF9500" // Orange
        case _ where lowercased.contains("транспорт") || lowercased.contains("такси") || lowercased.contains("taxi") || lowercased.contains("transport"):
            return "#5856D6" // Purple
        case _ where lowercased.contains("развлечения") || lowercased.contains("entertainment") || lowercased.contains("кино") || lowercased.contains("cinema"):
            return "#FF2D55" // Pink
        case _ where lowercased.contains("здоровье") || lowercased.contains("health") || lowercased.contains("аптека") || lowercased.contains("pharmacy"):
            return "#34C759" // Green
        case _ where lowercased.contains("покупки") || lowercased.contains("shopping") || lowercased.contains("одежда") || lowercased.contains("clothes"):
            return "#AF52DE" // Purple
        default:
            return "#007AFF" // Blue
        }
    }
}
