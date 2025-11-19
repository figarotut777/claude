//
//  CalculatorViewModel.swift
//  BizCalc
//
//  ViewModel managing calculator state and history
//

import Foundation
import Combine

class CalculatorViewModel: ObservableObject {
    // MARK: - Published Properties
    @Published var engine = CalculatorEngine()
    @Published var history: [HistoryItem] = []
    @Published var showHistory = true

    private var cancellables = Set<AnyCancellable>()
    private var lastStoredValue: Double = 0
    private var lastOperation: CalculatorOperation = .none

    // MARK: - UserDefaults Keys
    private let historyKey = "calculatorHistory"
    private let taxRateKey = "taxRate"

    // MARK: - Initialization
    init() {
        loadHistory()
        loadTaxRate()
    }

    // MARK: - Button Handling
    func handleButton(_ button: CalculatorButton) {
        // Track operation before executing
        let previousOperation = engine.currentOperation
        let previousValue = engine.storedValue

        // Execute button action
        engine.handleButton(button)

        // Add to history when equals is pressed
        if button == .equals && previousOperation != .none {
            addToHistory(
                firstValue: previousValue,
                operation: previousOperation,
                secondValue: lastStoredValue,
                result: engine.currentValue
            )
        }

        // Store last value for history
        if engine.waitingForSecondOperand {
            lastStoredValue = engine.currentValue
            lastOperation = engine.currentOperation
        }
    }

    // MARK: - History Management
    private func addToHistory(firstValue: Double, operation: CalculatorOperation, secondValue: Double, result: Double) {
        let operationSymbol = getOperationSymbol(operation)
        let expression = formatExpression(firstValue: firstValue, operation: operationSymbol, secondValue: secondValue, operationType: operation)

        let item = HistoryItem(expression: expression, result: result)
        history.insert(item, at: 0) // Add to beginning (most recent first)

        // Limit history to 100 items
        if history.count > 100 {
            history.removeLast()
        }

        saveHistory()
    }

    private func formatExpression(firstValue: Double, operation: String, secondValue: Double, operationType: CalculatorOperation) -> String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        formatter.groupingSeparator = " "
        formatter.maximumFractionDigits = 8

        let first = formatter.string(from: NSNumber(value: firstValue)) ?? "\(firstValue)"
        let second = formatter.string(from: NSNumber(value: secondValue)) ?? "\(secondValue)"

        // Special formatting for business operations
        switch operationType {
        case .taxAdd, .taxSubtract:
            return "\(first) \(operation) \(second)%"
        case .margin:
            return "\(first) MARGIN \(second)%"
        case .markup:
            return "\(first) MARKUP \(second)%"
        case .discount:
            return "\(first) DISC \(second)%"
        default:
            return "\(first) \(operation) \(second)"
        }
    }

    private func getOperationSymbol(_ operation: CalculatorOperation) -> String {
        switch operation {
        case .add: return "+"
        case .subtract: return "−"
        case .multiply: return "×"
        case .divide: return "÷"
        case .taxAdd: return "TAX+"
        case .taxSubtract: return "TAX−"
        case .margin: return "MARGIN"
        case .markup: return "MARKUP"
        case .discount: return "DISC"
        case .none: return ""
        }
    }

    func clearHistory() {
        history.removeAll()
        saveHistory()
    }

    func selectHistoryItem(_ item: HistoryItem) {
        engine.currentValue = item.result
        engine.isEnteringNumber = false
    }

    func copyHistoryToClipboard() -> String {
        return history.map { $0.displayString }.joined(separator: "\n")
    }

    // MARK: - Persistence
    private func saveHistory() {
        if let encoded = try? JSONEncoder().encode(history) {
            UserDefaults.standard.set(encoded, forKey: historyKey)
        }
    }

    private func loadHistory() {
        if let data = UserDefaults.standard.data(forKey: historyKey),
           let decoded = try? JSONDecoder().decode([HistoryItem].self, from: data) {
            history = decoded
        }
    }

    private func saveTaxRate() {
        UserDefaults.standard.set(engine.taxRate, forKey: taxRateKey)
    }

    private func loadTaxRate() {
        let savedRate = UserDefaults.standard.double(forKey: taxRateKey)
        if savedRate > 0 {
            engine.taxRate = savedRate
        }
    }

    func updateTaxRate(_ newRate: Double) {
        engine.taxRate = newRate
        saveTaxRate()
    }

    // MARK: - Keyboard Support
    func handleKeyPress(_ key: String) {
        switch key {
        case "0"..."9":
            if let digit = Int(key) {
                handleButton(.digit(digit))
            }
        case ".":
            handleButton(.decimal)
        case "+":
            handleButton(.operation(.add))
        case "-":
            handleButton(.operation(.subtract))
        case "*", "×":
            handleButton(.operation(.multiply))
        case "/", "÷":
            handleButton(.operation(.divide))
        case "=", "\r", "\n": // Enter
            handleButton(.equals)
        case "c", "C": // Clear
            handleButton(.clear)
        case "%":
            handleButton(.percent)
        default:
            break
        }
    }
}
