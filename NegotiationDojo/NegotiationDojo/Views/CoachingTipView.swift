//
//  CoachingTipView.swift
//  NegotiationDojo
//
//  Live coaching tips display
//  Created by Claude on 2025-11-19.
//

import SwiftUI

struct CoachingTipView: View {
    let tip: CoachingTip

    @State private var isVisible = false

    var body: some View {
        HStack(spacing: 12) {
            // Coach icon
            Image(systemName: "brain.head.profile")
                .font(.title2)
                .foregroundColor(.yellow)

            VStack(alignment: .leading, spacing: 4) {
                Text("Coach's Insight")
                    .font(.caption)
                    .fontWeight(.bold)
                    .foregroundColor(.yellow)

                Text(tip.content)
                    .font(.body)
                    .foregroundColor(.white)
                    .fixedSize(horizontal: false, vertical: true)
            }

            Spacer()
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.purple.opacity(0.9))
                .shadow(color: .purple.opacity(0.5), radius: 10, x: 0, y: 5)
        )
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color.yellow.opacity(0.5), lineWidth: 1)
        )
        .padding(.horizontal, 20)
        .scaleEffect(isVisible ? 1.0 : 0.8)
        .opacity(isVisible ? 1.0 : 0.0)
        .offset(y: isVisible ? 0 : 20)
        .animation(.spring(response: 0.5, dampingFraction: 0.7), value: isVisible)
        .onAppear {
            withAnimation {
                isVisible = true
            }
        }
    }
}

#Preview {
    ZStack {
        Color.gray
        VStack {
            Spacer()
            CoachingTipView(tip: CoachingTip(content: "Great use of data! Back it up with more specific examples."))
        }
    }
}
