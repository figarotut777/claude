//
//  IngredientListView.swift
//  FridgeChef
//
//  Created by Claude on 19/11/2025.
//

import SwiftUI

struct IngredientListView: View {
    @ObservedObject var viewModel: MainViewModel

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Detected Ingredients")
                .font(.title2)
                .fontWeight(.semibold)

            Text("Review the ingredients below. Add missing items or remove incorrect ones.")
                .font(.subheadline)
                .foregroundColor(.secondary)

            // Ingredients List
            ScrollView {
                LazyVStack(spacing: 8) {
                    ForEach(viewModel.detectedIngredients) { ingredient in
                        IngredientRow(ingredient: ingredient) {
                            viewModel.removeIngredient(ingredient)
                        }
                    }

                    if viewModel.detectedIngredients.isEmpty {
                        Text("No ingredients detected")
                            .foregroundColor(.secondary)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 32)
                    }
                }
            }
            .frame(maxHeight: 300)

            Divider()

            // Add New Ingredient
            HStack {
                Image(systemName: "plus.circle.fill")
                    .foregroundColor(.green)

                TextField("Add ingredient...", text: $viewModel.newIngredientName)
                    .textFieldStyle(.roundedBorder)
                    .onSubmit {
                        viewModel.addIngredient()
                    }

                Button("Add") {
                    viewModel.addIngredient()
                }
                .disabled(viewModel.newIngredientName.trimmingCharacters(in: .whitespaces).isEmpty)
            }

            Divider()

            // Actions
            HStack {
                Button("Back") {
                    viewModel.startOver()
                }
                .keyboardShortcut(.cancelAction)

                Spacer()

                Button("Generate Recipes") {
                    Task {
                        await viewModel.generateRecipes()
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(!viewModel.canGenerateRecipes)
                .keyboardShortcut(.defaultAction)
            }
        }
        .padding()
    }
}

// MARK: - Ingredient Row

struct IngredientRow: View {
    let ingredient: Ingredient
    let onRemove: () -> Void

    var body: some View {
        HStack {
            Image(systemName: "leaf.fill")
                .foregroundColor(.green)
                .font(.caption)

            Text(ingredient.name)
                .font(.body)

            Spacer()

            Button(action: onRemove) {
                Image(systemName: "trash")
                    .foregroundColor(.red)
            }
            .buttonStyle(.plain)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(Color.gray.opacity(0.1))
        )
    }
}

// MARK: - Preview

struct IngredientListView_Previews: PreviewProvider {
    static var previews: some View {
        IngredientListView(viewModel: {
            let vm = MainViewModel()
            vm.detectedIngredients = [
                Ingredient(name: "Eggs"),
                Ingredient(name: "Milk"),
                Ingredient(name: "Cheese")
            ]
            return vm
        }())
        .frame(width: 600)
    }
}
