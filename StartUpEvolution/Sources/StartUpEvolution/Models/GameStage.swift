import Foundation

/// Represents different stages of startup evolution
enum GameStage: String, CaseIterable {
    case garage = "Garage Startup"
    case smallOffice = "Small Office"
    case coWorking = "Co-Working Space"
    case midSize = "Mid-size Company"
    case unicorn = "Unicorn Status"

    /// XP required to reach this stage
    var minXP: Int {
        switch self {
        case .garage: return 0
        case .smallOffice: return 51
        case .coWorking: return 151
        case .midSize: return 301
        case .unicorn: return 501
        }
    }

    /// XP required to reach next stage
    var maxXP: Int {
        switch self {
        case .garage: return 50
        case .smallOffice: return 150
        case .coWorking: return 300
        case .midSize: return 500
        case .unicorn: return Int.max
        }
    }

    /// Background color gradient for this stage
    var backgroundColors: (top: String, bottom: String) {
        switch self {
        case .garage:
            return ("#2C3E50", "#34495E") // Dark blue-gray
        case .smallOffice:
            return ("#4A5568", "#718096") // Gray
        case .coWorking:
            return ("#2D3748", "#4A5568") // Dark gray
        case .midSize:
            return ("#1A365D", "#2C5282") // Professional blue
        case .unicorn:
            return ("#1A202C", "#2D3748") // Luxurious dark
        }
    }

    /// DALL-E prompt for logo generation
    var logoPrompt: String {
        switch self {
        case .garage:
            return "A simple, somewhat amateurish, black and white logo for a tech startup. Minimalist icon. Text: 'My App'."
        case .smallOffice:
            return "A slightly more refined, colorful (2-3 colors) logo for a growing tech company. Modern icon. Text: 'My App Co.'."
        case .coWorking:
            return "A professional, sleek, and minimalist logo for a successful tech company. Abstract icon. Text: 'MyApp Solutions'."
        case .midSize:
            return "A sophisticated, premium-looking, vectorized logo for an established technology firm. Elegant icon. Text: 'MyApp Innovations Inc.'."
        case .unicorn:
            return "A highly stylized, iconic, and luxurious logo for a leading global tech unicorn. Abstract and unique symbol. Text: 'MYAPP GLOBAL'."
        }
    }

    /// Get stage from XP value
    static func stage(for xp: Int) -> GameStage {
        for stage in GameStage.allCases.reversed() {
            if xp >= stage.minXP {
                return stage
            }
        }
        return .garage
    }

    /// Get next stage
    var next: GameStage? {
        let allStages = GameStage.allCases
        guard let currentIndex = allStages.firstIndex(of: self),
              currentIndex < allStages.count - 1 else {
            return nil
        }
        return allStages[currentIndex + 1]
    }
}
