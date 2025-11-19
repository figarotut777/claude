//
//  FormulaTests.swift
//  BizCalc Tests
//
//  Unit tests for business calculation formulas
//  Run these tests to verify margin, markup, tax calculations are correct
//

import XCTest
@testable import BizCalc

final class FormulaTests: XCTestCase {

    var engine: CalculatorEngine!

    override func setUp() {
        super.setUp()
        engine = CalculatorEngine()
    }

    override func tearDown() {
        engine = nil
        super.tearDown()
    }

    // MARK: - Margin Tests

    /// Test Case: 100 руб себестоимость, 20% маржа → 125 руб цена
    /// Formula: Price = Cost / (1 - Margin/100)
    func testMarginCalculation20Percent() {
        // Given
        let cost: Double = 100
        let marginPercent: Double = 20

        // When
        engine.currentValue = cost
        engine.handleButton(.margin)
        engine.currentValue = marginPercent
        engine.handleEquals()

        // Then
        let expectedPrice: Double = 125.0
        XCTAssertEqual(engine.currentValue, expectedPrice, accuracy: 0.01,
                       "Маржа 20% от 100₽ должна дать цену 125₽")
    }

    /// Test Case: 100 руб себестоимость, 50% маржа → 200 руб цена
    func testMarginCalculation50Percent() {
        let cost: Double = 100
        let marginPercent: Double = 50

        engine.currentValue = cost
        engine.handleButton(.margin)
        engine.currentValue = marginPercent
        engine.handleEquals()

        let expectedPrice: Double = 200.0
        XCTAssertEqual(engine.currentValue, expectedPrice, accuracy: 0.01,
                       "Маржа 50% от 100₽ должна дать цену 200₽")
    }

    /// Test Case: 200 руб себестоимость, 25% маржа → 266.67 руб цена
    func testMarginCalculation25Percent() {
        let cost: Double = 200
        let marginPercent: Double = 25

        engine.currentValue = cost
        engine.handleButton(.margin)
        engine.currentValue = marginPercent
        engine.handleEquals()

        let expectedPrice: Double = 266.67
        XCTAssertEqual(engine.currentValue, expectedPrice, accuracy: 0.01,
                       "Маржа 25% от 200₽ должна дать цену ~266.67₽")
    }

    // MARK: - Markup Tests

    /// Test Case: 100 руб себестоимость, 20% наценка → 120 руб цена
    /// Formula: Price = Cost * (1 + Markup/100)
    func testMarkupCalculation20Percent() {
        // Given
        let cost: Double = 100
        let markupPercent: Double = 20

        // When
        engine.currentValue = cost
        engine.handleButton(.markup)
        engine.currentValue = markupPercent
        engine.handleEquals()

        // Then
        let expectedPrice: Double = 120.0
        XCTAssertEqual(engine.currentValue, expectedPrice, accuracy: 0.01,
                       "Наценка 20% на 100₽ должна дать цену 120₽")
    }

    /// Test Case: 100 руб себестоимость, 50% наценка → 150 руб цена
    func testMarkupCalculation50Percent() {
        let cost: Double = 100
        let markupPercent: Double = 50

        engine.currentValue = cost
        engine.handleButton(.markup)
        engine.currentValue = markupPercent
        engine.handleEquals()

        let expectedPrice: Double = 150.0
        XCTAssertEqual(engine.currentValue, expectedPrice, accuracy: 0.01,
                       "Наценка 50% на 100₽ должна дать цену 150₽")
    }

    /// Test Case: 200 руб себестоимость, 25% наценка → 250 руб цена
    func testMarkupCalculation25Percent() {
        let cost: Double = 200
        let markupPercent: Double = 25

        engine.currentValue = cost
        engine.handleButton(.markup)
        engine.currentValue = markupPercent
        engine.handleEquals()

        let expectedPrice: Double = 250.0
        XCTAssertEqual(engine.currentValue, expectedPrice, accuracy: 0.01,
                       "Наценка 25% на 200₽ должна дать цену 250₽")
    }

    // MARK: - Margin vs Markup Comparison

    /// Important test: Verify that Margin and Markup give DIFFERENT results
    func testMarginVsMarkupDifference() {
        let cost: Double = 100
        let percent: Double = 20

        // Calculate Margin
        engine.currentValue = cost
        engine.handleButton(.margin)
        engine.currentValue = percent
        engine.handleEquals()
        let priceWithMargin = engine.currentValue

        // Reset and calculate Markup
        engine.handleButton(.clear)
        engine.currentValue = cost
        engine.handleButton(.markup)
        engine.currentValue = percent
        engine.handleEquals()
        let priceWithMarkup = engine.currentValue

        // Verify they are different
        XCTAssertNotEqual(priceWithMargin, priceWithMarkup,
                          "Маржа и наценка должны давать РАЗНЫЕ результаты!")
        XCTAssertEqual(priceWithMargin, 125.0, accuracy: 0.01, "Маржа 20% = 125₽")
        XCTAssertEqual(priceWithMarkup, 120.0, accuracy: 0.01, "Наценка 20% = 120₽")
    }

