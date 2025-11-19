//
//  ContentView.swift
//  BizCalc
//
//  Main calculator interface
//

import SwiftUI

struct ContentView: View {
    @StateObject private var viewModel = CalculatorViewModel()
    @Environment(\.colorScheme) var colorScheme

    var body: some View {
        HStack(spacing: 0) {
            // Calculator Section
            VStack(spacing: 0) {
                // Display
                displayView
                    .padding()

                // Calculator Buttons
                CalculatorButtonsView(viewModel: viewModel)
                    .padding(.horizontal)
                    .padding(.bottom)
            }
            .frame(minWidth: 320, maxWidth: 400)

            // History Panel
            if viewModel.showHistory {
                Divider()
                HistoryView(viewModel: viewModel)
                    .frame(width: 250)
            }
        }
        .frame(minWidth: 320, minHeight: 550)
        .background(
            VisualEffectBlur(material: .sidebar, blendingMode: .behindWindow)
        )
        .onAppear {
            // Configure window appearance
            if let window = NSApplication.shared.windows.first {
                window.titlebarAppearsTransparent = true
                window.isMovableByWindowBackground = true
            }
        }
    }

    // MARK: - Display View
    private var displayView: some View {
        VStack(alignment: .trailing, spacing: 4) {
            // Operation indicator
            if viewModel.engine.currentOperation != .none {
                Text(viewModel.engine.getOperationString())
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, alignment: .trailing)
            }

            // Main display
            Text(viewModel.engine.display)
                .font(.system(size: 48, weight: .light, design: .rounded))
                .lineLimit(1)
                .minimumScaleFactor(0.5)
                .frame(maxWidth: .infinity, alignment: .trailing)
                .padding(.horizontal, 8)
                .frame(height: 80)
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color(nsColor: colorScheme == .dark ? .black.withAlphaComponent(0.3) : .white.withAlphaComponent(0.5)))
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(Color.white.opacity(0.2), lineWidth: 1)
                )
        )
    }
}

// MARK: - Visual Effect Blur
struct VisualEffectBlur: NSViewRepresentable {
    var material: NSVisualEffectView.Material
    var blendingMode: NSVisualEffectView.BlendingMode

    func makeNSView(context: Context) -> NSVisualEffectView {
        let view = NSVisualEffectView()
        view.material = material
        view.blendingMode = blendingMode
        view.state = .active
        return view
    }

    func updateNSView(_ nsView: NSVisualEffectView, context: Context) {
        nsView.material = material
        nsView.blendingMode = blendingMode
    }
}

#Preview {
    ContentView()
        .frame(width: 600, height: 600)
}
