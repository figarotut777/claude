import SwiftUI

@main
struct StartUpEvolutionApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .windowStyle(.hiddenTitleBar)
        .windowResizability(.contentSize)
        .commands {
            // Remove default "New Window" menu item
            CommandGroup(replacing: .newItem) { }
        }
    }
}
