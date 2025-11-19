//
//  ContentView.swift
//  NegotiationDojo
//
//  Created by Claude on 2025-11-19.
//

import SwiftUI

struct ContentView: View {
    @State private var selectedScenario: Scenario?
    @State private var showDashboard = true

    var body: some View {
        ZStack {
            if showDashboard {
                DashboardView(selectedScenario: $selectedScenario, showDashboard: $showDashboard)
            } else if let scenario = selectedScenario {
                DialogView(scenario: scenario, showDashboard: $showDashboard)
            }
        }
        .frame(minWidth: 800, minHeight: 600)
    }
}

#Preview {
    ContentView()
}
