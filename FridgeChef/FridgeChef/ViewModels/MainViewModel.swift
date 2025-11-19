//
//  MainViewModel.swift
//  FridgeChef
//
//  Created by Claude on 19/11/2025.
//

import Foundation
import AppKit
import SwiftUI

enum AppState {
    case idle
    case analyzingImage
    case confirmingIngredients
    case generatingRecipes
    case showingRecipes
    case error(String)
}

@MainActor
class MainViewModel: ObservableObject {
    @Published var selectedImage: NSImage?
    @Published var appState: AppState = .idle
    @Published var detectedIngredients: [Ingredient] = []
    @Published var generatedRecipes: [Recipe] = []
    @Published var newIngredientName: String = ""

    private let apiService = APIService.shared

    // MARK: - Image Analysis

    func scanIngredients() async {
        guard let image = selectedImage else { return }

        appState = .analyzingImage

        do {
            let ingredientNames = try await apiService.analyzeImage(image: image)
            detectedIngredients = ingredientNames.map { Ingredient(name: $0) }
            appState = .confirmingIngredients
        } catch {
            appState = .error("Failed to analyze image: \(error.localizedDescription)")
        }
    }

    // MARK: - Ingredient Management

    func addIngredient() {
        let trimmed = newIngredientName.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }

        // Check if ingredient already exists
        if !detectedIngredients.contains(where: { $0.name.lowercased() == trimmed.lowercased() }) {
            detectedIngredients.append(Ingredient(name: trimmed))
        }

        newIngredientName = ""
    }

    func removeIngredient(_ ingredient: Ingredient) {
        detectedIngredients.removeAll { $0.id == ingredient.id }
    }

    func removeIngredients(at offsets: IndexSet) {
        detectedIngredients.remove(atOffsets: offsets)
    }

    // MARK: - Recipe Generation

    func generateRecipes() async {
        guard !detectedIngredients.isEmpty else {
            appState = .error("Please add at least one ingredient")
            return
        }

        appState = .generatingRecipes

        do {
            let ingredientNames = detectedIngredients.map { $0.name }
            generatedRecipes = try await apiService.generateRecipes(ingredients: ingredientNames)
            appState = .showingRecipes
        } catch {
            appState = .error("Failed to generate recipes: \(error.localizedDescription)")
        }
    }

    // MARK: - State Management

    func reset() {
        selectedImage = nil
        appState = .idle
        detectedIngredients = []
        generatedRecipes = []
        newIngredientName = ""
    }

    func startOver() {
        selectedImage = nil
        appState = .idle
        detectedIngredients = []
        generatedRecipes = []
    }

    var isLoading: Bool {
        if case .analyzingImage = appState { return true }
        if case .generatingRecipes = appState { return true }
        return false
    }

    var canScan: Bool {
        return selectedImage != nil && appState == .idle
    }

    var canGenerateRecipes: Bool {
        return !detectedIngredients.isEmpty && appState == .confirmingIngredients
    }
}
