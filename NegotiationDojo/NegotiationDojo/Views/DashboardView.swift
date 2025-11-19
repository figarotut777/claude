//
//  DashboardView.swift
//  NegotiationDojo
//
//  Scenario selection dashboard
//  Created by Claude on 2025-11-19.
//

import SwiftUI

struct DashboardView: View {
    @Binding var selectedScenario: Scenario?
    @Binding var showDashboard: Bool

    var body: some View {
        ZStack {
            // Background gradient
            LinearGradient(
                colors: [Color(red: 0.1, green: 0.1, blue: 0.2), Color(red: 0.2, green: 0.15, blue: 0.3)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            VStack(spacing: 40) {
                // Header
                VStack(spacing: 12) {
                    Text("🥋 Negotiation Dojo")
                        .font(.system(size: 48, weight: .bold))
                        .foregroundColor(.white)

                    Text("Master the Art of Persuasion")
                        .font(.title3)
                        .foregroundColor(.white.opacity(0.7))
                }
                .padding(.top, 60)

                // Scenario Cards
                ScrollView {
                    LazyVGrid(columns: [GridItem(.adaptive(minimum: 300), spacing: 20)], spacing: 20) {
                        ForEach(Scenario.scenarios) { scenario in
                            ScenarioCard(scenario: scenario)
                                .onTapGesture {
                                    selectScenario(scenario)
                                }
                        }
                    }
                    .padding(.horizontal, 40)
                }

                Spacer()
            }
        }
    }

    private func selectScenario(_ scenario: Scenario) {
        selectedScenario = scenario
        withAnimation {
            showDashboard = false
        }
    }
}

// MARK: - Scenario Card
struct ScenarioCard: View {
    let scenario: Scenario

    @State private var isHovered = false

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            // Emoji and Title
            HStack(spacing: 12) {
                Text(scenario.opponentEmoji)
                    .font(.system(size: 40))

                VStack(alignment: .leading, spacing: 4) {
                    Text(scenario.title)
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(.white)

                    Text("vs. \(scenario.opponentName)")
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.7))
                }

                Spacer()
            }

            // Description
            Text(scenario.description)
                .font(.body)
                .foregroundColor(.white.opacity(0.8))
                .lineLimit(2)

            // Difficulty indicator
            HStack {
                Text("Difficulty:")
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.6))

                HStack(spacing: 4) {
                    ForEach(0..<3) { index in
                        Circle()
                            .fill(index < difficultyLevel ? Color.orange : Color.white.opacity(0.3))
                            .frame(width: 8, height: 8)
                    }
                }
            }

            // Start button
            HStack {
                Spacer()
                Text("Begin Training")
                    .font(.headline)
                    .foregroundColor(.white)
                    .padding(.horizontal, 20)
                    .padding(.vertical, 10)
                    .background(
                        RoundedRectangle(cornerRadius: 8)
                            .fill(Color.blue)
                    )
                Spacer()
            }
        }
        .padding(24)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.white.opacity(isHovered ? 0.15 : 0.1))
                .shadow(color: .black.opacity(0.3), radius: isHovered ? 20 : 10, x: 0, y: isHovered ? 10 : 5)
        )
        .scaleEffect(isHovered ? 1.02 : 1.0)
        .animation(.spring(response: 0.3), value: isHovered)
        .onHover { hovering in
            isHovered = hovering
        }
    }

    private var difficultyLevel: Int {
        switch scenario.initialResistance {
        case 0..<60:
            return 1
        case 60..<80:
            return 2
        default:
            return 3
        }
    }
}

#Preview {
    DashboardView(
        selectedScenario: .constant(nil),
        showDashboard: .constant(true)
    )
}
