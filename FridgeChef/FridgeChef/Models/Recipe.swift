//
//  Recipe.swift
//  FridgeChef
//
//  Created by Claude on 19/11/2025.
//

import Foundation

struct Recipe: Identifiable, Codable, Equatable {
    let id: UUID
    var title: String
    var cookingTime: String
    var description: String?
    var ingredients: [String]
    var instructions: [String]

    init(
        id: UUID = UUID(),
        title: String,
        cookingTime: String,
        description: String? = nil,
        ingredients: [String],
        instructions: [String]
    ) {
        self.id = id
        self.title = title
        self.cookingTime = cookingTime
        self.description = description
        self.ingredients = ingredients
        self.instructions = instructions
    }
}
