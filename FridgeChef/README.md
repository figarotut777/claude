# FridgeChef — AI Cooking Assistant 🍳🤖

![macOS](https://img.shields.io/badge/macOS-14.0+-blue.svg)
![Swift](https://img.shields.io/badge/Swift-5.9+-orange.svg)
![SwiftUI](https://img.shields.io/badge/SwiftUI-green.svg)

FridgeChef is a native macOS app that helps you create delicious recipes based on what's in your fridge. Simply take a photo of your fridge contents, and AI will suggest recipes you can make with those ingredients!

## ✨ Features

- 📸 **Drag & Drop** - Easy image upload with drag and drop support
- 🔍 **AI Vision** - Automatic ingredient detection using GPT-4o or Claude 3.5 Sonnet
- ✏️ **Editable Ingredients** - Review and edit detected ingredients before generating recipes
- 🍽️ **Recipe Generation** - Get 3 unique recipes using ONLY your available ingredients
- 💾 **Save Favorites** - Bookmark your favorite recipes for later
- 🎨 **Beautiful UI** - Native macOS design with SwiftUI

## 🚀 Quick Start

### Opening the Project

**Option 1: Create New Xcode Project (Recommended)**

Since the project was created in a Linux environment, the easiest way to get started is:

1. Open Xcode on your Mac
2. Create a new macOS App project:
   - Product Name: `FridgeChef`
   - Interface: `SwiftUI`
   - Language: `Swift`
   - Minimum Deployment: `macOS 14.0`
3. Close Xcode
4. Replace the generated files with the files from this repository:
   ```bash
   # Navigate to your new Xcode project
   cd /path/to/your/FridgeChef

   # Copy all Swift files from this repo
   cp -r /path/to/this/repo/FridgeChef/FridgeChef/* FridgeChef/
   ```
5. Open the project in Xcode

**Option 2: Use Xcodegen (Alternative)**

If you have [Xcodegen](https://github.com/yonaskolb/XcodeGen) installed:

```bash
cd FridgeChef
xcodegen generate
open FridgeChef.xcodeproj
```

### Project Structure

```
FridgeChef/
├── FridgeChef/
│   ├── FridgeChefApp.swift          # App entry point
│   ├── ContentView.swift            # Main view controller
│   ├── Models/
│   │   ├── Ingredient.swift         # Ingredient data model
│   │   └── Recipe.swift             # Recipe data model
│   ├── Services/
│   │   └── APIService.swift         # API client with mock data
│   ├── Views/
│   │   ├── DropZoneView.swift       # Drag & drop image view
│   │   ├── IngredientListView.swift # Ingredient confirmation view
│   │   └── RecipeListView.swift     # Recipe display views
│   └── ViewModels/
│       └── MainViewModel.swift      # MVVM view model
└── README.md
```

## 🎯 Implementation Status

### ✅ Phase 1: Setup & UI Foundation
- [x] Project structure created
- [x] DropZoneView with drag & drop support
- [x] NSImage handling from various sources
- [x] Beautiful native macOS UI

### ✅ Phase 2: API Client (Vision)
- [x] APIService structure
- [x] Image to Base64 conversion (with 1024px compression)
- [x] Mock data for testing
- [x] Ingredient detection flow

### 🔄 Phase 3: Recipe Generation (In Progress)
- [x] Recipe generation with mock data
- [x] Ingredient confirmation screen
- [x] Recipe list and detail views
- [ ] Real OpenAI API integration
- [ ] Real Anthropic API integration

### 📋 Phase 4: Final Polish (Planned)
- [x] Settings screen for API key
- [x] Mock data toggle for testing
- [ ] API provider selection (OpenAI/Anthropic)
- [ ] Persistent favorites storage with SwiftData
- [ ] Error handling improvements
- [ ] App icon design

## 🧪 Testing with Mock Data

The app is configured to use **mock data by default**, so you can test all features without spending money on API calls:

1. Launch the app
2. Drag any food image into the drop zone
3. Click "Scan Ingredients" - you'll see mock ingredients
4. Edit the list if needed
5. Click "Generate Recipes" - you'll see 3 mock recipes

To enable real API calls:
1. Go to **Settings** (⌘,)
2. Enter your API key
3. Uncheck "Use Mock Data"

## 🔑 API Configuration

### OpenAI (GPT-4o)
1. Get API key from [platform.openai.com](https://platform.openai.com/)
2. Add to Settings in the app
3. Select "OpenAI (GPT-4o)" as provider

### Anthropic (Claude 3.5 Sonnet)
1. Get API key from [console.anthropic.com](https://console.anthropic.com/)
2. Add to Settings in the app
3. Select "Anthropic (Claude 3.5 Sonnet)" as provider

## 📝 System Prompts

**Vision Analysis:**
```
Identify all food ingredients in this image. Be specific (e.g., 'Cheddar Cheese'
instead of 'Cheese'). Ignore non-food items. Return ONLY a raw JSON array of strings,
e.g., ['Eggs', 'Milk'].
```

**Recipe Generation:**
```
Create 3 distinct recipes using ONLY these ingredients: {INGREDIENTS}.
Assume user has basic pantry items (Salt, Pepper, Oil, Water).
Format response as JSON: [{ 'title': '...', 'time': '15 min', 'steps': ['Step 1', 'Step 2'] }].
```

## 🛠️ Technical Details

- **Architecture**: MVVM (Model-View-ViewModel)
- **UI Framework**: SwiftUI
- **Minimum macOS**: 14.0 (Sonoma)
- **Swift Version**: 5.9+
- **Storage**: UserDefaults (API keys), SwiftData (planned for favorites)

## 📸 Key Components

### APIService.swift
- Image to Base64 conversion with compression
- Mock data for testing
- Prepared for both OpenAI and Anthropic integrations
- API key management via UserDefaults

### DropZoneView.swift
- Drag & drop support for images
- File picker integration
- Support for JPG, PNG, HEIC formats
- Visual feedback for drop targets

### MainViewModel.swift
- State management (idle, analyzing, confirming, generating, showing)
- Ingredient CRUD operations
- Async API calls
- Error handling

## 🤝 Contributing

This is a personal project created as a learning exercise. Feel free to fork and customize!

## 📄 License

MIT License - Feel free to use this code for your own projects.

## 🙏 Credits

Created by Claude (AI Assistant) based on detailed specifications.
Built with ❤️ using Swift and SwiftUI.

---

**Note**: This app was initially developed in a Linux environment, so the Xcode project file might need to be recreated. Follow the "Quick Start" instructions above to get the project running properly.
