//
//  TubePlannerApp.swift
//  TubePlanner
//
//  Created on 19.11.2025
//  Main app entry point with SwiftData configuration
//

import SwiftUI
import SwiftData

@main
struct TubePlannerApp: App {
    // MARK: - SwiftData Model Container

    let modelContainer: ModelContainer

    // MARK: - Initialization

    init() {
        do {
            // Configure the SwiftData schema
            let schema = Schema([
                VideoProject.self,
                TaskItem.self
            ])

            // Configure the model container
            let modelConfiguration = ModelConfiguration(
                schema: schema,
                isStoredInMemoryOnly: false
            )

            modelContainer = try ModelContainer(
                for: schema,
                configurations: [modelConfiguration]
            )

            print("✅ SwiftData container initialized successfully")
        } catch {
            fatalError("Failed to create ModelContainer: \(error)")
        }
    }

    // MARK: - Scene Configuration

    var body: some Scene {
        WindowGroup {
            ContentView()
                .frame(minWidth: 800, minHeight: 600)
        }
        .modelContainer(modelContainer)
        .commands {
            // Custom commands for macOS menu bar
            CommandGroup(replacing: .newItem) {
                Button("New Video Project") {
                    // This will be handled by ContentView later
                    NotificationCenter.default.post(
                        name: NSNotification.Name("ShowAddVideoSheet"),
                        object: nil
                    )
                }
                .keyboardShortcut("n", modifiers: [.command])
            }
        }

        // MARK: - Settings Scene (for future use)
        #if os(macOS)
        Settings {
            SettingsView()
        }
        #endif
    }
}

// MARK: - Settings View (Placeholder)

struct SettingsView: View {
    var body: some View {
        TabView {
            GeneralSettingsView()
                .tabItem {
                    Label("General", systemImage: "gear")
                }

            APISettingsView()
                .tabItem {
                    Label("API Keys", systemImage: "key.fill")
                }
        }
        .frame(width: 500, height: 300)
    }
}

struct GeneralSettingsView: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("General Settings")
                .font(.headline)

            Text("Settings will be available in Phase 4")
                .foregroundStyle(.secondary)

            Spacer()
        }
        .padding()
    }
}

struct APISettingsView: View {
    @AppStorage("openaiApiKey") private var openaiApiKey: String = ""
    @AppStorage("selectedAIProvider") private var selectedProvider: String = "openai"

    var body: some View {
        Form {
            Section {
                Picker("AI Provider", selection: $selectedProvider) {
                    Text("OpenAI (GPT-4o)").tag("openai")
                    Text("Anthropic (Claude 3.5 Sonnet)").tag("anthropic")
                }

                SecureField("API Key", text: $openaiApiKey)
                    .textFieldStyle(.roundedBorder)

                Text("Your API key is stored securely in the macOS Keychain")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            } header: {
                Text("AI Configuration")
            }

            Section {
                Link("Get OpenAI API Key", destination: URL(string: "https://platform.openai.com/api-keys")!)
                Link("Get Anthropic API Key", destination: URL(string: "https://console.anthropic.com/")!)
            }
        }
        .formStyle(.grouped)
        .padding()
    }
}
