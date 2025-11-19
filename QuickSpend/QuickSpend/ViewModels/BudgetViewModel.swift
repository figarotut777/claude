//
//  BudgetViewModel.swift
//  QuickSpend
//
//  Created by Claude on 19.11.2025.
//

import Foundation
import SwiftData
import SwiftUI

@Observable
final class BudgetViewModel {
    var inputText: String = ""
    var isInputValid: Bool = false

    private var modelContext: ModelContext

    init(modelContext: ModelContext) {
        self.modelContext = modelContext
    }

    /// Validates input text
    func validateInput() {
        isInputValid = InputParser.containsValidAmount(text: inputText)
    }

    /// Processes input and creates transaction
    func submitTransaction() -> Bool {
        guard let parsed = InputParser.parse(text: inputText) else {
            return false
        }

        // Find or create category
        let category = findOrCreateCategory(name: parsed.categoryName)

        // Create transaction
        let transaction = Transaction(
            amount: parsed.amount,
            date: Date(),
            note: parsed.note,
            category: category
        )

        modelContext.insert(transaction)

        do {
            try modelContext.save()
            clearInput()
            return true
        } catch {
            print("Error saving transaction: \(error)")
            return false
        }
    }

    /// Finds existing category or creates new one
    private func findOrCreateCategory(name: String) -> Category {
        let descriptor = FetchDescriptor<Category>(
            predicate: #Predicate { $0.name == name }
        )

        if let existing = try? modelContext.fetch(descriptor).first {
            return existing
        }

        // Create new category with auto-detected icon and color
        let icon = CategoryIconMapper.icon(for: name)
        let color = Category.defaultColor(for: name)

        let newCategory = Category(
            name: name,
            icon: icon,
            colorHex: color
        )

        modelContext.insert(newCategory)
        return newCategory
    }

    /// Clears input field
    func clearInput() {
        inputText = ""
        isInputValid = false
    }

    /// Deletes a transaction
    func deleteTransaction(_ transaction: Transaction) {
        modelContext.delete(transaction)
        try? modelContext.save()
    }

    /// Calculates total spending for current month
    func totalThisMonth(transactions: [Transaction]) -> Double {
        let calendar = Calendar.current
        let now = Date()

        return transactions
            .filter { calendar.isDate($0.date, equalTo: now, toGranularity: .month) }
            .reduce(0) { $0 + $1.amount }
    }

    /// Groups transactions by category for current month
    func categoryTotals(transactions: [Transaction]) -> [(category: String, amount: Double, icon: String, color: String)] {
        let calendar = Calendar.current
        let now = Date()

        // Filter current month
        let currentMonthTransactions = transactions.filter {
            calendar.isDate($0.date, equalTo: now, toGranularity: .month)
        }

        // Group by category
        var totals: [String: (amount: Double, icon: String, color: String)] = [:]

        for transaction in currentMonthTransactions {
            let categoryName = transaction.category?.name ?? "Uncategorized"
            let icon = transaction.category?.icon ?? "cart"
            let color = transaction.category?.colorHex ?? "#007AFF"

            if let existing = totals[categoryName] {
                totals[categoryName] = (existing.amount + transaction.amount, icon, color)
            } else {
                totals[categoryName] = (transaction.amount, icon, color)
            }
        }

        // Convert to array and sort by amount
        return totals
            .map { (category: $0.key, amount: $0.value.amount, icon: $0.value.icon, color: $0.value.color) }
            .sorted { $0.amount > $1.amount }
    }
}
