# 🤖 Smart Local Assistant - Enhanced AI Assistant with Real-Time Search & Desktop Control

A comprehensive AI assistant with voice recognition, advanced plugin system, real-time Google-like web search capabilities, and full desktop PC integration. Inspired by the best features from leading open-source AI assistant projects.

## 🚀 **NEW: Enhanced Capabilities**

Your Smart AI Assistant now includes:
- ✅ **Real-time Google-like web search** with live results
- ✅ **Full desktop PC integration** and control
- ✅ **Advanced system monitoring** and process management  
- ✅ **Live information access** from multiple sources
- ✅ **Comprehensive automation** tools and capabilities

## ✨ Features

### 🎙️ Voice Recognition & Control
- **Wake word detection** - Say "Assistant" to activate
- **Continuous listening** with automatic microphone calibration
- **Text-to-speech responses** with configurable voice settings
- **Voice commands** for all functionality

### 🔌 Advanced Plugin System
- **Auto-discovery** - Plugins are automatically loaded from the plugins directory
- **Dynamic enable/disable** - Control plugins at runtime
- **Standardized interface** - All plugins inherit from BasePlugin
- **Command matching** - Intelligent intent recognition

### 🌐 Enhanced Web Search & Real-Time Information
- **Real-Time Google Search** - Advanced web search with live results
- **Instant Answers** - Quick calculations and factual responses
- **Live News Feeds** - Latest news from multiple sources
- **YouTube Search** - Find videos with detailed results
- **Stock Prices** - Real-time market information
- **Weather Updates** - Current conditions and forecasts
- **Social Media Trends** - Reddit and Twitter integration
- **Image & Video Search** - Multimedia content discovery
- **Maps & Directions** - Location-based queries

### 🖥️ Advanced Desktop Integration & System Control
- **Complete System Monitoring** - CPU, memory, disk, network statistics
- **Process Management** - List, monitor, kill, and start applications
- **Window Control** - Focus, minimize, maximize, close windows
- **File Operations** - Search, open, create, delete files and folders
- **Clipboard Management** - Get, set, and view clipboard history
- **Screenshot Capture** - Take and save screenshots
- **Automation** - Mouse clicks, keyboard input, and key presses
- **Hardware Information** - Detailed system and hardware specs
- **Network Information** - Interface details and network statistics
- **Windows Services** - List and monitor system services
- **Battery Status** - Power management for laptops

### 🌤️ Weather Information
- **Current Weather** - "what's the weather in London"
- **Weather Forecasts** - "weather forecast for tomorrow"
- **Multiple Cities** - Automatic city extraction from queries

### 🚀 AI Integration
- **Ollama Support** - Local LLM integration with fallback
- **Multiple Models** - Configure different models for different tasks
- **Smart Fallback** - Graceful degradation when services are unavailable

## 🛠️ Installation & Setup

### Quick Start
```bash
# Clone or download the project
cd "Smart Local Assistant"

# Run setup (installs dependencies including enhanced features)
python start_assistant.py setup

# Start the enhanced assistant with all new capabilities
python start_assistant.py pro
```

### Testing Enhanced Features
```bash
# Run comprehensive demo of all enhanced capabilities
python demo_enhanced_capabilities.py

# Test individual plugins
python debug_test.py
```

### Manual Installation
```bash
# Install required packages for enhanced features
pip install speech_recognition pyttsx3 pyaudio psutil beautifulsoup4 wikipedia requests
pip install googlesearch-python pyautogui pillow pyperclip duckduckgo-search
pip install requests-html selenium feedparser pywin32 wmi

# Start the assistant with enhanced capabilities
python main_pro.py
```

## 🚀 Usage

### Starting the Assistant

**Enhanced Mode (Recommended)**
```bash
python start_assistant.py pro
```

**Voice-Only Mode**
```bash
python start_assistant.py voice
```

**Text-Only Mode**
```bash
python start_assistant.py text
```

**Original Basic Mode**
```bash
python start_assistant.py basic
```

### Voice Commands

**General**
- "Assistant" - Wake word to activate
- "help" - Show available commands
- "exit" or "quit" - Stop the assistant

**Weather**
- "What's the weather in New York?"
- "Weather forecast for tomorrow"
- "Is it raining in London?"

**Enhanced Web Search & Real-Time Information**
- "Search for latest AI developments"
- "What's 15% of 250?" (instant calculations)
- "Latest news about technology"
- "Find YouTube videos about Python"
- "Stock price of Apple"
- "Current weather in Tokyo"
- "Trending topics on Reddit"
- "Images of northern lights"

**Advanced Desktop & System Control**
- "Show system information"
- "List running processes"
- "Take a screenshot"
- "Get clipboard content"
- "Set clipboard to Hello World"
- "List open windows"
- "Search files *.txt"
- "Click at coordinates 500,300"
- "Type text Hello World"
- "Show CPU usage"
- "Check memory usage"
- "Network information"
- "Battery status"

**Basic System Control**
- "Set volume to 50"
- "Volume up" / "Volume down"
- "Set brightness to 80"
- "Brightness up" / "Brightness down"

**Plugin Management**
- "List plugins"
- "Enable weather plugin"
- "Disable system plugin"
- "Plugin status"

### Text Commands

All voice commands work in text mode. Just type them instead of speaking.

## ⚙️ Configuration

Edit `config.json` to customize settings:

