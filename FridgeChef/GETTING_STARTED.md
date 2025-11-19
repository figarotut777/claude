# Getting Started with FridgeChef 🚀

## Prerequisites

- macOS 14.0 (Sonoma) or later
- Xcode 15.0 or later
- (Optional) [XcodeGen](https://github.com/yonaskolb/XcodeGen) for project generation

## Setup Instructions

### Method 1: Using XcodeGen (Recommended)

1. Install XcodeGen (if not already installed):
   ```bash
   brew install xcodegen
   ```

2. Navigate to the project folder:
   ```bash
   cd FridgeChef
   ```

3. Generate the Xcode project:
   ```bash
   xcodegen generate
   ```

4. Open the project:
   ```bash
   open FridgeChef.xcodeproj
   ```

### Method 2: Manual Xcode Project Creation

1. Open Xcode and create a new project:
   - **Template**: macOS → App
   - **Product Name**: `FridgeChef`
   - **Interface**: SwiftUI
   - **Language**: Swift
   - **Organization Identifier**: `com.fridgechef`
   - **Deployment Target**: macOS 14.0

2. Close Xcode

3. Replace the auto-generated `FridgeChef` folder contents with the files from this repository

4. Open the project in Xcode

## First Run

1. Build and run the project (⌘R)

2. The app will launch in **Mock Data mode** by default - this means you can test all features without API keys!

3. Try the flow:
   - Drag any food photo into the drop zone
   - Click "Scan Ingredients"
   - Review detected ingredients (from mock data)
   - Click "Generate Recipes"
   - Browse 3 recipe suggestions

## Configuring Real API Access

When you're ready to use real AI:

1. Get an API key:
   - **OpenAI**: https://platform.openai.com/api-keys
   - **Anthropic**: https://console.anthropic.com/

2. Open FridgeChef Settings (⌘,):
   - Select your AI provider
   - Enter your API key
   - Uncheck "Use Mock Data"

3. Test with a real fridge photo!

## Project Structure Overview

```
FridgeChef/
├── Models/              # Data structures
│   ├── Ingredient.swift
│   └── Recipe.swift
├── Services/            # Business logic
│   └── APIService.swift # API client with mock data
├── ViewModels/          # MVVM state management
│   └── MainViewModel.swift
├── Views/               # SwiftUI views
│   ├── DropZoneView.swift
│   ├── IngredientListView.swift
│   └── RecipeListView.swift
├── ContentView.swift    # Main app view
└── FridgeChefApp.swift  # App entry point
```

## Key Features Implemented

✅ **Phase 1 Complete**:
- Drag & Drop interface
- Image selection and preview
- Beautiful native macOS UI

✅ **Phase 2 Complete**:
- APIService with mock data
- Image to Base64 conversion (with compression)
- Ingredient detection flow
- API key management

✅ **Phase 3 Partially Complete**:
- Mock recipe generation
- Ingredient confirmation & editing
- Recipe browsing & detail views
- ⚠️ Real API integration (OpenAI/Anthropic) - TODO

## Development Roadmap

### Next Steps (Phase 3)
- [ ] Implement OpenAI Vision API integration
- [ ] Implement Anthropic Claude Vision API integration
- [ ] Add proper error handling for API failures
- [ ] Improve JSON parsing from AI responses

### Future (Phase 4)
- [ ] SwiftData for persistent favorites
- [ ] Recipe sharing functionality
- [ ] Dietary restrictions filter
- [ ] Custom app icon
- [ ] Dark mode optimization

## Troubleshooting

**Build errors?**
- Ensure deployment target is set to macOS 14.0 or higher
- Check that all files are included in the target

**App crashes on image drop?**
- Verify you're using a valid image format (JPG, PNG, HEIC)
- Check console for error messages

**API not working?**
- Ensure "Use Mock Data" is disabled in Settings
- Verify your API key is correct
- Check your internet connection

## Testing

The app is designed to work perfectly with mock data, so you can:
- Test all UI flows without spending money
- Develop new features without API limits
- Share with testers who don't have API keys

Simply keep "Use Mock Data" enabled in Settings!

## Need Help?

- Check `README.md` for full project documentation
- Review the code comments in each Swift file
- All major functions have clear documentation

---

**Happy Coding! 🎉**

If you have questions or want to contribute, feel free to open an issue or PR.
