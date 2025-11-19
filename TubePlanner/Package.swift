// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "TubePlanner",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .executable(
            name: "TubePlanner",
            targets: ["TubePlanner"]
        )
    ],
    dependencies: [
        // Dependencies will be added in Phase 2 (for networking, etc.)
    ],
    targets: [
        .executableTarget(
            name: "TubePlanner",
            dependencies: [],
            path: ".",
            exclude: [
                "Package.swift",
                "README.md",
                "Resources"
            ],
            sources: [
                "TubePlannerApp.swift",
                "Models",
                "Views",
                "Services"
            ],
            swiftSettings: [
                .enableUpcomingFeature("BareSlashRegexLiterals")
            ]
        )
    ]
)
