//
//  QuickSpendApp.swift
//  QuickSpend
//
//  Created by Claude on 19.11.2025.
//

import SwiftUI
import SwiftData

@main
struct QuickSpendApp: App {
    var sharedModelContainer: ModelContainer = {
        let schema = Schema([
            Transaction.self,
            Category.self
        ])

        let modelConfiguration = ModelConfiguration(
            schema: schema,
            isStoredInMemoryOnly: false
        )

        do {
            return try ModelContainer(
                for: schema,
                configurations: [modelConfiguration]
            )
        } catch {
            fatalError("Could not create ModelContainer: \(error)")
        }
    }()

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(sharedModelContainer)
        .commands {
            CommandGroup(replacing: .newItem) {
                Button("New Transaction") {
                    // Focus on input field
                }
                .keyboardShortcut("n", modifiers: .command)
            }
        }
    }
}
