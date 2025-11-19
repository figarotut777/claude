import SwiftUI

struct ContentView: View {
    @StateObject private var viewModel = GameViewModel()

    var body: some View {
        ZStack {
            // Background gradient
            backgroundGradient

            VStack(spacing: 30) {
                Spacer()

                // Stage title
                Text(viewModel.currentStage.rawValue)
                    .font(.system(size: 36, weight: .bold))
                    .foregroundColor(.white)
                    .shadow(color: .black.opacity(0.3), radius: 10, x: 0, y: 5)

                // Logo placeholder
                logoPlaceholder

                Spacer()

                // Stats section
                statsSection

                // Progress bar
                progressBar

                // Main "Code" button
                codeButton

                Spacer()

                // Debug controls (remove in production)
                debugControls
            }
            .padding(40)

            // CTA Modal overlay
            if viewModel.showCTAModal {
                CTAModalView(viewModel: viewModel)
            }
        }
        .frame(minWidth: 600, minHeight: 700)
    }

    // MARK: - UI Components

    private var backgroundGradient: some View {
        LinearGradient(
            gradient: Gradient(colors: [
                Color(hex: viewModel.currentStage.backgroundColors.top),
                Color(hex: viewModel.currentStage.backgroundColors.bottom)
            ]),
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
        .ignoresSafeArea()
        .animation(.easeInOut(duration: 1.0), value: viewModel.currentStage)
    }

    private var logoPlaceholder: some View {
        ZStack {
            if viewModel.isGeneratingLogo {
                ProgressView()
                    .scaleEffect(2.0)
                    .tint(.white)
            } else {
                RoundedRectangle(cornerRadius: 20)
                    .fill(Color.white.opacity(0.1))
                    .frame(width: 200, height: 200)
                    .overlay(
                        VStack(spacing: 10) {
                            Image(systemName: "photo")
                                .font(.system(size: 60))
                                .foregroundColor(.white.opacity(0.5))
                            Text("Logo Placeholder")
                                .font(.caption)
                                .foregroundColor(.white.opacity(0.5))
                        }
                    )
            }
        }
        .frame(height: 200)
    }

    private var statsSection: some View {
        HStack(spacing: 60) {
            StatView(
                icon: "dollarsign.circle.fill",
                title: "Money",
                value: "$\(viewModel.money)"
            )

            StatView(
                icon: "star.fill",
                title: "Experience",
                value: "\(viewModel.xp) XP"
            )
        }
    }

    private var progressBar: some View {
        VStack(spacing: 8) {
            HStack {
                Text("Progress to Next Level")
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.8))

                Spacer()

                if !viewModel.isMaxLevel {
                    Text("\(viewModel.xpForNextLevel) XP needed")
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.8))
                } else {
                    Text("MAX LEVEL!")
                        .font(.caption)
                        .foregroundColor(.yellow)
                }
            }

            ZStack(alignment: .leading) {
                // Background
                RoundedRectangle(cornerRadius: 10)
                    .fill(Color.white.opacity(0.2))
                    .frame(height: 20)

                // Progress
                RoundedRectangle(cornerRadius: 10)
                    .fill(
                        LinearGradient(
                            gradient: Gradient(colors: [Color.green, Color.blue]),
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .frame(width: progressWidth, height: 20)
                    .animation(.easeInOut(duration: 0.3), value: viewModel.progressToNextLevel)
            }
            .frame(maxWidth: .infinity)
        }
    }

    private var progressWidth: CGFloat {
        // This will be calculated based on the actual width
        return 500 * viewModel.progressToNextLevel
    }

    private var codeButton: some View {
        Button(action: {
            viewModel.onCodeButtonPressed()
        }) {
            Text("< CODE />")
                .font(.system(size: 28, weight: .bold, design: .monospaced))
                .foregroundColor(.white)
                .frame(width: 250, height: 80)
                .background(
                    LinearGradient(
                        gradient: Gradient(colors: [Color.blue, Color.purple]),
                        startPoint: .leading,
                        endPoint: .trailing
                    )
                )
                .cornerRadius(20)
                .shadow(color: .black.opacity(0.3), radius: 10, x: 0, y: 5)
        }
        .buttonStyle(PlainButtonStyle())
        .scaleEffect(viewModel.isMaxLevel ? 1.1 : 1.0)
        .animation(.easeInOut(duration: 0.5).repeatForever(autoreverses: true), value: viewModel.isMaxLevel)
    }

    private var debugControls: some View {
        HStack {
            Button("Add 50 XP") {
                for _ in 0..<50 {
                    viewModel.onCodeButtonPressed()
                }
            }
            .buttonStyle(.bordered)

            Button("Reset Game") {
                viewModel.resetGame()
            }
            .buttonStyle(.bordered)
        }
        .foregroundColor(.white.opacity(0.7))
    }
}

// MARK: - Stat View Component

struct StatView: View {
    let icon: String
    let title: String
    let value: String

    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: icon)
                .font(.system(size: 40))
                .foregroundColor(.yellow)

            Text(title)
                .font(.caption)
                .foregroundColor(.white.opacity(0.7))

            Text(value)
                .font(.system(size: 24, weight: .bold))
                .foregroundColor(.white)
        }
    }
}

// MARK: - CTA Modal View

struct CTAModalView: View {
    @ObservedObject var viewModel: GameViewModel

    var body: some View {
        ZStack {
            // Dark overlay
            Color.black.opacity(0.7)
                .ignoresSafeArea()

            // Modal content
            VStack(spacing: 25) {
                // Celebration icon
                Image(systemName: "sparkles")
                    .font(.system(size: 60))
                    .foregroundColor(.yellow)

                Text("Поздравляем!")
                    .font(.system(size: 36, weight: .bold))
                    .foregroundColor(.white)

                Text("Ваш стартап достиг статуса Единорога!")
                    .font(.system(size: 20))
                    .foregroundColor(.white.opacity(0.9))
                    .multilineTextAlignment(.center)

                Divider()
                    .background(Color.white.opacity(0.3))
                    .padding(.vertical, 10)

                VStack(spacing: 15) {
                    Text("Построить компанию с нуля непросто. Мы знаем, как помочь вашему **реальному** проекту взлететь.")
                        .font(.body)
                        .foregroundColor(.white.opacity(0.9))
                        .multilineTextAlignment(.center)

                    Text("Мы специализируемся на разработке MVP и сложных систем.")
                        .font(.body)
                        .foregroundColor(.white.opacity(0.8))
                        .multilineTextAlignment(.center)
                }
                .padding(.horizontal)

                // CTA Button
                Button(action: {
                    viewModel.openCTALink()
                }) {
                    Text("Узнать, как мы можем помочь")
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 16)
                        .background(
                            LinearGradient(
                                gradient: Gradient(colors: [Color.green, Color.blue]),
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .cornerRadius(12)
                }
                .buttonStyle(PlainButtonStyle())
                .padding(.horizontal)

                // Close button (optional)
                Button("Закрыть") {
                    viewModel.dismissCTA()
                }
                .foregroundColor(.white.opacity(0.6))
            }
            .padding(40)
            .frame(width: 500)
            .background(
                RoundedRectangle(cornerRadius: 20)
                    .fill(Color(hex: "#1A202C"))
                    .shadow(color: .black.opacity(0.5), radius: 20, x: 0, y: 10)
            )
        }
    }
}

// MARK: - Color Extension for Hex Support

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
