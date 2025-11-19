//
//  HistoryView.swift
//  BizCalc
//
//  History tape showing past calculations
//

import SwiftUI

struct HistoryView: View {
    @ObservedObject var viewModel: CalculatorViewModel
    @Environment(\.colorScheme) var colorScheme

    var body: some View {
        VStack(spacing: 0) {
            // Header
            headerView

            Divider()

            // History List
            if viewModel.history.isEmpty {
                emptyStateView
            } else {
                historyListView
            }
        }
        .background(
            VisualEffectBlur(material: .sidebar, blendingMode: .behindWindow)
        )
    }

    // MARK: - Header
    private var headerView: some View {
        HStack {
            Text("History")
                .font(.headline)
                .foregroundColor(.primary)

            Spacer()

            Button(action: {
                copyToClipboard()
            }) {
                Image(systemName: "doc.on.doc")
                    .font(.system(size: 14))
            }
            .buttonStyle(.plain)
            .help("Copy history to clipboard")

            Button(action: {
                viewModel.clearHistory()
            }) {
                Image(systemName: "trash")
                    .font(.system(size: 14))
                    .foregroundColor(.red)
            }
            .buttonStyle(.plain)
            .help("Clear history")
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
    }

    // MARK: - Empty State
    private var emptyStateView: some View {
        VStack(spacing: 12) {
            Image(systemName: "clock.arrow.circlepath")
                .font(.system(size: 40))
                .foregroundColor(.secondary)

            Text("No calculations yet")
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    // MARK: - History List
    private var historyListView: some View {
        ScrollView {
            LazyVStack(spacing: 0) {
                ForEach(viewModel.history) { item in
                    HistoryItemRow(item: item) {
                        viewModel.selectHistoryItem(item)
                    }
                    .padding(.horizontal, 8)
                    .padding(.vertical, 6)

                    Divider()
                        .padding(.leading, 12)
                }
            }
        }
    }

    // MARK: - Actions
    private func copyToClipboard() {
        let text = viewModel.copyHistoryToClipboard()
        let pasteboard = NSPasteboard.general
        pasteboard.clearContents()
        pasteboard.setString(text, forType: .string)
    }
}

// MARK: - History Item Row
struct HistoryItemRow: View {
    let item: HistoryItem
    let onTap: () -> Void
    @State private var isHovered = false

    var body: some View {
        Button(action: onTap) {
            VStack(alignment: .leading, spacing: 4) {
                // Expression
                Text(item.expression)
                    .font(.system(size: 12, weight: .regular, design: .monospaced))
                    .foregroundColor(.secondary)
                    .lineLimit(2)

                // Result
                Text(formatResult(item.result))
                    .font(.system(size: 16, weight: .semibold, design: .rounded))
                    .foregroundColor(.primary)

                // Timestamp
                Text(item.timeString)
                    .font(.system(size: 10))
                    .foregroundColor(.secondary.opacity(0.7))
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(8)
            .background(
                RoundedRectangle(cornerRadius: 8)
                    .fill(isHovered ? Color.accentColor.opacity(0.1) : Color.clear)
            )
        }
        .buttonStyle(.plain)
        .onHover { hovering in
            isHovered = hovering
        }
        .help("Click to use this result")
    }

    private func formatResult(_ value: Double) -> String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        formatter.groupingSeparator = " "
        formatter.maximumFractionDigits = 8
        formatter.minimumFractionDigits = 0
        return formatter.string(from: NSNumber(value: value)) ?? "\(value)"
    }
}

#Preview {
    HistoryView(viewModel: {
        let vm = CalculatorViewModel()
        // Add sample history
        vm.history = [
            HistoryItem(expression: "100 MARGIN 20%", result: 125),
            HistoryItem(expression: "1000 + 500", result: 1500),
            HistoryItem(expression: "200 MARKUP 15%", result: 230),
        ]
        return vm
    }())
    .frame(width: 250, height: 600)
}
