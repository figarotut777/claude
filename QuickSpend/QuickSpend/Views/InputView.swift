//
//  InputView.swift
//  QuickSpend
//
//  Created by Claude on 19.11.2025.
//

import SwiftUI

struct InputView: View {
    @Bindable var viewModel: BudgetViewModel
    @FocusState private var isFocused: Bool

    var body: some View {
        VStack(spacing: 8) {
            HStack(spacing: 12) {
                Image(systemName: "dollarsign.circle.fill")
                    .font(.title2)
                    .foregroundStyle(.blue)

                TextField("500 кофе", text: $viewModel.inputText)
                    .textFieldStyle(.plain)
                    .font(.system(size: 18, weight: .medium))
                    .focused($isFocused)
                    .onChange(of: viewModel.inputText) {
                        viewModel.validateInput()
                    }
                    .onSubmit {
                        submitTransaction()
                    }

                if !viewModel.inputText.isEmpty {
                    Button(action: { viewModel.clearInput() }) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundStyle(.secondary)
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color(nsColor: .controlBackgroundColor))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(isFocused ? Color.blue : Color.clear, lineWidth: 2)
            )

            // Hint text
            if viewModel.inputText.isEmpty {
                HStack {
                    Text("💡 Введите: **сумма категория** (например: 500 кофе)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Spacer()
                }
            } else if viewModel.isInputValid {
                if let parsed = InputParser.parse(text: viewModel.inputText) {
                    HStack(spacing: 4) {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundStyle(.green)

                        Text("→ \(formatAmount(parsed.amount)) · ")
                            .font(.caption)
                            .foregroundStyle(.primary)
                        +
                        Text(parsed.categoryName)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(.blue)

                        if let note = parsed.note {
                            Text(" · \(note)")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }

                        Spacer()
                    }
                }
            }
        }
        .onAppear {
            isFocused = true
        }
    }

    private func submitTransaction() {
        if viewModel.submitTransaction() {
            // Success animation could be added here
        }
    }

    private func formatAmount(_ amount: Double) -> String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        formatter.locale = Locale.current
        return formatter.string(from: NSNumber(value: amount)) ?? "\(amount)"
    }
}
