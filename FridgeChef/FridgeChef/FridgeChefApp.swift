//
//  FridgeChefApp.swift
//  FridgeChef
//
//  Created by Claude on 19/11/2025.
//

import SwiftUI

@main
struct FridgeChefApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .frame(minWidth: 700, minHeight: 600)
        }
        .windowStyle(.hiddenTitleBar)
        .windowResizability(.contentSize)

        #if os(macOS)
        Settings {
            SettingsView()
        }
        #endif
    }
}

// MARK: - Settings View

struct SettingsView: View {
    @AppStorage("api_key") private var apiKey: String = ""
    @State private var selectedProvider: Int = 0
    @State private var useMockData: Bool = true

    let providers = ["OpenAI (GPT-4o)", "Anthropic (Claude 3.5 Sonnet)"]

    var body: some View {
        Form {
            Section {
                VStack(alignment: .leading, spacing: 8) {
                    Text("AI Provider")
                        .font(.headline)

                    Picker("Provider", selection: $selectedProvider) {
                        ForEach(0..<providers.count, id: \.self) { index in
                            Text(providers[index]).tag(index)
                        }
                    }
                    .pickerStyle(.radioGroup)
                }

                Divider()

                VStack(alignment: .leading, spacing: 8) {
                    Text("API Key")
                        .font(.headline)

                    SecureField("Enter your API key", text: $apiKey)
                        .textFieldStyle(.roundedBorder)

                    Text("Your API key is stored securely on this device.")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Divider()

                VStack(alignment: .leading, spacing: 8) {
                    Toggle("Use Mock Data (for testing)", isOn: $useMockData)
                        .onChange(of: useMockData) { _, newValue in
                            APIService.shared.useMockData = newValue
                        }

                    Text("Enable this to test the app without making real API calls.")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding()
        .frame(width: 500)
        .onAppear {
            useMockData = APIService.shared.useMockData
        }
    }
}

// MARK: - Preview

struct SettingsView_Previews: PreviewProvider {
    static var previews: some View {
        SettingsView()
    }
}
