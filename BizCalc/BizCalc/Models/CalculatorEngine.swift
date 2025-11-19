//
//  CalculatorEngine.swift
//  BizCalc
//
//  Calculator engine with business logic for margin, markup, tax calculations
//

import Foundation

enum CalculatorOperation {
    case none
    case add
    case subtract
    case multiply
    case divide
    case taxAdd
    case taxSubtract
    case margin
    case markup
    case discount
}

enum CalculatorButton: Equatable {
    case digit(Int)
    case decimal
    case operation(CalculatorOperation)
    case equals
    case clear
    case negate
    case percent

    // Business buttons
    case taxPlus
    case taxMinus
    case margin
    case markup
    case discount

    var displayText: String {
        switch self {
        case .digit(let num): return "\(num)"
        case .decimal: return "."
        case .operation(.add): return "+"
        case .operation(.subtract): return "−"
        case .operation(.multiply): return "×"
        case .operation(.divide): return "÷"
        case .equals: return "="
        case .clear: return "AC"
        case .negate: return "±"
        case .percent: return "%"
        case .taxPlus: return "TAX+"
        case .taxMinus: return "TAX−"
        case .margin: return "MARGIN"
        case .markup: return "MARKUP"
        case .discount: return "DISC"
        default: return ""
        }
    }
}

class CalculatorEngine: ObservableObject {
    // MARK: - Published Properties
    @Published var display: String = "0"
    @Published var isEnteringNumber = false
    @Published var storedValue: Double = 0
    @Published var currentOperation: CalculatorOperation = .none
    @Published var taxRate: Double = 20.0 // Default 20% tax
    @Published var waitingForSecondOperand = false

    // MARK: - Display Formatting
    private let formatter: NumberFormatter = {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        formatter.groupingSeparator = " " // Using space as thousand separator
        formatter.maximumFractionDigits = 8
        formatter.minimumFractionDigits = 0
        return formatter
    }()

    // MARK: - Current Value
    var currentValue: Double {
        get {
            return Double(display.replacingOccurrences(of: " ", with: "")) ?? 0
        }
        set {
            display = formatNumber(newValue)
        }
    }

    // MARK: - Number Formatting
    func formatNumber(_ number: Double) -> String {
        // Remove trailing zeros and format with thousand separators
        let formatted = formatter.string(from: NSNumber(value: number)) ?? "0"
        return formatted
    }

    // MARK: - Input Handling
    func handleButton(_ button: CalculatorButton) {
        switch button {
        case .digit(let digit):
            handleDigit(digit)

        case .decimal:
            handleDecimal()

        case .clear:
            handleClear()

        case .negate:
            handleNegate()

        case .operation(let op):
            handleOperation(op)

        case .equals:
            handleEquals()

        case .taxPlus:
            handleTaxAdd()

        case .taxMinus:
            handleTaxSubtract()

        case .margin:
            handleMargin()

        case .markup:
            handleMarkup()

        case .discount:
            handleDiscount()

        case .percent:
            handlePercent()
        }
    }

    // MARK: - Digit Input
    private func handleDigit(_ digit: Int) {
        if waitingForSecondOperand {
            display = "\(digit)"
            waitingForSecondOperand = false
            isEnteringNumber = true
        } else if isEnteringNumber {
            let cleanDisplay = display.replacingOccurrences(of: " ", with: "")
            if cleanDisplay == "0" {
                display = "\(digit)"
            } else {
                display = formatNumber(Double(cleanDisplay + "\(digit)") ?? 0)
            }
        } else {
            display = "\(digit)"
            isEnteringNumber = true
        }
    }

    // MARK: - Decimal Point
    private func handleDecimal() {
        let cleanDisplay = display.replacingOccurrences(of: " ", with: "")

        if waitingForSecondOperand {
            display = "0."
            waitingForSecondOperand = false
            isEnteringNumber = true
        } else if isEnteringNumber {
            if !cleanDisplay.contains(".") {
                display = cleanDisplay + "."
            }
        } else {
            display = "0."
            isEnteringNumber = true
        }
    }

    // MARK: - Clear
    private func handleClear() {
        display = "0"
        storedValue = 0
        currentOperation = .none
        isEnteringNumber = false
        waitingForSecondOperand = false
    }

    // MARK: - Negate
    private func handleNegate() {
        let value = currentValue
        currentValue = -value
    }

    // MARK: - Basic Operations
    private func handleOperation(_ operation: CalculatorOperation) {
        if currentOperation != .none && isEnteringNumber {
            handleEquals()
        }

        storedValue = currentValue
        currentOperation = operation
        waitingForSecondOperand = true
        isEnteringNumber = false
    }

