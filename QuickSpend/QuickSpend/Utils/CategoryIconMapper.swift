//
//  CategoryIconMapper.swift
//  QuickSpend
//
//  Created by Claude on 19.11.2025.
//

import Foundation

/// Maps category names to appropriate SF Symbol icons
final class CategoryIconMapper {

    /// Returns appropriate SF Symbol name based on category name
    static func icon(for categoryName: String) -> String {
        let lowercased = categoryName.lowercased()

        // Food & Drinks
        if lowercased.contains("еда") || lowercased.contains("food") {
            return "fork.knife"
        }
        if lowercased.contains("кофе") || lowercased.contains("coffee") {
            return "cup.and.saucer.fill"
        }
        if lowercased.contains("ресторан") || lowercased.contains("restaurant") {
            return "fork.knife.circle.fill"
        }
        if lowercased.contains("продукты") || lowercased.contains("groceries") {
            return "cart.fill"
        }

        // Transport
        if lowercased.contains("такси") || lowercased.contains("taxi") {
            return "car.fill"
        }
        if lowercased.contains("транспорт") || lowercased.contains("transport") {
            return "car"
        }
        if lowercased.contains("метро") || lowercased.contains("metro") || lowercased.contains("subway") {
            return "tram.fill"
        }
        if lowercased.contains("бензин") || lowercased.contains("fuel") || lowercased.contains("gas") {
            return "fuelpump.fill"
        }

        // Entertainment
        if lowercased.contains("развлечения") || lowercased.contains("entertainment") {
            return "party.popper.fill"
        }
        if lowercased.contains("кино") || lowercased.contains("cinema") || lowercased.contains("movie") {
            return "film.fill"
        }
        if lowercased.contains("игры") || lowercased.contains("games") {
            return "gamecontroller.fill"
        }

        // Shopping
        if lowercased.contains("покупки") || lowercased.contains("shopping") {
            return "bag.fill"
        }
        if lowercased.contains("одежда") || lowercased.contains("clothes") {
            return "tshirt.fill"
        }
        if lowercased.contains("техника") || lowercased.contains("electronics") {
            return "laptopcomputer"
        }

        // Health & Fitness
        if lowercased.contains("здоровье") || lowercased.contains("health") {
            return "heart.fill"
        }
        if lowercased.contains("аптека") || lowercased.contains("pharmacy") {
            return "cross.case.fill"
        }
        if lowercased.contains("спорт") || lowercased.contains("fitness") || lowercased.contains("gym") {
            return "figure.run"
        }

        // Bills & Utilities
        if lowercased.contains("счета") || lowercased.contains("bills") {
            return "doc.text.fill"
        }
        if lowercased.contains("интернет") || lowercased.contains("internet") {
            return "wifi"
        }
        if lowercased.contains("телефон") || lowercased.contains("phone") {
            return "phone.fill"
        }

        // Education
        if lowercased.contains("образование") || lowercased.contains("education") {
            return "book.fill"
        }

        // Home
        if lowercased.contains("дом") || lowercased.contains("home") {
            return "house.fill"
        }

        // Beauty
        if lowercased.contains("красота") || lowercased.contains("beauty") {
            return "sparkles"
        }

        // Gifts
        if lowercased.contains("подарки") || lowercased.contains("gifts") {
            return "gift.fill"
        }

        // Default
        return "cart"
    }

    /// Returns all available category presets with icons
    static var presets: [(name: String, icon: String)] {
        return [
            ("Еда", "fork.knife"),
            ("Кофе", "cup.and.saucer.fill"),
            ("Такси", "car.fill"),
            ("Транспорт", "car"),
            ("Развлечения", "party.popper.fill"),
            ("Покупки", "bag.fill"),
            ("Здоровье", "heart.fill"),
            ("Спорт", "figure.run"),
            ("Счета", "doc.text.fill"),
            ("Образование", "book.fill"),
            ("Дом", "house.fill"),
            ("Uncategorized", "cart")
        ]
    }
}
