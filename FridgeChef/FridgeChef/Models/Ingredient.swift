//
//  Ingredient.swift
//  FridgeChef
//
//  Created by Claude on 19/11/2025.
//

import Foundation

struct Ingredient: Identifiable, Codable, Equatable {
    let id: UUID
    var name: String

    init(id: UUID = UUID(), name: String) {
        self.id = id
        self.name = name
    }
}
