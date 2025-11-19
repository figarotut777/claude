//
//  ContentView.swift
//  FridgeChef
//
//  Created by Claude on 19/11/2025.
//

import SwiftUI

struct ContentView: View {
    @StateObject private var viewModel = MainViewModel()

    var body: some View {
        NavigationStack {
            ZStack {
                // Background gradient
                LinearGradient(
                    colors: [Color.blue.opacity(0.05), Color.green.opacity(0.05)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .ignoresSafeArea()

                // Main content
                VStack(spacing: 0) {
                    // Header
                    VStack(spacing: 8) {
                        HStack {
                            Image(systemName: "refrigerator")
                                .font(.system(size: 32))
                                .foregroundColor(.blue)

                            Text("FridgeChef")
                                .font(.system(size: 36, weight: .bold, design: .rounded))

                            Spacer()

                            // Mock Data Indicator
                            if APIService.shared.useMockData {
                                HStack(spacing: 4) {
                                    Image(systemName: "exclamationmark.triangle.fill")
                                        .font(.caption)
                                    Text("Using Mock Data")
                                        .font(.caption)
                                }
                                .foregroundColor(.orange)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 6)
                                .background(
                                    Capsule()
                                        .fill(Color.orange.opacity(0.1))
                                )
                            }
                        }

                        Text("AI-Powered Cooking Assistant")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    .padding()

                    Divider()

                    // State-based content
                    ScrollView {
                        stateContent
                            .padding()
                    }
                }
            }
            .frame(minWidth: 700, minHeight: 600)
        }
    }

    @ViewBuilder
    private var stateContent: some View {
        switch viewModel.appState {
        case .idle:
            idleView

        case .analyzingImage:
            loadingView(message: "Analyzing your fridge photo...")

        case .confirmingIngredients:
            IngredientListView(viewModel: viewModel)

        case .generatingRecipes:
            loadingView(message: "Creating delicious recipes...")

        case .showingRecipes:
            RecipeListView(viewModel: viewModel)

        case .error(let message):
            errorView(message: message)
        }
    }

    // MARK: - Idle State (Drop Zone)

    private var idleView: some View {
        VStack(spacing: 24) {
            DropZoneView(image: $viewModel.selectedImage)
                .padding()

            if viewModel.canScan {
                Button(action: {
                    Task {
                        await viewModel.scanIngredients()
                    }
                }) {
                    Label("Scan Ingredients", systemImage: "viewfinder")
                        .font(.headline)
                        .padding(.horizontal, 32)
                        .padding(.vertical, 12)
                }
                .buttonStyle(.borderedProminent)
                .controlSize(.large)
            }

            // Instructions
            VStack(alignment: .leading, spacing: 12) {
                InstructionStep(number: 1, text: "Upload or drag a photo of your fridge")
                InstructionStep(number: 2, text: "AI will identify all ingredients")
                InstructionStep(number: 3, text: "Get 3 recipe suggestions using only those items")
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.gray.opacity(0.05))
            )
        }
    }

    // MARK: - Loading State

    private func loadingView(message: String) -> some View {
        VStack(spacing: 24) {
            ProgressView()
                .scaleEffect(1.5)
                .progressViewStyle(.circular)

            Text(message)
                .font(.headline)
                .foregroundColor(.secondary)

            Text("This may take a few seconds...")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding(64)
    }

    // MARK: - Error State

    private func errorView(message: String) -> some View {
        VStack(spacing: 24) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.system(size: 64))
                .foregroundColor(.red)

            Text("Oops!")
                .font(.title)
                .fontWeight(.bold)

            Text(message)
                .font(.body)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)

            Button("Try Again") {
                viewModel.reset()
            }
            .buttonStyle(.borderedProminent)
        }
        .frame(maxWidth: .infinity)
        .padding(64)
    }
}

// MARK: - Instruction Step

struct InstructionStep: View {
    let number: Int
    let text: String

    var body: some View {
        HStack(spacing: 12) {
            Text("\(number)")
                .font(.headline)
                .fontWeight(.bold)
                .foregroundColor(.white)
                .frame(width: 28, height: 28)
                .background(Circle().fill(Color.blue))

            Text(text)
                .font(.body)
        }
    }
}

// MARK: - Preview

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
