# 🤖 Smart Local AI Assistant

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://windows.com)

A comprehensive AI assistant with voice recognition, real-time Google-like web search capabilities, and full desktop PC integration. Features advanced plugin architecture, live information access, and complete system automation.

## ✨ **Key Features**

### 🌐 **Enhanced Web Search & Real-Time Information**
- **Real-Time Google Search** - Advanced web search with live results and content extraction
- **Instant Answers** - Quick calculations, definitions, and factual responses
- **Live News Feeds** - Latest news from multiple sources (BBC, CNN, Reuters, NPR)
- **YouTube Search** - Find videos with detailed metadata
- **Stock Prices** - Real-time market information
- **Weather Updates** - Current conditions and forecasts
- **Social Media Trends** - Reddit integration
- **Content Reading** - Actually reads and processes web content

### 🖥️ **Advanced Desktop Integration & System Control**
- **Complete System Monitoring** - CPU, memory, disk, network statistics
- **Process Management** - List, monitor, kill, and start applications
- **Window Control** - Focus, minimize, maximize, close windows
- **File Operations** - Search, open, create, delete files and folders
- **Clipboard Management** - Get, set, and view clipboard history
- **Screenshot Capture** - Take and save screenshots
- **Automation** - Mouse clicks, keyboard input, and key presses
- **Hardware Information** - Detailed system and hardware specs
- **Windows Services** - List and monitor system services

### 🎙️ **Voice Recognition & Control**
- **Wake word detection** - Say "Assistant" to activate
- **Continuous listening** with automatic microphone calibration
- **Text-to-speech responses** with configurable voice settings
- **Voice commands** for all functionality

### 🔌 **Advanced Plugin System**
- **Auto-discovery** - Plugins automatically loaded from plugins directory
- **Dynamic enable/disable** - Control plugins at runtime
- **Standardized interface** - All plugins inherit from BasePlugin
- **Command matching** - Intelligent intent recognition

## 🚀 **Quick Start**

### **Installation**

1. **Clone the repository:**   ```bash
   git clone https://github.com/yourusername/Smart-Local-AI-Assistant.git
   cd Smart-Local-AI-Assistant
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the enhanced assistant:**
   ```bash
   python start_assistant.py pro
   ```

### **Dependencies Installation**
```bash
pip install speech_recognition pyttsx3 pyaudio psutil beautifulsoup4 wikipedia requests
pip install googlesearch-python pyautogui pillow pyperclip duckduckgo-search
pip install requests-html selenium feedparser pywin32 wmi
```

## 🎯 **Usage Examples**

### **Voice Commands**

**Web Search & Information:**
- "Search for latest AI developments"
- "What's 15% of 250?" (instant calculations)
- "Latest news about technology"
- "Find YouTube videos about Python"
- "Current weather in Tokyo"

**Desktop & System Control:**
- "Show system information"
- "List running processes"
- "Take a screenshot"
- "Get clipboard content"
- "List open windows"
- "Show CPU usage"
- "Check memory usage"

**Basic System Control:**
- "Set volume to 50"
- "Volume up" / "Volume down"
- "Set brightness to 80"

### **Text Mode**
All voice commands work in text mode - just type them instead of speaking.

## ⚙️ **Configuration**

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
        "enabled_plugins": ["enhanced_websearch", "advanced_desktop", "weather", "system"]
    },
    "enhanced_websearch": {
        "max_results": 10,
        "enable_instant_answers": true,
        "enable_news": true,
        "timeout": 10
    },
    "advanced_desktop": {
        "screenshot_path": "./screenshots/",
        "enable_automation": true,
        "max_clipboard_history": 50
    }
}
```

## 🔌 **Plugin Development**

Create custom plugins by extending the BasePlugin class:

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
```

## 📁 **Project Structure**

```
Smart Local Assistant/
├── main_pro.py                    # Enhanced assistant main file
├── start_assistant.py             # Launcher script
├── voice_handler.py               # Voice recognition and TTS
├── advanced_plugin_manager.py     # Plugin system
├── config.json                    # Configuration
├── demo_enhanced_capabilities.py  # Feature demonstration
├── plugins/
│   ├── enhanced_websearch.py      # Real-time web search
│   ├── advanced_desktop.py        # Desktop integration
│   ├── weather.py                 # Weather information
│   └── system.py                  # System control
└── README.md
```

## 🧪 **Testing**

Run the comprehensive demo:
```bash
python demo_enhanced_capabilities.py
```

Test individual features:
```bash
python debug_test.py
python quick_test.py
```

## 🔧 **Troubleshooting**

### **Voice Recognition Issues**
- Check microphone permissions and default device
- Calibrate microphone with "calibrate microphone" command
- Verify speakers/headphones and TTS settings

### **Plugin Issues**
- Check for syntax errors in plugin files
- Clear Python cache: `rm -rf __pycache__ plugins/__pycache__`
- Verify the `can_handle()` method in your plugin

### **Dependencies**
- **PyAudio installation fails**: Install Microsoft Visual C++ Build Tools
- **Windows-specific features**: Requires `pywin32` and `wmi` packages

## 🎯 **Roadmap**

### ✅ **Completed Features**
- [x] Enhanced Web Search with real-time content reading
- [x] Advanced Desktop Integration and automation
- [x] Voice recognition and text-to-speech
- [x] Plugin architecture with auto-discovery
- [x] System monitoring and process management
- [x] Clipboard and window management
- [x] Screenshot capabilities and file operations

### 📋 **Planned Features**
- [ ] Web UI interface
- [ ] Calendar integration
- [ ] Email plugin
- [ ] Smart home integration
- [ ] Multi-language support
- [ ] Custom wake words
- [ ] Task automation workflows

## 🤝 **Contributing**

Contributions are welcome! Please feel free to:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

Inspired by and incorporates ideas from:
- **Microsoft TaskWeaver** - Plugin architecture concepts
- **Langchain-Chatchat** - RAG capabilities inspiration
- **LocalForge** - Local development agent concepts
- Various open-source voice assistant projects

## 📊 **Project Stats**

- **Languages**: Python 3.8+
- **Plugins**: 5+ built-in plugins
- **Commands**: 30+ voice/text commands
- **Platform**: Windows (with cross-platform potential)
- **Dependencies**: 15+ packages for enhanced functionality

---

**🚀 Ready to enhance your productivity with AI assistance!**

## 📞 **Support**

If you encounter any issues or have questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Search through existing [Issues](../../issues)
3. Create a new [Issue](../../issues/new) with detailed information

---

⭐ **Star this repository if you find it useful!**
