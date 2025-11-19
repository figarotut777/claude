# ⚡️ Quick Start Guide

Get Negotiation Dojo running in 5 minutes!

## Prerequisites

- macOS 14.0+ (Sonoma)
- Xcode 15.0+
- OpenAI API key

## Installation

### 1. Get Your OpenAI API Key

Visit [OpenAI Platform](https://platform.openai.com/api-keys) and create a new key.

### 2. Set Environment Variable

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

**Make it permanent** (recommended):
```bash
echo 'export OPENAI_API_KEY="sk-your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Open and Run

```bash
cd NegotiationDojo
open NegotiationDojo.xcodeproj
```

In Xcode:
1. Select your development team under "Signing & Capabilities"
2. Press `⌘R` to build and run
3. Grant microphone permission when prompted

## First Session

1. Select "Return Without Receipt" (easiest scenario)
2. Hold the microphone button and speak:
   > "Hi, I bought this last week but lost my receipt. I'd really appreciate your help - is there any way you could process the return?"
3. Release and wait for the AI response
4. Watch the resistance bar decrease!
5. Continue the conversation until you win

## Troubleshooting

**"OpenAI API key is missing"**
```bash
echo $OPENAI_API_KEY  # Should print your key
# If empty, set it again and restart Xcode
```

**"Microphone permission denied"**
- System Settings → Privacy & Security → Microphone
- Enable "NegotiationDojo"

**Build errors**
- Product → Clean Build Folder (`⌘⇧K`)
- Rebuild (`⌘B`)

## Next Steps

- Read [README.md](README.md) for full documentation
- See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup
- Check [ARCHITECTURE.md](ARCHITECTURE.md) to understand the code

---

**🎯 Pro Tip**: Start with specific facts and numbers. The AI responds better to data-driven arguments than emotional appeals!
