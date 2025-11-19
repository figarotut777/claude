//
//  HistoryItem.swift
//  BizCalc
//
//  Model for calculator history entries
//

import Foundation

struct HistoryItem: Identifiable, Codable {
    let id: UUID
    let timestamp: Date
    let expression: String
    let result: Double

    init(expression: String, result: Double) {
        self.id = UUID()
        self.timestamp = Date()
        self.expression = expression
        self.result = result
    }

    // Formatted display string for history tape
    var displayString: String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        formatter.groupingSeparator = " "
        formatter.maximumFractionDigits = 8
        formatter.minimumFractionDigits = 0

        let formattedResult = formatter.string(from: NSNumber(value: result)) ?? "\(result)"
        return "\(expression) = \(formattedResult)"
    }

    // Time formatted for display
    var timeString: String {
        let formatter = DateFormatter()
        formatter.timeStyle = .short
        return formatter.string(from: timestamp)
    }
}
