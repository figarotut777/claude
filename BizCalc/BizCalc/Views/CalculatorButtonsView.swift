//
//  CalculatorButtonsView.swift
//  BizCalc
//
//  Calculator buttons with glassmorphism design
//

import SwiftUI

struct CalculatorButtonsView: View {
    @ObservedObject var viewModel: CalculatorViewModel
    @Environment(\.colorScheme) var colorScheme

    // Button layout
    private let columns = Array(repeating: GridItem(.flexible(), spacing: 8), count: 4)

    var body: some View {
        VStack(spacing: 12) {
            // Business Functions Row
            businessFunctionsRow

            Divider()
                .padding(.vertical, 4)

            // Standard Calculator Grid
            standardCalculatorGrid
        }
    }

    // MARK: - Business Functions
    private var businessFunctionsRow: some View {
        HStack(spacing: 8) {
            CalcButton(
                title: "TAX+",
                type: .business,
                colorScheme: colorScheme
            ) {
                viewModel.handleButton(.taxPlus)
            }

            CalcButton(
                title: "TAX−",
                type: .business,
                colorScheme: colorScheme
            ) {
                viewModel.handleButton(.taxMinus)
            }

            CalcButton(
                title: "MARGIN",
                type: .business,
                colorScheme: colorScheme
            ) {
                viewModel.handleButton(.margin)
            }

            CalcButton(
                title: "MARKUP",
                type: .business,
                colorScheme: colorScheme
            ) {
                viewModel.handleButton(.markup)
            }

            CalcButton(
                title: "DISC",
                type: .business,
                colorScheme: colorScheme
            ) {
                viewModel.handleButton(.discount)
            }
        }
        .frame(height: 40)
    }

    // MARK: - Standard Calculator
    private var standardCalculatorGrid: some View {
        VStack(spacing: 8) {
            // Row 1: AC, ±, %, ÷
            HStack(spacing: 8) {
                CalcButton(title: "AC", type: .function, colorScheme: colorScheme) {
                    viewModel.handleButton(.clear)
                }
                CalcButton(title: "±", type: .function, colorScheme: colorScheme) {
                    viewModel.handleButton(.negate)
                }
                CalcButton(title: "%", type: .function, colorScheme: colorScheme) {
                    viewModel.handleButton(.percent)
                }
                CalcButton(title: "÷", type: .operation, colorScheme: colorScheme) {
                    viewModel.handleButton(.operation(.divide))
                }
            }

            // Row 2: 7, 8, 9, ×
            HStack(spacing: 8) {
                CalcButton(title: "7", type: .number, colorScheme: colorScheme) {
                    viewModel.handleButton(.digit(7))
                }
                CalcButton(title: "8", type: .number, colorScheme: colorScheme) {
                    viewModel.handleButton(.digit(8))
                }
                CalcButton(title: "9", type: .number, colorScheme: colorScheme) {
                    viewModel.handleButton(.digit(9))
                }
                CalcButton(title: "×", type: .operation, colorScheme: colorScheme) {
                    viewModel.handleButton(.operation(.multiply))
                }
            }

            // Row 3: 4, 5, 6, −
            HStack(spacing: 8) {
                CalcButton(title: "4", type: .number, colorScheme: colorScheme) {
                    viewModel.handleButton(.digit(4))
                }
                CalcButton(title: "5", type: .number, colorScheme: colorScheme) {
                    viewModel.handleButton(.digit(5))
                }
                CalcButton(title: "6", type: .number, colorScheme: colorScheme) {
                    viewModel.handleButton(.digit(6))
                }
                CalcButton(title: "−", type: .operation, colorScheme: colorScheme) {
                    viewModel.handleButton(.operation(.subtract))
                }
            }

            // Row 4: 1, 2, 3, +
            HStack(spacing: 8) {
                CalcButton(title: "1", type: .number, colorScheme: colorScheme) {
                    viewModel.handleButton(.digit(1))
                }
                CalcButton(title: "2", type: .number, colorScheme: colorScheme) {
                    viewModel.handleButton(.digit(2))
                }
                CalcButton(title: "3", type: .number, colorScheme: colorScheme) {
                    viewModel.handleButton(.digit(3))
                }
                CalcButton(title: "+", type: .operation, colorScheme: colorScheme) {
                    viewModel.handleButton(.operation(.add))
                }
            }

            // Row 5: 0 (wide), ., =
            HStack(spacing: 8) {
                CalcButton(title: "0", type: .number, colorScheme: colorScheme, isWide: true) {
                    viewModel.handleButton(.digit(0))
                }
                CalcButton(title: ".", type: .number, colorScheme: colorScheme) {
                    viewModel.handleButton(.decimal)
                }
                CalcButton(title: "=", type: .equals, colorScheme: colorScheme) {
                    viewModel.handleButton(.equals)
                }
            }
        }
    }
}

// MARK: - Calculator Button Component
struct CalcButton: View {
    let title: String
    let type: ButtonType
    let colorScheme: ColorScheme
    var isWide: Bool = false
    let action: () -> Void

    enum ButtonType {
        case number
        case operation
        case function
        case equals
        case business
    }

    var body: some View {
        Button(action: action) {
            Text(title)
                .font(fontSize)
                .fontWeight(fontWeight)
                .foregroundColor(foregroundColor)
                .frame(maxWidth: .infinity)
                .frame(height: 50)
                .background(buttonBackground)
                .cornerRadius(12)
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(borderColor, lineWidth: 1)
                )
                .shadow(color: shadowColor, radius: 4, x: 0, y: 2)
        }
        .buttonStyle(.plain)
        .if(isWide) { view in
            view.gridCellColumns(2)
        }
    }

    // MARK: - Button Styling
    private var buttonBackground: some View {
        Group {
            switch type {
            case .number:
                Color(nsColor: colorScheme == .dark ? .white.withAlphaComponent(0.15) : .black.withAlphaComponent(0.08))
            case .operation:
                Color.accentColor.opacity(colorScheme == .dark ? 0.5 : 0.6)
            case .function:
                Color.orange.opacity(colorScheme == .dark ? 0.4 : 0.5)
            case .equals:
                Color.green.opacity(colorScheme == .dark ? 0.5 : 0.6)
            case .business:
                Color.blue.opacity(colorScheme == .dark ? 0.4 : 0.5)
            }
        }
    }

    private var foregroundColor: Color {
        switch type {
        case .number:
            return colorScheme == .dark ? .white : .black
        case .operation, .equals, .business:
            return .white
        case .function:
            return .white
        }
    }

    private var borderColor: Color {
        Color.white.opacity(colorScheme == .dark ? 0.2 : 0.3)
    }

    private var shadowColor: Color {
        Color.black.opacity(colorScheme == .dark ? 0.3 : 0.1)
    }

    private var fontSize: Font {
        type == .business ? .system(size: 11, weight: .semibold) : .system(size: 18)
    }

    private var fontWeight: Font.Weight {
        type == .number ? .regular : .semibold
    }
}

// MARK: - View Extension for Conditional Modifiers
extension View {
    @ViewBuilder
    func `if`<Transform: View>(_ condition: Bool, transform: (Self) -> Transform) -> some View {
        if condition {
            transform(self)
        } else {
            self
        }
    }
}

#Preview {
    CalculatorButtonsView(viewModel: CalculatorViewModel())
        .padding()
        .frame(width: 350)
        .background(Color(nsColor: .windowBackgroundColor))
}
