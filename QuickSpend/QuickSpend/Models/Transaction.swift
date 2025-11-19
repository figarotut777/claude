//
//  Transaction.swift
//  QuickSpend
//
//  Created by Claude on 19.11.2025.
//

import Foundation
import SwiftData

@Model
final class Transaction {
    var amount: Double
    var date: Date
    var note: String?

    @Relationship var category: Category?

    init(amount: Double, date: Date = Date(), note: String? = nil, category: Category? = nil) {
        self.amount = amount
        self.date = date
        self.note = note
        self.category = category
    }

    /// Formatted amount as currency string
    var formattedAmount: String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        formatter.locale = Locale.current
        return formatter.string(from: NSNumber(value: amount)) ?? "\(amount)"
    }

    /// Formatted date as short string
    var formattedDate: String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}
