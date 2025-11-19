//
//  ResistanceBar.swift
//  NegotiationDojo
//
//  Visual resistance meter component
//  Created by Claude on 2025-11-19.
//

import SwiftUI

struct ResistanceBar: View {
    let resistance: Int
    let emoji: String

    @State private var animatedResistance: Double = 100

    var body: some View {
        VStack(spacing: 12) {
            // Emoji avatar
            Text(emoji)
                .font(.system(size: 60))
                .shadow(color: .black.opacity(0.3), radius: 5, x: 0, y: 2)

            // Resistance label
            Text("RESISTANCE")
                .font(.caption)
                .fontWeight(.bold)
                .foregroundColor(.white.opacity(0.7))
                .tracking(2)

            // Progress bar
            ZStack(alignment: .leading) {
                // Background
                RoundedRectangle(cornerRadius: 10)
                    .fill(Color.white.opacity(0.2))
                    .frame(width: 200, height: 24)

                // Foreground (resistance level)
                RoundedRectangle(cornerRadius: 10)
                    .fill(
                        LinearGradient(
                            colors: [resistanceColor, resistanceColor.opacity(0.7)],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .frame(width: 200 * (animatedResistance / 100), height: 24)
                    .animation(.spring(response: 0.6, dampingFraction: 0.7), value: animatedResistance)

                // Percentage text
                Text("\(Int(animatedResistance))%")
                    .font(.system(size: 12, weight: .bold))
                    .foregroundColor(.white)
                    .frame(width: 200)
                    .shadow(color: .black.opacity(0.5), radius: 2, x: 0, y: 1)
            }

            // Status text
            Text(statusText)
                .font(.caption2)
                .foregroundColor(resistanceColor)
                .fontWeight(.semibold)
        }
        .padding(20)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.black.opacity(0.3))
                .shadow(color: .black.opacity(0.3), radius: 10, x: 0, y: 5)
        )
        .onChange(of: resistance) { _, newValue in
            animatedResistance = Double(newValue)
        }
        .onAppear {
            animatedResistance = Double(resistance)
        }
    }

    private var resistanceColor: Color {
        switch resistance {
        case 0...30:
            return .green
        case 31...70:
            return .orange
        default:
            return .red
        }
    }

    private var statusText: String {
        switch resistance {
        case 0:
            return "CONVINCED!"
        case 1...20:
            return "Almost there..."
        case 21...40:
            return "Making progress"
        case 41...60:
            return "Skeptical"
        case 61...80:
            return "Very resistant"
        default:
            return "Highly resistant"
        }
    }
}

#Preview {
    ZStack {
        Color.gray
        VStack(spacing: 30) {
            ResistanceBar(resistance: 85, emoji: "👔")
            ResistanceBar(resistance: 50, emoji: "🛍️")
            ResistanceBar(resistance: 15, emoji: "🛋️")
        }
    }
}
