// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "StartUpEvolution",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .executable(
            name: "StartUpEvolution",
            targets: ["StartUpEvolution"]
        )
    ],
    targets: [
        .executableTarget(
            name: "StartUpEvolution",
            dependencies: [],
            path: "Sources/StartUpEvolution"
        )
    ]
)
