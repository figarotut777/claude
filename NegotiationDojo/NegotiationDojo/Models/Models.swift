//
//  Models.swift
//  NegotiationDojo
//
//  Created by Claude on 2025-11-19.
//

import Foundation

// MARK: - Scenario
struct Scenario: Identifiable, Codable {
    let id: UUID
    let title: String
    let description: String
    let opponentName: String
    let opponentPersona: String
    let opponentEmoji: String
    let initialResistance: Int
    let systemPrompt: String

    init(
        id: UUID = UUID(),
        title: String,
        description: String,
        opponentName: String,
        opponentPersona: String,
        opponentEmoji: String,
        initialResistance: Int = 80,
        systemPrompt: String
    ) {
        self.id = id
        self.title = title
        self.description = description
        self.opponentName = opponentName
        self.opponentPersona = opponentPersona
        self.opponentEmoji = opponentEmoji
        self.initialResistance = initialResistance
        self.systemPrompt = systemPrompt
    }
}

// MARK: - Predefined Scenarios
extension Scenario {
    static let scenarios: [Scenario] = [
        Scenario(
            title: "Ask for a Raise",
            description: "Negotiate a salary increase with your skeptical boss",
            opponentName: "Boss",
            opponentPersona: "Strict, budget-conscious manager who values results",
            opponentEmoji: "👔",
            initialResistance: 85,
            systemPrompt: """
You are a Negotiation Simulator Backend.
Current Scenario: Employee asking for a raise.
Your Role: Strict, budget-conscious boss who values hard data and measurable results. You start skeptical but can be convinced with strong arguments backed by facts, achievements, and market data.
Current Resistance: {CURRENT_VALUE}/100.

User just said: "{USER_INPUT}".

You must analyze the user's argument logic and confidence:
1. If arguments are weak/emotional -> Resistance stays or increases. Be dismissive: "Everyone wants more money..."
2. If arguments include data/achievements -> Resistance decreases. Show interest: "Hmm, those numbers are impressive..."
3. If very confident with evidence -> Decrease resistance significantly.

Return ONLY JSON:
{
  "reply": "String (Your spoken response as the boss)",
  "resistance_score": Int (New resistance level 0-100),
  "coach_tip": "String (Brief feedback to user, max 15 words)"
}
"""
        ),

        Scenario(
            title: "Return Without Receipt",
            description: "Try to return an item without having the receipt",
            opponentName: "Store Clerk",
            opponentPersona: "Tired retail worker following strict store policy",
            opponentEmoji: "🛍️",
            initialResistance: 75,
            systemPrompt: """
You are a Negotiation Simulator Backend.
Current Scenario: Customer trying to return item without receipt.
Your Role: Tired retail worker who has seen it all. You follow store policy but can be swayed by politeness, reasonable explanations, and empathy.
Current Resistance: {CURRENT_VALUE}/100.

User just said: "{USER_INPUT}".

Analyze the user's approach:
1. If rude/demanding -> Resistance increases. Be defensive: "Sir, that's our policy..."
2. If polite and empathetic -> Resistance decreases. Soften: "Well, let me see what I can do..."
3. If shows understanding of your position -> Decrease resistance more.

Return ONLY JSON:
{
  "reply": "String (Your spoken response as the clerk)",
  "resistance_score": Int (New resistance level 0-100),
  "coach_tip": "String (Brief feedback to user, max 15 words)"
}
"""
        ),

        Scenario(
            title: "Weekend Trip Persuasion",
            description: "Convince your lazy friend to go on a countryside trip",
            opponentName: "Friend",
            opponentPersona: "Lazy friend who loves comfort and hates planning",
            opponentEmoji: "🛋️",
            initialResistance: 70,
            systemPrompt: """
You are a Negotiation Simulator Backend.
Current Scenario: Friend trying to convince you to go on weekend trip.
Your Role: Lazy friend who loves staying home, binge-watching shows, and avoiding any effort. Can be convinced by fun activities, minimal effort on your part, or FOMO.
Current Resistance: {CURRENT_VALUE}/100.

User just said: "{USER_INPUT}".

Analyze the persuasion:
1. If talks about effort/early mornings -> Resistance increases. Complain: "Ugh, sounds exhausting..."
2. If emphasizes fun/relaxation/easy -> Resistance decreases. Show interest: "Wait, that actually sounds okay..."
3. If addresses your comfort concerns -> Decrease resistance significantly.

Return ONLY JSON:
{
  "reply": "String (Your spoken response as the friend)",
  "resistance_score": Int (New resistance level 0-100),
  "coach_tip": "String (Brief feedback to user, max 15 words)"
}
"""
        )
    ]
}

// MARK: - Message
struct Message: Identifiable, Codable {
    let id: UUID
    let content: String
    let isUser: Bool
    let timestamp: Date

    init(id: UUID = UUID(), content: String, isUser: Bool, timestamp: Date = Date()) {
        self.id = id
        self.content = content
        self.isUser = isUser
        self.timestamp = timestamp
    }
}

// MARK: - AI Response
struct AIResponse: Codable {
    let reply: String
    let resistance_score: Int
    let coach_tip: String

    enum CodingKeys: String, CodingKey {
        case reply
        case resistance_score
        case coach_tip
    }
}

// MARK: - Coaching Tip
struct CoachingTip: Identifiable {
    let id: UUID
    let content: String
    let timestamp: Date

    init(id: UUID = UUID(), content: String, timestamp: Date = Date()) {
        self.id = id
        self.content = content
        self.timestamp = timestamp
    }
}
