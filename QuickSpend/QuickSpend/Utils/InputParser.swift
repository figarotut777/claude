//
//  InputParser.swift
//  QuickSpend
//
//  Created by Claude on 19.11.2025.
//

import Foundation

struct ParsedInput {
    let amount: Double
    let categoryName: String
    let note: String?
}

final class InputParser {

    /// Parses input string in format: "[Amount] [Category] [Note]"
    /// Examples:
    /// - "500 кофе" -> amount: 500, category: "кофе", note: nil
    /// - "1200 еда бизнес ланч" -> amount: 1200, category: "еда", note: "бизнес ланч"
    /// - "50" -> amount: 50, category: "Uncategorized", note: nil
    static func parse(text: String) -> ParsedInput? {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)

        guard !trimmed.isEmpty else { return nil }

        // Regex to find first number (integer or decimal)
        let numberPattern = #"(\d+(?:[.,]\d+)?)"#

        guard let numberRegex = try? NSRegularExpression(pattern: numberPattern),
              let numberMatch = numberRegex.firstMatch(
                in: trimmed,
                range: NSRange(trimmed.startIndex..., in: trimmed)
              ) else {
            return nil
        }

        // Extract amount
        let numberRange = Range(numberMatch.range, in: trimmed)!
        let numberString = String(trimmed[numberRange])
            .replacingOccurrences(of: ",", with: ".") // Handle comma as decimal separator

        guard let amount = Double(numberString) else { return nil }

        // Get text after the number
        let afterNumberIndex = numberRange.upperBound
        let remainingText = trimmed[afterNumberIndex...]
            .trimmingCharacters(in: .whitespacesAndNewlines)

        // If no text after number, use "Uncategorized"
        if remainingText.isEmpty {
            return ParsedInput(
                amount: amount,
                categoryName: "Uncategorized",
                note: nil
            )
        }

        // Split remaining text into words
        let words = remainingText.split(separator: " ", omittingEmptySubsequences: true)

        guard !words.isEmpty else {
            return ParsedInput(
                amount: amount,
                categoryName: "Uncategorized",
                note: nil
            )
        }

        // First word is category
        let categoryName = String(words[0])

        // Rest is note (if exists)
        let note: String? = words.count > 1
            ? words[1...].joined(separator: " ")
            : nil

        return ParsedInput(
            amount: amount,
            categoryName: categoryName,
            note: note
        )
    }

    /// Validates if input contains a valid amount
    static func containsValidAmount(text: String) -> Bool {
        let numberPattern = #"(\d+(?:[.,]\d+)?)"#
        guard let regex = try? NSRegularExpression(pattern: numberPattern) else {
            return false
        }

        let range = NSRange(text.startIndex..., in: text)
        return regex.firstMatch(in: text, range: range) != nil
    }
}
