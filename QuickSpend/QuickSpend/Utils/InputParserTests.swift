//
//  InputParserTests.swift
//  QuickSpend
//
//  Created by Claude on 19.11.2025.
//
//  Test cases for InputParser logic
//

import Foundation

/// Test suite for InputParser
/// Run this to verify parsing logic works correctly
final class InputParserTests {

    static func runTests() {
        print("🧪 Running InputParser tests...\n")

        // Test 1: Only amount
        test(
            input: "50",
            expectedAmount: 50,
            expectedCategory: "Uncategorized",
            expectedNote: nil,
            description: "Only amount"
        )

        // Test 2: Amount with category
        test(
            input: "500 кофе",
            expectedAmount: 500,
            expectedCategory: "кофе",
            expectedNote: nil,
            description: "Amount with category"
        )

        // Test 3: Amount with category and note
        test(
            input: "1200 еда бизнес ланч",
            expectedAmount: 1200,
            expectedCategory: "еда",
            expectedNote: "бизнес ланч",
            description: "Amount with category and note"
        )

        // Test 4: Decimal amount
        test(
            input: "99.50 такси",
            expectedAmount: 99.50,
            expectedCategory: "такси",
            expectedNote: nil,
            description: "Decimal amount"
        )

        // Test 5: Comma as decimal separator
        test(
            input: "150,75 кофе",
            expectedAmount: 150.75,
            expectedCategory: "кофе",
            expectedNote: nil,
            description: "Comma as decimal separator"
        )

        // Test 6: Complex note
        test(
            input: "5000 продукты недельный запас для семьи",
            expectedAmount: 5000,
            expectedCategory: "продукты",
            expectedNote: "недельный запас для семьи",
            description: "Complex note with multiple words"
        )

        // Test 7: English input
        test(
            input: "300 Coffee morning espresso",
            expectedAmount: 300,
            expectedCategory: "Coffee",
            expectedNote: "morning espresso",
            description: "English input"
        )

        // Test 8: Large amount
        test(
            input: "15000 rent",
            expectedAmount: 15000,
            expectedCategory: "rent",
            expectedNote: nil,
            description: "Large amount"
        )

        // Test 9: Amount in middle of text (should find first number)
        test(
            input: "купил за 250 кофе",
            expectedAmount: 250,
            expectedCategory: "кофе",
            expectedNote: nil,
            description: "Amount in middle of text"
        )

        print("\n✅ All tests completed!")
    }

    private static func test(
        input: String,
        expectedAmount: Double,
        expectedCategory: String,
        expectedNote: String?,
        description: String
    ) {
        guard let result = InputParser.parse(text: input) else {
            print("❌ \(description): Failed to parse '\(input)'")
            return
        }

        var passed = true
        var errors: [String] = []

        if result.amount != expectedAmount {
            passed = false
            errors.append("Amount mismatch: expected \(expectedAmount), got \(result.amount)")
        }

        if result.categoryName != expectedCategory {
            passed = false
            errors.append("Category mismatch: expected '\(expectedCategory)', got '\(result.categoryName)'")
        }

        if result.note != expectedNote {
            passed = false
            errors.append("Note mismatch: expected '\(expectedNote ?? "nil")', got '\(result.note ?? "nil")'")
        }

        if passed {
            print("✅ \(description)")
            print("   Input: '\(input)'")
            print("   → \(result.amount) · \(result.categoryName)" + (result.note.map { " · \($0)" } ?? ""))
        } else {
            print("❌ \(description)")
            print("   Input: '\(input)'")
            for error in errors {
                print("   \(error)")
            }
        }
        print()
    }
}

// Uncomment to run tests:
// InputParserTests.runTests()