```json
{
    "voice": {
        "enabled": true,
        "wake_word": "assistant",
        "language": "en-US",
        "tts_rate": 200
    },
    "plugins": {
        "enabled_plugins": ["enhanced_websearch", "advanced_desktop", "weather", "system", "websearch"]
    },
    "enhanced_websearch": {
        "max_results": 10,
        "enable_instant_answers": true,
        "enable_news": true,
        "enable_youtube": true,
        "timeout": 10
    },
    "advanced_desktop": {
        "screenshot_path": "./screenshots/",
        "enable_automation": true,
        "enable_window_management": true,
        "max_clipboard_history": 50
    },
    "weather": {
        "api_key": "your_openweather_api_key",
        "default_city": "New York"
    }
}
```

### Weather API Setup
1. Get a free API key from [OpenWeatherMap](https://openweathermap.org/api)
2. Add it to `config.json` under `weather.api_key`

### Enhanced Features Setup
The enhanced plugins work out of the box with no additional setup required:
- **Enhanced WebSearch**: Uses multiple search engines and sources
- **Advanced Desktop**: Full Windows PC integration and control
- **Real-time Information**: Live data from various APIs and services

## 🔌 Creating Custom Plugins

Create a new plugin by extending the BasePlugin class:

```python
from advanced_plugin_manager import BasePlugin

class MyPlugin(BasePlugin):
    def __init__(self):
        super().__init__("myplugin", "My Custom Plugin")
    
    def can_handle(self, command):
        return "my command" in command.lower()
    
    def execute(self, command, context=None):
        return "Hello from my plugin!"
    
    def get_help(self):
        return "my command - Does something amazing"

# Plugin will be auto-discovered when placed in plugins/ directory
```

## 📁 Project Structure

```
Smart Local Assistant/
├── main_pro.py                    # Enhanced assistant main file
├── main.py                        # Original assistant (preserved)
├── start_assistant.py             # Launcher script
├── voice_handler.py               # Voice recognition and TTS
├── advanced_plugin_manager.py     # Plugin system
├── config.json                    # Configuration
├── utils.py                       # Utility functions
├── demo_enhanced_capabilities.py  # Demo of enhanced features
├── debug_test.py                  # Plugin testing utilities
├── MISSION_COMPLETE.md            # Implementation documentation
├── QUICK_REFERENCE.md             # Quick command reference
├── plugins/
│   ├── __init__.py
│   ├── enhanced_websearch.py      # Real-time web search plugin
│   ├── advanced_desktop.py        # Desktop integration plugin
│   ├── weather.py                 # Weather plugin
│   ├── system.py                  # System control plugin
│   └── websearch.py               # Basic web search plugin
└── README.md                      # This file
```

## 🔧 Troubleshooting

### Voice Recognition Issues
- **Microphone not working**: Check microphone permissions and default device
- **Poor recognition**: Calibrate microphone with "calibrate microphone" command
- **No audio output**: Verify speakers/headphones and TTS settings

### Plugin Issues
- **Plugin not loading**: Check for syntax errors in plugin files
- **Command not recognized**: Verify the `can_handle()` method in your plugin

### Dependencies
- **PyAudio installation fails**: Install Microsoft Visual C++ Build Tools
- **SpeechRecognition issues**: Update to latest version

## 🎯 Roadmap

### ✅ Recently Completed
- [x] **Enhanced Web Search** - Real-time Google-like search capabilities
- [x] **Advanced Desktop Integration** - Full Windows PC control and automation
- [x] **Real-time Information** - Live news, stock prices, weather updates
- [x] **System Monitoring** - Comprehensive hardware and software monitoring
- [x] **Process Management** - Advanced process control and monitoring
- [x] **Clipboard Management** - Full clipboard operations and history
- [x] **Window Management** - Complete window control for productivity
- [x] **Screenshot Capabilities** - Screen capture and automation tools
- [x] **File Operations** - Advanced file search and management

### Planned Features
- [ ] **Web UI** - Browser-based interface like TaskWeaver
- [ ] **Calendar Integration** - Schedule management and reminders
- [ ] **Email Plugin** - Send and read emails
- [ ] **Smart Home Integration** - Control IoT devices
- [ ] **Multi-Language Support** - Support for multiple languages
- [ ] **Custom Wake Words** - Trainable wake word detection
- [ ] **Voice Profiles** - Multiple user voice recognition

### Advanced Features
- [ ] **Task Automation** - Workflow automation and scheduling
- [ ] **Machine Learning Pipeline** - Local model training and inference
- [ ] **Code Generation** - Advanced coding assistance
- [ ] **Knowledge Base** - Personal information management
- [ ] **API Integration** - Connect with popular services

## 🤝 Contributing

Feel free to contribute by:
1. Creating new plugins
2. Improving existing functionality
3. Adding new features
4. Fixing bugs
5. Improving documentation

## 📝 License

This project is open source. Feel free to modify and distribute.

## 🙏 Acknowledgments

Inspired by and incorporates ideas from:
- **Microsoft TaskWeaver** - Plugin architecture and code execution
- **Langchain-Chatchat** - RAG capabilities and multi-model support  
- **LocalForge** - Local development agent concepts
- **OpenVoice** - Advanced voice synthesis techniques
- Various open-source voice assistant projects

---

**Enjoy your enhanced AI assistant! 🚀**
