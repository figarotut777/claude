# 🤝 Contributing to Negotiation Dojo

Thank you for your interest in contributing! This guide will help you get started.

## Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest new features
- 📝 Improve documentation
- 🎨 Enhance UI/UX
- 🧪 Add test coverage
- 🎯 Create new scenarios
- 🔧 Fix issues

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/claude.git
cd claude/NegotiationDojo
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 3. Set Up Development Environment

Follow [SETUP_GUIDE.md](SETUP_GUIDE.md) to configure your environment.

## Development Guidelines

### Code Style

#### Swift Naming Conventions

```swift
// Classes and Structs: PascalCase
class NegotiationEngine { }
struct Scenario { }

// Variables and Functions: camelCase
var currentResistance: Int
func processUserSpeech() async { }

// Constants: camelCase
let maxResistance = 100

// Published properties: descriptive, state-focused
@Published var isProcessing = false
@Published var errorMessage: String?
```

#### SwiftUI View Structure

```swift
struct MyView: View {
    // MARK: - Properties
    @State private var myState: Bool = false

    // MARK: - Body
    var body: some View {
        // View hierarchy
    }

    // MARK: - Subviews
    private var mySubview: some View {
        // Component
    }

    // MARK: - Methods
    private func myAction() {
        // Logic
    }
}
```

### File Organization

```
NegotiationDojo/
├── Models/           # Pure data structures
├── Views/            # SwiftUI views
├── ViewModels/       # Business logic
└── Services/         # External integrations
```

### Comments

```swift
// MARK: - Section Name   (for major sections)

/// Documentation comment for public API
/// - Parameter input: Description
/// - Returns: Description
func publicMethod(input: String) -> Int { }

// Inline comment for complex logic
let result = complexCalculation() // Brief explanation
```

### Error Handling

```swift
// Define custom errors
enum MyError: LocalizedError {
    case specificCase

    var errorDescription: String? {
        switch self {
        case .specificCase:
            return "User-friendly message"
        }
    }
}

// Use async/await with proper error propagation
func myAsyncFunction() async throws -> Result {
    do {
        return try await riskyOperation()
    } catch {
        // Log for debugging
        print("Error in myAsyncFunction: \(error)")
        throw error // Propagate
    }
}
```

## Adding New Features

### 1. New Scenarios

Edit `Models/Models.swift`:

```swift
extension Scenario {
    static let scenarios: [Scenario] = [
        // Existing scenarios...

        Scenario(
            title: "Your New Scenario",
            description: "Brief description for dashboard",
            opponentName: "Opponent Type",
            opponentPersona: "Detailed personality",
            opponentEmoji: "🎭",
            initialResistance: 75,
            systemPrompt: """
You are a Negotiation Simulator Backend.
Current Scenario: [Describe the situation]
Your Role: [Opponent personality and behavior]
Current Resistance: {CURRENT_VALUE}/100.

User just said: "{USER_INPUT}".

Analyze the user's approach:
1. If [bad approach] -> Resistance increases. Be [reaction]
2. If [good approach] -> Resistance decreases. Show [reaction]
3. If [excellent approach] -> Decrease significantly.

Return ONLY JSON:
{
  "reply": "String (Your spoken response)",
  "resistance_score": Int (New resistance level 0-100),
  "coach_tip": "String (Brief feedback, max 15 words)"
}
"""
        )
    ]
}
```

**Test your scenario:**
- Run multiple conversations
- Verify resistance changes appropriately
- Ensure coaching tips are helpful
- Check that victory is achievable

### 2. New UI Components

Create in `Views/`:

```swift
//
//  MyNewComponent.swift
//  NegotiationDojo
//
//  Brief description
//  Created by Your Name on Date
//

import SwiftUI

struct MyNewComponent: View {
    // Properties
    let data: MyData

    var body: some View {
        // Implementation
    }
}

#Preview {
    MyNewComponent(data: .sample)
}
```

**Guidelines:**
- Keep components small and focused
- Use composition over complexity
- Add Preview for easy testing
- Follow existing visual style

### 3. New Services

Create in `Services/`:

```swift
@MainActor
class MyService: ObservableObject {
    @Published var state: MyState = .idle

    func performAction() async throws {
        // Implementation
    }
}
```

**Requirements:**
- Use `@MainActor` for UI-updating services
- Publish state changes
- Handle errors gracefully
- Clean up resources (implement deinit if needed)

## Testing

### Manual Testing Checklist

Before submitting a PR:

- [ ] Dashboard loads correctly
- [ ] All scenarios start properly
- [ ] Audio recording works
- [ ] Audio playback works
- [ ] Resistance bar updates
- [ ] Coaching tips appear
- [ ] Victory condition triggers
- [ ] Reset functionality works
- [ ] Back navigation works
- [ ] Error messages display correctly
- [ ] No crashes or freezes

### Test on Clean Installation

```bash
# Remove all app data
rm -rf ~/Library/Developer/Xcode/DerivedData/NegotiationDojo-*

# Clean build
xcodebuild clean

# Build fresh
xcodebuild -project NegotiationDojo.xcodeproj -scheme NegotiationDojo
```

## Submitting Changes

### 1. Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Format
<type>: <description>

# Types
feat: New feature
fix: Bug fix
docs: Documentation changes
style: Code style changes (formatting, etc.)
refactor: Code refactoring
test: Adding tests
chore: Build process or auxiliary changes

# Examples
git commit -m "feat: add custom scenario creation"
git commit -m "fix: resolve microphone permission crash"
git commit -m "docs: update setup guide with troubleshooting"
git commit -m "style: format DialogView with SwiftFormat"
git commit -m "refactor: extract message handling to separate service"
```

### 2. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:

**Title**: Brief description (e.g., "Add meditation scenario")

**Description**:
```markdown
## What does this PR do?
Brief explanation of changes

## Why is this needed?
Problem this solves or feature this adds

## How has this been tested?
- [ ] Manual testing
- [ ] Added unit tests
- [ ] Tested on clean install

## Screenshots (if UI changes)
[Add screenshots]

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No console warnings
- [ ] Tested on macOS 14.0+
```

### 3. Code Review

- Be open to feedback
- Respond to comments promptly
- Make requested changes in new commits
- Squash commits before merge (if requested)

## Community Guidelines

### Be Respectful

- Assume good intentions
- Provide constructive feedback
- Welcome newcomers
- Help others learn

### Communication

- Be clear and concise
- Use examples when explaining
- Ask questions if unsure
- Document your decisions

## Issue Reporting

### Bug Reports

**Title**: Brief description of the bug

**Template**:
```markdown
## Description
What is the bug?

## Steps to Reproduce
1. Step one
2. Step two
3. See error

## Expected Behavior
What should happen?

## Actual Behavior
What actually happens?

## Environment
- macOS version:
- Xcode version:
- App version:

## Console Logs
```
Paste any error messages
```

## Screenshots
[If applicable]
```

### Feature Requests

**Title**: Brief feature description

**Template**:
```markdown
## Problem
What problem does this solve?

## Proposed Solution
How would this feature work?

## Alternatives Considered
Any other approaches?

## Additional Context
Mockups, examples, etc.
```

## Recognition

Contributors will be acknowledged in:
- README.md Contributors section
- Release notes
- Project credits

## Questions?

- Check [README.md](README.md) and [ARCHITECTURE.md](ARCHITECTURE.md)
- Search existing issues
- Create a new issue with the "question" label

---

**Thank you for contributing to Negotiation Dojo! 🥋**