    // MARK: - Tax Tests

    /// Test Case: 1000 руб + НДС 20% → 1200 руб
    /// Formula: Value * (1 + TaxRate/100)
    func testTaxAddCalculation() {
        let value: Double = 1000
        let taxRate: Double = 20

        engine.currentValue = value
        engine.handleButton(.taxPlus)
        engine.currentValue = taxRate
        engine.handleEquals()

        let expectedResult: Double = 1200.0
        XCTAssertEqual(engine.currentValue, expectedResult, accuracy: 0.01,
                       "1000₽ + НДС 20% = 1200₽")
    }

    /// Test Case: 1200 руб выделить НДС 20% → 1000 руб без НДС
    /// Formula: Value / (1 + TaxRate/100)
    func testTaxSubtractCalculation() {
        let valueWithTax: Double = 1200
        let taxRate: Double = 20

        engine.currentValue = valueWithTax
        engine.handleButton(.taxMinus)
        engine.currentValue = taxRate
        engine.handleEquals()

        let expectedResult: Double = 1000.0
        XCTAssertEqual(engine.currentValue, expectedResult, accuracy: 0.01,
                       "1200₽ выделить НДС 20% = 1000₽")
    }

    // MARK: - Discount Tests

    /// Test Case: 500 руб − скидка 15% → 425 руб
    /// Formula: FinalPrice = Price * (1 - Discount/100)
    func testDiscountCalculation() {
        let price: Double = 500
        let discountPercent: Double = 15

        engine.currentValue = price
        engine.handleButton(.discount)
        engine.currentValue = discountPercent
        engine.handleEquals()

        let expectedResult: Double = 425.0
        XCTAssertEqual(engine.currentValue, expectedResult, accuracy: 0.01,
                       "500₽ − скидка 15% = 425₽")
    }

    // MARK: - Edge Cases

    /// Test: Division by zero protection
    func testDivisionByZero() {
        engine.currentValue = 100
        engine.handleButton(.operation(.divide))
        engine.currentValue = 0
        engine.handleEquals()

        // Should not crash and return 0
        XCTAssertEqual(engine.currentValue, 0, "Деление на ноль должно вернуть 0")
    }

    /// Test: Margin 100% should not cause division by zero
    func testMargin100PercentEdgeCase() {
        engine.currentValue = 100
        engine.handleButton(.margin)
        engine.currentValue = 100 // Edge case: 100%
        engine.handleEquals()

        // Should return original value (or handle gracefully)
        XCTAssertEqual(engine.currentValue, 100, "Маржа 100% должна обрабатываться корректно")
    }

    // MARK: - Real World Scenarios

    /// Real scenario: Calculate selling price for desired margin
    func testRealWorldMarginScenario() {
        // Я купил товар за 2500₽ и хочу 30% маржи. Какая цена продажи?
        let cost: Double = 2500
        let desiredMargin: Double = 30

        engine.currentValue = cost
        engine.handleButton(.margin)
        engine.currentValue = desiredMargin
        engine.handleEquals()

        let expectedPrice: Double = 3571.43 // 2500 / (1 - 0.3)
        XCTAssertEqual(engine.currentValue, expectedPrice, accuracy: 0.01,
                       "Себестоимость 2500₽ с маржой 30% = ~3571.43₽")
    }

    /// Real scenario: Add tax to invoice
    func testRealWorldTaxScenario() {
        // Счет на 15000₽ + НДС 20%
        let invoiceAmount: Double = 15000
        let vat: Double = 20

        engine.currentValue = invoiceAmount
        engine.handleButton(.taxPlus)
        engine.currentValue = vat
        engine.handleEquals()

        let expectedTotal: Double = 18000
        XCTAssertEqual(engine.currentValue, expectedTotal, accuracy: 0.01,
                       "15000₽ + НДС 20% = 18000₽")
    }
}

// MARK: - Manual Test Instructions

/*
 MANUAL TESTING CHECKLIST:

 1. Launch BizCalc app
 2. Test Margin:
    - Input: 100
    - Press: MARGIN
    - Input: 20
    - Press: =
    - Expected: 125

 3. Test Markup:
    - Press: AC (clear)
    - Input: 100
    - Press: MARKUP
    - Input: 20
    - Press: =
    - Expected: 120

 4. Test Tax+:
    - Press: AC
    - Input: 1000
    - Press: TAX+
    - Input: 20
    - Press: =
    - Expected: 1200

 5. Test Tax−:
    - Press: AC
    - Input: 1200
    - Press: TAX−
    - Input: 20
    - Press: =
    - Expected: 1000

 6. Test Discount:
    - Press: AC
    - Input: 500
    - Press: DISC
    - Input: 15
    - Press: =
    - Expected: 425

 7. Verify History:
    - All calculations should appear in history panel
    - Click on any result to recall it
    - Copy history and verify format

 8. Test Keyboard:
    - Use NumPad for input
    - Press Enter for equals
    - Press C for clear

 ✓ All tests should pass!
 */
