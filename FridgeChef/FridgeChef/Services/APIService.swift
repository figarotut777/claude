//
//  APIService.swift
//  FridgeChef
//
//  Created by Claude on 19/11/2025.
//

import Foundation
import AppKit

enum APIError: Error {
    case invalidImage
    case networkError(String)
    case decodingError
    case apiKeyMissing
}

enum AIProvider {
    case openAI
    case anthropic
}

class APIService: ObservableObject {
    static let shared = APIService()

    @Published var useMockData: Bool = true  // Set to false when ready to use real API
    private var apiKey: String?
    private let provider: AIProvider = .openAI

    private init() {
        // Load API key from UserDefaults
        self.apiKey = UserDefaults.standard.string(forKey: "api_key")
    }

    // MARK: - Public Methods

    /// Analyze image to detect ingredients
    func analyzeImage(image: NSImage) async throws -> [String] {
        if useMockData {
            return getMockIngredients()
        }

        guard apiKey != nil else {
            throw APIError.apiKeyMissing
        }

        let base64Image = try convertImageToBase64(image: image)

        switch provider {
        case .openAI:
            return try await analyzeWithOpenAI(base64Image: base64Image)
        case .anthropic:
            return try await analyzeWithAnthropic(base64Image: base64Image)
        }
    }

    /// Generate recipes based on ingredients
    func generateRecipes(ingredients: [String]) async throws -> [Recipe] {
        if useMockData {
            return getMockRecipes(for: ingredients)
        }

        guard apiKey != nil else {
            throw APIError.apiKeyMissing
        }

        switch provider {
        case .openAI:
            return try await generateRecipesWithOpenAI(ingredients: ingredients)
        case .anthropic:
            return try await generateRecipesWithAnthropic(ingredients: ingredients)
        }
    }

    // MARK: - Image Processing

    /// Convert NSImage to Base64 string (with compression to max 1024px)
    func convertImageToBase64(image: NSImage) throws -> String {
        // Resize image to max 1024px
        let resizedImage = resizeImage(image: image, maxDimension: 1024)

        // Convert to JPEG data
        guard let tiffData = resizedImage.tiffRepresentation,
              let bitmapImage = NSBitmapImageRep(data: tiffData),
              let jpegData = bitmapImage.representation(using: .jpeg, properties: [.compressionFactor: 0.8]) else {
            throw APIError.invalidImage
        }

        return jpegData.base64EncodedString()
    }

    private func resizeImage(image: NSImage, maxDimension: CGFloat) -> NSImage {
        let size = image.size
        let ratio = min(maxDimension / size.width, maxDimension / size.height)

        if ratio >= 1 {
            return image  // No need to resize
        }

        let newSize = NSSize(width: size.width * ratio, height: size.height * ratio)
        let newImage = NSImage(size: newSize)

        newImage.lockFocus()
        image.draw(in: NSRect(origin: .zero, size: newSize),
                   from: NSRect(origin: .zero, size: size),
                   operation: .copy,
                   fraction: 1.0)
        newImage.unlockFocus()

        return newImage
    }

    // MARK: - OpenAI API

    private func analyzeWithOpenAI(base64Image: String) async throws -> [String] {
        // TODO: Implement real OpenAI Vision API call
        // Endpoint: https://api.openai.com/v1/chat/completions
        // Model: gpt-4o
        throw APIError.networkError("Not implemented yet")
    }

    private func generateRecipesWithOpenAI(ingredients: [String]) async throws -> [Recipe] {
        // TODO: Implement real OpenAI API call
        throw APIError.networkError("Not implemented yet")
    }

    // MARK: - Anthropic API

    private func analyzeWithAnthropic(base64Image: String) async throws -> [String] {
        // TODO: Implement real Anthropic Vision API call
        // Endpoint: https://api.anthropic.com/v1/messages
        // Model: claude-3-5-sonnet-20241022
        throw APIError.networkError("Not implemented yet")
    }

    private func generateRecipesWithAnthropic(ingredients: [String]) async throws -> [Recipe] {
        // TODO: Implement real Anthropic API call
        throw APIError.networkError("Not implemented yet")
    }

    // MARK: - Mock Data

    private func getMockIngredients() -> [String] {
        // Simulate network delay
        Thread.sleep(forTimeInterval: 1.0)

        return [
            "Eggs",
            "Milk",
            "Cheddar Cheese",
            "Tomatoes",
            "Onion",
            "Butter",
            "Spinach",
            "Chicken Breast"
        ]
    }

    private func getMockRecipes(for ingredients: [String]) -> [Recipe] {
        // Simulate network delay
        Thread.sleep(forTimeInterval: 1.5)

        return [
            Recipe(
                title: "Cheesy Spinach Omelet",
                cookingTime: "15 min",
                description: "A fluffy omelet packed with spinach and melted cheese",
                ingredients: [
                    "3 Eggs",
                    "50g Cheddar Cheese (grated)",
                    "1 cup Spinach",
                    "1 tbsp Butter",
                    "Salt and Pepper"
                ],
                instructions: [
                    "Beat eggs in a bowl with salt and pepper",
                    "Heat butter in a pan over medium heat",
                    "Add spinach and cook until wilted, then remove",
                    "Pour eggs into pan, cook until almost set",
                    "Add spinach and cheese to one half",
                    "Fold omelet and cook for 1 more minute",
                    "Serve hot"
                ]
            ),
            Recipe(
                title: "Chicken & Tomato Skillet",
                cookingTime: "25 min",
                description: "Tender chicken breast cooked with fresh tomatoes and onions",
                ingredients: [
                    "2 Chicken Breasts",
                    "2 Tomatoes (diced)",
                    "1 Onion (sliced)",
                    "2 tbsp Oil",
                    "Salt and Pepper"
                ],
                instructions: [
                    "Season chicken with salt and pepper",
                    "Heat oil in a large skillet over medium-high heat",
                    "Cook chicken for 6-7 minutes per side, then remove",
                    "In the same pan, sauté onion until soft",
                    "Add tomatoes and cook for 5 minutes",
                    "Return chicken to pan, simmer for 5 minutes",
                    "Serve with the tomato sauce"
                ]
            ),
            Recipe(
                title: "Creamy Cheese & Egg Bowl",
                cookingTime: "10 min",
                description: "Quick and satisfying breakfast bowl",
                ingredients: [
                    "2 Eggs",
                    "1/4 cup Milk",
                    "100g Cheddar Cheese (cubed)",
                    "1 tbsp Butter",
                    "Salt and Pepper"
                ],
                instructions: [
                    "Whisk eggs with milk, salt, and pepper",
                    "Melt butter in a pan over low heat",
                    "Pour in egg mixture",
                    "Stir gently as eggs cook",
                    "When almost set, add cheese cubes",
                    "Remove from heat and let cheese melt",
                    "Serve immediately"
                ]
            )
        ]
    }

    // MARK: - API Key Management

    func setAPIKey(_ key: String) {
        self.apiKey = key
        UserDefaults.standard.set(key, forKey: "api_key")
    }

    func hasAPIKey() -> Bool {
        return apiKey != nil && !apiKey!.isEmpty
    }
}
