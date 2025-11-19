import Foundation
import Combine
import SwiftUI

/// Main game logic controller
@MainActor
class GameViewModel: ObservableObject {
    // MARK: - Published Properties

    @Published var money: Int = 0
    @Published var xp: Int = 0
    @Published var currentStage: GameStage = .garage
    @Published var currentLogoPath: String?
    @Published var showCTAModal: Bool = false
    @Published var isGeneratingLogo: Bool = false

    // MARK: - UserDefaults Keys

    private enum Keys {
        static let money = "game_money"
        static let xp = "game_xp"
        static let currentStage = "game_current_stage"
        static let currentLogoPath = "game_logo_path"
        static let hasShownCTA = "game_has_shown_cta"
    }

    private var hasShownCTA: Bool = false

    // MARK: - Computed Properties

    /// Progress to next level (0.0 to 1.0)
    var progressToNextLevel: Double {
        let currentMin = currentStage.minXP
        let currentMax = currentStage.maxXP

        guard currentMax != Int.max else { return 1.0 }

        let progress = Double(xp - currentMin) / Double(currentMax - currentMin)
        return min(max(progress, 0.0), 1.0)
    }

    /// XP needed for next level
    var xpForNextLevel: Int {
        return currentStage.maxXP - xp
    }

    /// Is max level reached
    var isMaxLevel: Bool {
        return currentStage == .unicorn
    }

    // MARK: - Initialization

    init() {
        loadGameState()
    }

    // MARK: - Game Actions

    /// Main action: clicking the "Code" button
    func onCodeButtonPressed() {
        money += 1
        xp += 1

        checkForStageProgression()
        saveGameState()

        // Play click sound (will implement in Phase 4)
        // SoundManager.shared.playClick()
    }

    /// Check if player has progressed to a new stage
    private func checkForStageProgression() {
        let newStage = GameStage.stage(for: xp)

        if newStage != currentStage {
            currentStage = newStage
            onStageChanged()
        }

        // Check for CTA trigger (Unicorn Status reached)
        if currentStage == .unicorn && !hasShownCTA {
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) { [weak self] in
                self?.showCTAModal = true
                self?.hasShownCTA = true
                self?.saveGameState()
            }
        }
    }

    /// Called when stage changes
    private func onStageChanged() {
        print("🎉 Stage changed to: \(currentStage.rawValue)")
        // In Phase 2, we'll trigger logo generation here
        // generateNewLogo()
    }

    // MARK: - Persistence (UserDefaults)

    /// Save game state to UserDefaults
    func saveGameState() {
        let defaults = UserDefaults.standard
        defaults.set(money, forKey: Keys.money)
        defaults.set(xp, forKey: Keys.xp)
        defaults.set(currentStage.rawValue, forKey: Keys.currentStage)
        defaults.set(currentLogoPath, forKey: Keys.currentLogoPath)
        defaults.set(hasShownCTA, forKey: Keys.hasShownCTA)
    }

    /// Load game state from UserDefaults
    func loadGameState() {
        let defaults = UserDefaults.standard

        money = defaults.integer(forKey: Keys.money)
        xp = defaults.integer(forKey: Keys.xp)
        hasShownCTA = defaults.bool(forKey: Keys.hasShownCTA)

        if let stageString = defaults.string(forKey: Keys.currentStage),
           let stage = GameStage(rawValue: stageString) {
            currentStage = stage
        } else {
            currentStage = GameStage.stage(for: xp)
        }

        currentLogoPath = defaults.string(forKey: Keys.currentLogoPath)

        print("📱 Game loaded: $\(money), \(xp)XP, \(currentStage.rawValue)")
    }

    /// Reset game to initial state
    func resetGame() {
        money = 0
        xp = 0
        currentStage = .garage
        currentLogoPath = nil
        hasShownCTA = false
        showCTAModal = false

        saveGameState()
        print("🔄 Game reset")
    }

    // MARK: - CTA Actions

    /// Open CTA URL in browser
    func openCTALink() {
        // Replace with your actual URL
        let urlString = "https://your-website.com/contact"

        if let url = URL(string: urlString) {
            NSWorkspace.shared.open(url)
        }
    }

    /// Dismiss CTA modal
    func dismissCTA() {
        showCTAModal = false
    }
}
