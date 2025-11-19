//
//  RecipeListView.swift
//  FridgeChef
//
//  Created by Claude on 19/11/2025.
//

import SwiftUI

struct RecipeListView: View {
    @ObservedObject var viewModel: MainViewModel
    @State private var selectedRecipe: Recipe?

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                VStack(alignment: .leading) {
                    Text("Your Recipes")
                        .font(.title2)
                        .fontWeight(.semibold)

                    Text("\(viewModel.generatedRecipes.count) recipes based on your ingredients")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }

                Spacer()

                Button("Start Over") {
                    viewModel.reset()
                }
            }

            ScrollView {
                LazyVStack(spacing: 16) {
                    ForEach(viewModel.generatedRecipes) { recipe in
                        RecipeCard(recipe: recipe)
                            .onTapGesture {
                                selectedRecipe = recipe
                            }
                    }
                }
            }
        }
        .padding()
        .sheet(item: $selectedRecipe) { recipe in
            RecipeDetailView(recipe: recipe)
        }
    }
}

// MARK: - Recipe Card

struct RecipeCard: View {
    let recipe: Recipe

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(recipe.title)
                        .font(.headline)
                        .fontWeight(.semibold)

                    if let description = recipe.description {
                        Text(description)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .lineLimit(2)
                    }
                }

                Spacer()

                HStack(spacing: 4) {
                    Image(systemName: "clock")
                        .font(.caption)
                    Text(recipe.cookingTime)
                        .font(.caption)
                        .fontWeight(.medium)
                }
                .foregroundColor(.blue)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(
                    Capsule()
                        .fill(Color.blue.opacity(0.1))
                )
            }

            Divider()

            HStack {
                Label("\(recipe.ingredients.count) ingredients", systemImage: "list.bullet")
                    .font(.caption)
                    .foregroundColor(.secondary)

                Spacer()

                Label("\(recipe.instructions.count) steps", systemImage: "list.number")
                    .font(.caption)
                    .foregroundColor(.secondary)

                Spacer()

                Image(systemName: "chevron.right")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.gray.opacity(0.05))
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .strokeBorder(Color.gray.opacity(0.2), lineWidth: 1)
                )
        )
        .contentShape(Rectangle())
    }
}

// MARK: - Recipe Detail View

struct RecipeDetailView: View {
    let recipe: Recipe
    @Environment(\.dismiss) var dismiss
    @State private var isSaved = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                // Header
                HStack {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(recipe.title)
                            .font(.largeTitle)
                            .fontWeight(.bold)

                        if let description = recipe.description {
                            Text(description)
                                .font(.body)
                                .foregroundColor(.secondary)
                        }

                        HStack(spacing: 16) {
                            Label(recipe.cookingTime, systemImage: "clock")
                                .font(.subheadline)
                                .foregroundColor(.blue)

                            Label("\(recipe.ingredients.count) ingredients", systemImage: "leaf")
                                .font(.subheadline)
                                .foregroundColor(.green)
                        }
                    }

                    Spacer()

                    Button(action: { isSaved.toggle() }) {
                        Image(systemName: isSaved ? "heart.fill" : "heart")
                            .font(.title2)
                            .foregroundColor(isSaved ? .red : .gray)
                    }
                    .buttonStyle(.plain)
                }

                Divider()

                // Ingredients
                VStack(alignment: .leading, spacing: 12) {
                    Text("Ingredients")
                        .font(.title2)
                        .fontWeight(.semibold)

                    VStack(alignment: .leading, spacing: 8) {
                        ForEach(Array(recipe.ingredients.enumerated()), id: \.offset) { index, ingredient in
                            HStack(alignment: .top) {
                                Image(systemName: "circle.fill")
                                    .font(.system(size: 6))
                                    .foregroundColor(.blue)
                                    .padding(.top, 6)

                                Text(ingredient)
                                    .font(.body)
                            }
                        }
                    }
                }

                Divider()

                // Instructions
                VStack(alignment: .leading, spacing: 12) {
                    Text("Instructions")
                        .font(.title2)
                        .fontWeight(.semibold)

                    VStack(alignment: .leading, spacing: 16) {
                        ForEach(Array(recipe.instructions.enumerated()), id: \.offset) { index, step in
                            HStack(alignment: .top, spacing: 12) {
                                Text("\(index + 1)")
                                    .font(.headline)
                                    .fontWeight(.bold)
                                    .foregroundColor(.white)
                                    .frame(width: 32, height: 32)
                                    .background(Circle().fill(Color.blue))

                                Text(step)
                                    .font(.body)
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                        }
                    }
                }

                Spacer()

                // Action Buttons
                HStack {
                    Button("Close") {
                        dismiss()
                    }
                    .keyboardShortcut(.cancelAction)

                    Spacer()

                    Button(isSaved ? "Saved ✓" : "Save to Favorites") {
                        isSaved.toggle()
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(isSaved)
                }
            }
            .padding(32)
        }
        .frame(minWidth: 600, minHeight: 700)
    }
}

// MARK: - Preview

struct RecipeListView_Previews: PreviewProvider {
    static var previews: some View {
        RecipeListView(viewModel: {
            let vm = MainViewModel()
            vm.generatedRecipes = [
                Recipe(
                    title: "Test Recipe",
                    cookingTime: "15 min",
                    description: "A test recipe",
                    ingredients: ["Eggs", "Milk"],
                    instructions: ["Step 1", "Step 2"]
                )
            ]
            return vm
        }())
        .frame(width: 800, height: 600)
    }
}
