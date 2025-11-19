# 🚀 Negotiation Dojo - Setup Guide

This guide will help you get Negotiation Dojo up and running on your macOS system.

## Step 1: System Requirements Check

### Verify macOS Version
```bash
sw_vers
```

You need:
- **ProductVersion**: 14.0 or higher (Sonoma)

### Verify Xcode Installation
```bash
xcodebuild -version
```

You need:
- **Xcode**: 15.0 or higher
- **Build version**: Any recent build

If Xcode is not installed:
1. Open the App Store
2. Search for "Xcode"
3. Click "Get" or "Install"
4. Wait for installation (this can take 30+ minutes)

## Step 2: OpenAI API Setup

### Get Your API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign in or create an account
3. Navigate to [API Keys](https://platform.openai.com/api-keys)
4. Click "Create new secret key"
5. Copy the key (you won't be able to see it again!)

### Verify API Access

Make sure your account has access to:
- ✅ Whisper API (speech-to-text)
- ✅ GPT-4o (required, not GPT-3.5)
- ✅ TTS API (text-to-speech)

### Check Account Credits

Visit [Usage Dashboard](https://platform.openai.com/usage) to ensure you have credits.

**Estimated costs per session:**
- Whisper: ~$0.01 per minute of audio
- GPT-4o: ~$0.03-0.05 per conversation turn
- TTS: ~$0.015 per response

A typical 10-minute practice session costs approximately **$0.50-1.00**.

## Step 3: Set Environment Variable

### Option A: Temporary (Current Terminal Session Only)

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

**Note**: This only works for the current terminal session. If you close the terminal, you'll need to set it again.

### Option B: Permanent (Recommended)

#### For Zsh (Default on modern macOS):

```bash
echo 'export OPENAI_API_KEY="sk-your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

#### For Bash:

```bash
echo 'export OPENAI_API_KEY="sk-your-api-key-here"' >> ~/.bash_profile
source ~/.bash_profile
```

### Verify Environment Variable

```bash
echo $OPENAI_API_KEY
```

You should see your API key printed.

## Step 4: Clone and Build

### Clone the Repository

```bash
# Navigate to where you want the project
cd ~/Documents  # or any other directory

# Clone the repository
git clone https://github.com/figarotut777/claude.git

# Navigate to the project
cd claude/NegotiationDojo
```

### Open in Xcode

```bash
open NegotiationDojo.xcodeproj
```

Xcode will launch and open the project.

## Step 5: Configure Xcode

### Set Development Team (Required for macOS apps)

1. In Xcode, select the project in the navigator (blue icon)
2. Select the "NegotiationDojo" target
3. Go to "Signing & Capabilities" tab
4. Under "Team", select your Apple ID or development team
5. If you don't have a team, click "Add Account..." and sign in with your Apple ID

### Verify Entitlements

Ensure these capabilities are enabled in "Signing & Capabilities":
- ✅ App Sandbox
- ✅ Audio Input (Microphone)
- ✅ Outgoing Connections (Network)
- ✅ User Selected Files (Read/Write)

## Step 6: Build and Run

### Build the Project

1. Select a run destination:
   - Click on "My Mac" or "My Mac (Designed for iPad)" in the toolbar

2. Build the project:
   - Press `⌘B` (Command + B)
   - Or click Product → Build

3. Wait for the build to complete (first build may take 30-60 seconds)

### Run the App

1. Press `⌘R` (Command + R)
2. Or click the "Play" button in the toolbar
3. Or click Product → Run

### Grant Permissions

When the app first launches:

1. **Microphone Permission**:
   - Click "OK" or "Allow" when prompted
   - If you accidentally denied, go to:
     - System Settings → Privacy & Security → Microphone
     - Enable "NegotiationDojo"

2. **Network Access**:
   - Should be automatic due to entitlements

## Step 7: Test the App

### Quick Test Checklist

1. ✅ Dashboard loads with 3 scenarios
2. ✅ Click on "Ask for a Raise" scenario
3. ✅ Dialog interface appears with resistance bar
4. ✅ Hold the microphone button and speak
5. ✅ Release and wait for AI response
6. ✅ Verify you can hear the AI voice
7. ✅ Check that coaching tips appear

### Test Audio Setup

If you have audio issues:

1. **Check system audio**:
   - System Settings → Sound
   - Ensure output device is correct
   - Ensure volume is not muted

2. **Check microphone**:
   - System Settings → Sound → Input
   - Speak and watch the input level move
   - If no movement, select a different microphone

3. **Restart Xcode and the app**

## Troubleshooting Common Issues

### Issue: "OpenAI API key is missing"

**Solution**:
```bash
# Check if the variable is set
echo $OPENAI_API_KEY

# If empty, set it again
export OPENAI_API_KEY="your-key-here"

# Restart Xcode from the same terminal
open NegotiationDojo.xcodeproj
```

**Important**: Xcode must be launched from a terminal that has the environment variable set, or add it to your shell profile.

### Issue: Build fails with signing errors

**Solution**:
1. Go to Signing & Capabilities
2. Uncheck "Automatically manage signing"
3. Then re-check it
4. Select your team again
5. Clean build folder: Product → Clean Build Folder (⌘⇧K)
6. Build again (⌘B)

### Issue: "GPT-4o not available" error

**Solution**:
- Your OpenAI account may not have GPT-4o access
- Check [OpenAI Models](https://platform.openai.com/docs/models)
- You may need to upgrade your account or wait for access
- Temporary workaround: Edit `OpenAIService.swift` and change `chatModel` to `"gpt-3.5-turbo"` (note: less effective coaching)

### Issue: App crashes on launch

**Solution**:
1. Check Console.app for crash logs
2. Look for errors related to:
   - Missing files
   - Audio permissions
   - Framework issues
3. Clean build and rebuild:
   ```bash
   # In terminal
   cd ~/Documents/claude/NegotiationDojo
   rm -rf ~/Library/Developer/Xcode/DerivedData/NegotiationDojo-*

   # Then rebuild in Xcode
   ```

### Issue: High latency (>10 seconds)

**Possible causes**:
- Slow internet connection
- OpenAI API server overload
- Large audio files

**Solutions**:
1. Check internet speed: [speed.cloudflare.com](https://speed.cloudflare.com)
2. Speak more concisely (shorter recordings = faster processing)
3. Try again during off-peak hours

### Issue: Microphone not working

**Solution**:
1. **Grant permissions**:
   - System Settings → Privacy & Security → Microphone
   - Enable NegotiationDojo

2. **Select correct input**:
   - System Settings → Sound → Input
   - Select your microphone
   - Test by speaking and watching level

3. **Restart the app** after granting permissions

### Issue: "Invalid response from OpenAI API"

**Solutions**:
1. **Check API key**: Make sure it's valid and not expired
2. **Check account status**: Visit [OpenAI Platform](https://platform.openai.com/)
3. **Check credits**: Ensure you have available credits
4. **Check API status**: [status.openai.com](https://status.openai.com)

## Advanced Configuration

### Using a Different TTS Voice

Edit `NegotiationDojo/Services/OpenAIService.swift`:

```swift
private let ttsVoice = "alloy"  // Change to: echo, fable, onyx, nova, or shimmer
```

Voice characteristics:
- **alloy**: Neutral, balanced
- **echo**: Clear, friendly (good for boss)
- **fable**: Warm, expressive
- **onyx**: Deep, authoritative
- **nova**: Energetic, young (good for friend)
- **shimmer**: Bright, engaging

### Adjusting Response Speed

Edit `NegotiationDojo/Services/OpenAIService.swift`:

```swift
private let ttsModel = "tts-1"  // Fast, lower quality
// OR
private let ttsModel = "tts-1-hd"  // Slower, higher quality
```

### Custom Scenarios

See the README.md "Customization" section for adding your own scenarios.

## Running from Terminal (Debug Mode)

For debugging, launch the app from Terminal to see console output:

```bash
cd ~/Documents/claude/NegotiationDojo
open NegotiationDojo.xcodeproj

# After building in Xcode, run from terminal:
~/Library/Developer/Xcode/DerivedData/NegotiationDojo-*/Build/Products/Debug/NegotiationDojo.app/Contents/MacOS/NegotiationDojo
```

This will print all debug messages to the terminal.

## Getting Help

If you're still having issues:

1. Check the [README.md](README.md) for more information
2. Create an issue on GitHub with:
   - macOS version
   - Xcode version
   - Error messages
   - Console logs
   - Steps to reproduce

## Next Steps

Once everything is working:

1. 🎯 Practice with all three scenarios
2. 📊 Pay attention to coaching tips
3. 🏆 Try to win with minimal words spoken
4. 🎨 Customize scenarios to your needs
5. 🚀 Share your success stories!

---

**Happy Negotiating! 🥋**