    // MARK: - Equals
    func handleEquals() {
        guard currentOperation != .none else { return }

        let result = performCalculation()
        currentValue = result
        currentOperation = .none
        isEnteringNumber = false
        waitingForSecondOperand = false
    }

    // MARK: - Perform Calculation
    private func performCalculation() -> Double {
        switch currentOperation {
        case .add:
            return storedValue + currentValue
        case .subtract:
            return storedValue - currentValue
        case .multiply:
            return storedValue * currentValue
        case .divide:
            return currentValue != 0 ? storedValue / currentValue : 0
        case .taxAdd:
            return calculateTaxAdd(storedValue, rate: currentValue)
        case .taxSubtract:
            return calculateTaxSubtract(storedValue, rate: currentValue)
        case .margin:
            return calculateMargin(cost: storedValue, marginPercent: currentValue)
        case .markup:
            return calculateMarkup(cost: storedValue, markupPercent: currentValue)
        case .discount:
            return calculateDiscount(price: storedValue, discountPercent: currentValue)
        case .none:
            return currentValue
        }
    }

    // MARK: - Business Calculations

    /// TAX+: Add tax to value
    /// Formula: Value * (1 + TaxRate/100)
    private func calculateTaxAdd(_ value: Double, rate: Double) -> Double {
        return value * (1 + rate / 100)
    }

    /// TAX-: Extract tax from value (get value without tax)
    /// Formula: Value / (1 + TaxRate/100)
    private func calculateTaxSubtract(_ value: Double, rate: Double) -> Double {
        return value / (1 + rate / 100)
    }

    /// MARGIN: Calculate selling price based on cost and desired margin percentage
    /// ВАЖНО: Маржа отличается от наценки!
    /// Formula: Price = Cost / (1 - Margin/100)
    /// Example: Cost = 100, Margin = 20% → Price = 100 / 0.8 = 125
    private func calculateMargin(cost: Double, marginPercent: Double) -> Double {
        // Prevent division by zero or invalid margin (>= 100%)
        guard marginPercent < 100 && marginPercent >= 0 else {
            return cost
        }
        return cost / (1 - marginPercent / 100)
    }

    /// MARKUP: Calculate selling price based on cost and markup percentage
    /// Formula: Price = Cost * (1 + Markup/100)
    /// Example: Cost = 100, Markup = 20% → Price = 100 * 1.2 = 120
    private func calculateMarkup(cost: Double, markupPercent: Double) -> Double {
        return cost * (1 + markupPercent / 100)
    }

    /// DISCOUNT: Calculate final price after discount
    /// Formula: FinalPrice = Price * (1 - Discount/100)
    /// Example: Price = 100, Discount = 20% → FinalPrice = 100 * 0.8 = 80
    private func calculateDiscount(price: Double, discountPercent: Double) -> Double {
        return price * (1 - discountPercent / 100)
    }

    // MARK: - Business Function Handlers

    private func handleTaxAdd() {
        storedValue = currentValue
        currentOperation = .taxAdd
        waitingForSecondOperand = true
        isEnteringNumber = false
    }

    private func handleTaxSubtract() {
        storedValue = currentValue
        currentOperation = .taxSubtract
        waitingForSecondOperand = true
        isEnteringNumber = false
    }

    private func handleMargin() {
        storedValue = currentValue
        currentOperation = .margin
        waitingForSecondOperand = true
        isEnteringNumber = false
    }

    private func handleMarkup() {
        storedValue = currentValue
        currentOperation = .markup
        waitingForSecondOperand = true
        isEnteringNumber = false
    }

    private func handleDiscount() {
        storedValue = currentValue
        currentOperation = .discount
        waitingForSecondOperand = true
        isEnteringNumber = false
    }

    private func handlePercent() {
        // Convert current value to percentage of stored value
        if currentOperation != .none {
            let percent = storedValue * (currentValue / 100)
            currentValue = percent
        } else {
            currentValue = currentValue / 100
        }
    }

    // MARK: - History Support
    func getOperationString() -> String {
        guard currentOperation != .none else { return "" }

        switch currentOperation {
        case .add: return "+"
        case .subtract: return "−"
        case .multiply: return "×"
        case .divide: return "÷"
        case .taxAdd: return "TAX+ \(taxRate)%"
        case .taxSubtract: return "TAX− \(taxRate)%"
        case .margin: return "MARGIN"
        case .markup: return "MARKUP"
        case .discount: return "DISCOUNT"
        case .none: return ""
        }
    }
}
