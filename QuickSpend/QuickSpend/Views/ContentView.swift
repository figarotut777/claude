//
//  ContentView.swift
//  QuickSpend
//
//  Created by Claude on 19.11.2025.
//

import SwiftUI
import SwiftData
import Charts

struct ContentView: View {
    @Environment(\.modelContext) private var modelContext
    @Query(sort: \Transaction.date, order: .reverse) private var transactions: [Transaction]

    @State private var viewModel: BudgetViewModel?

    var body: some View {
        VStack(spacing: 0) {
            // Header with total
            headerView

            Divider()

            // Main content
            ScrollView {
                VStack(spacing: 24) {
                    // Input field
                    if let vm = viewModel {
                        InputView(viewModel: vm)
                            .padding(.horizontal, 20)
                            .padding(.top, 20)
                    }

                    // Chart
                    if !transactions.isEmpty {
                        chartView
                            .padding(.horizontal, 20)
                    }

                    // Transactions list
                    transactionsList
                }
                .padding(.bottom, 20)
            }
        }
        .frame(minWidth: 600, minHeight: 700)
        .onAppear {
            if viewModel == nil {
                viewModel = BudgetViewModel(modelContext: modelContext)
            }
        }
    }

    // MARK: - Header

    private var headerView: some View {
        VStack(spacing: 8) {
            Text("QuickSpend")
                .font(.title2.weight(.bold))

            HStack(spacing: 4) {
                Text("Траты в этом месяце:")
                    .font(.caption)
                    .foregroundStyle(.secondary)

                Text(formatAmount(monthlyTotal))
                    .font(.title.weight(.bold))
                    .foregroundStyle(.primary)
            }
        }
        .padding(.vertical, 16)
        .frame(maxWidth: .infinity)
        .background(Color(nsColor: .controlBackgroundColor))
    }

    // MARK: - Chart

    private var chartView: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("По категориям")
                .font(.headline)

            if let vm = viewModel {
                let categoryData = vm.categoryTotals(transactions: transactions)

                if !categoryData.isEmpty {
                    Chart(categoryData, id: \.category) { item in
                        SectorMark(
                            angle: .value("Amount", item.amount),
                            innerRadius: .ratio(0.5),
                            angularInset: 2
                        )
                        .foregroundStyle(by: .value("Category", item.category))
                        .cornerRadius(4)
                    }
                    .frame(height: 250)
                    .chartLegend(position: .bottom, spacing: 12)

                    // Category breakdown
                    VStack(spacing: 8) {
                        ForEach(categoryData, id: \.category) { item in
                            HStack {
                                Image(systemName: item.icon)
                                    .foregroundStyle(Color(hex: item.color))
                                    .frame(width: 24)

                                Text(item.category)
                                    .font(.subheadline)

                                Spacer()

                                Text(formatAmount(item.amount))
                                    .font(.subheadline.weight(.semibold))
                                    .foregroundStyle(.secondary)

                                Text("(\(Int((item.amount / monthlyTotal) * 100))%)")
                                    .font(.caption)
                                    .foregroundStyle(.tertiary)
                            }
                            .padding(.vertical, 4)
                        }
                    }
                    .padding(.top, 8)
                }
            }
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color(nsColor: .controlBackgroundColor))
        )
    }

    // MARK: - Transactions List

    private var transactionsList: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("История")
                    .font(.headline)

                Spacer()

                Text("\(transactions.count) записей")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            .padding(.horizontal, 20)

            if transactions.isEmpty {
                emptyStateView
            } else {
                LazyVStack(spacing: 0) {
                    ForEach(groupedTransactions, id: \.key) { group in
                        Section {
                            ForEach(group.value) { transaction in
                                TransactionRow(transaction: transaction)
                                    .contentShape(Rectangle())
                                    .swipeActions(edge: .trailing, allowsFullSwipe: true) {
                                        Button(role: .destructive) {
                                            viewModel?.deleteTransaction(transaction)
                                        } label: {
                                            Label("Delete", systemImage: "trash")
                                        }
                                    }
                            }
                        } header: {
                            Text(group.key)
                                .font(.subheadline.weight(.semibold))
                                .foregroundStyle(.secondary)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .padding(.horizontal, 20)
                                .padding(.vertical, 8)
                                .background(Color(nsColor: .windowBackgroundColor))
                        }
                    }
                }
            }
        }
    }

    private var emptyStateView: some View {
        VStack(spacing: 12) {
            Image(systemName: "tray")
                .font(.system(size: 48))
                .foregroundStyle(.tertiary)

            Text("Нет транзакций")
                .font(.headline)
                .foregroundStyle(.secondary)

            Text("Начните вводить расходы выше")
                .font(.caption)
                .foregroundStyle(.tertiary)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 60)
    }

    // MARK: - Helpers

    private var monthlyTotal: Double {
        guard let vm = viewModel else { return 0 }
        return vm.totalThisMonth(transactions: transactions)
    }

    private var groupedTransactions: [(key: String, value: [Transaction])] {
        let grouped = Dictionary(grouping: transactions) { transaction in
            formatDate(transaction.date)
        }
        return grouped.sorted { $0.key > $1.key }
    }

    private func formatAmount(_ amount: Double) -> String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        formatter.locale = Locale.current
        return formatter.string(from: NSNumber(value: amount)) ?? "\(amount)"
    }

    private func formatDate(_ date: Date) -> String {
        let calendar = Calendar.current
        let now = Date()

        if calendar.isDateInToday(date) {
            return "Сегодня"
        } else if calendar.isDateInYesterday(date) {
            return "Вчера"
        } else {
            let formatter = DateFormatter()
            formatter.dateFormat = "d MMMM"
            formatter.locale = Locale(identifier: "ru_RU")
            return formatter.string(from: date)
        }
    }
}

// MARK: - Transaction Row

struct TransactionRow: View {
    let transaction: Transaction

    var body: some View {
        HStack(spacing: 12) {
            // Category icon
            ZStack {
                Circle()
                    .fill(Color(hex: transaction.category?.colorHex ?? "#007AFF").opacity(0.15))
                    .frame(width: 40, height: 40)

                Image(systemName: transaction.category?.icon ?? "cart")
                    .foregroundStyle(Color(hex: transaction.category?.colorHex ?? "#007AFF"))
            }

            // Details
            VStack(alignment: .leading, spacing: 4) {
                Text(transaction.category?.name ?? "Uncategorized")
                    .font(.subheadline.weight(.medium))

                if let note = transaction.note {
                    Text(note)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                Text(formatTime(transaction.date))
                    .font(.caption2)
                    .foregroundStyle(.tertiary)
            }

            Spacer()

            // Amount
            Text(formatAmount(transaction.amount))
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.primary)
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 12)
        .background(Color(nsColor: .controlBackgroundColor))
    }

    private func formatAmount(_ amount: Double) -> String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        formatter.locale = Locale.current
        return formatter.string(from: NSNumber(value: amount)) ?? "\(amount)"
    }

    private func formatTime(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}

// MARK: - Color Extension

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (255, 0, 0, 0)
        }

        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue:  Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}
