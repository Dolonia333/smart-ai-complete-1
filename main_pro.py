import plugin_loader
import requests
import os
import json
import sys
import argparse
import threading
import time
from voice_handler import VoiceHandler
from advanced_plugin_manager import AdvancedPluginManager

class SmartAssistantPro:
    def __init__(self, config=None):
        self.plugins = {}
        self.config = config if config else self.load_config()
        self.plugin_manager = AdvancedPluginManager()
        self.voice_handler = None
        self.voice_enabled = self.config.get("voice", {}).get("enabled", False)
        self.voice_wake_word = self.config.get("voice", {}).get("wake_word", "assistant")
        self.load_legacy_plugins()
        
        if self.voice_enabled:
            self.initialize_voice()
    
    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Config load failed: {e}, using defaults.")
            return {
                "ollama_enabled": True,
                "ollama_url": "http://localhost:11434/api/generate",
                "model": "deepseek-r1:14b",
                "fallback_to_simple": True,
                "voice_enabled": False,
                "voice_wake_word": "assistant",
                "tts_enabled": True,
                "advanced_plugins": True
            }
    
    def load_legacy_plugins(self):
        """Load legacy plugins for backward compatibility"""
        if os.path.exists("plugins"):
            self.plugins.update(plugin_loader.load_plugins("plugins"))
    
    def initialize_voice(self):
        """Initialize voice recognition and TTS"""
        try:
            self.voice_handler = VoiceHandler()
            print("Voice system initialized successfully!")
            
            if self.config.get("test_voice_on_startup", False):
                if self.voice_handler.test_voice_system():
                    print("Voice system test passed!")
                else:
                    print("Voice system test failed!")
                    
        except Exception as e:
            print(f"Voice initialization failed: {e}")
            self.voice_enabled = False
    
    def ask_ollama(self, prompt):
        if not self.config.get("ollama_enabled", True):
            return None
        try:
            response = requests.post(
                self.config["ollama_url"],
                json={
                    "model": self.config["model"],
                    "prompt": f"You are a helpful assistant. User request: {prompt}",
                    "stream": False
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            print(f"Ollama unavailable: {e}")
            return None if not self.config.get("fallback_to_simple", True) else ""

    def classify_intent(self, text, ai_response=None):
        combined_text = f"{text} {ai_response or ''}".lower()
        
        # First, try advanced plugin system
        if self.config.get("advanced_plugins", True):
            plugin = self.plugin_manager.find_plugin_for_command(text)
            if plugin:
                return {"action": "advanced_plugin", "plugin": plugin, "text": text}
        
        # Fallback to legacy classification
        if any(app in combined_text for app in ["photoshop", "ps"]):
            return {"action": "open_app", "app": "photoshop"}
        elif "discord" in combined_text:
            return {"action": "open_app", "app": "discord"}
        elif any(app in combined_text for app in ["browser", "chrome"]):
            return {"action": "open_app", "app": "chrome"}
        elif "weather" in combined_text:
            city = self.extract_city(text)
            return {"action": "weather", "city": city}
        elif any(plugin in combined_text for plugin in self.plugins):
            for plugin_name in self.plugins:
                if plugin_name in combined_text:
                    return {"action": "plugin", "plugin": plugin_name, "text": text}
        
        # Voice control commands
        if self.voice_enabled and any(word in combined_text for word in ["stop listening", "quiet", "silence"]):
            return {"action": "voice_control", "command": "stop"}
        elif any(word in combined_text for word in ["start listening", "listen", "wake up"]):
            return {"action": "voice_control", "command": "start"}
        
        # Assistant control commands
        if any(word in combined_text for word in ["help", "commands", "what can you do"]):
            return {"action": "help"}
        elif any(word in combined_text for word in ["plugins", "list plugins", "show plugins"]):
            return {"action": "list_plugins"}

        return {"action": "unknown", "text": text}

    def extract_city(self, text):
        if " in " in text:
            return text.split(" in ")[-1].strip()
        elif " for " in text:
            return text.split(" for ")[-1].strip()
        return "London"

    def handle_action(self, intent):
        action = intent["action"]

        if action == "advanced_plugin":
            try:
                result = intent["plugin"].handle_command(intent["text"])
                return result
            except Exception as e:
                return f"Error in plugin {intent['plugin'].name}: {e}"
        
        elif action == "open_app":
            return self.open_application(intent["app"])
        
        elif action == "weather":
            if "weather" in self.plugins:
                return self.plugins["weather"].get_weather(intent["city"])
            return "Weather plugin not available."
        
        elif action == "plugin":
            plugin = self.plugins[intent["plugin"]]
            if hasattr(plugin, 'handle_command'):
                return plugin.handle_command(intent["text"])
            return f"Plugin {intent['plugin']} loaded but no handler found."
        
        elif action == "voice_control":
            return self.handle_voice_control(intent["command"])
        
        elif action == "help":
            return self.get_help_text()
        
        elif action == "list_plugins":
            return self.list_all_plugins()
        
        else:
            return "I don't understand that command. Say 'help' for available commands."

    def handle_voice_control(self, command):
        """Handle voice control commands"""
        if not self.voice_handler:
            return "Voice system not available."
        
        if command == "stop":
            self.voice_handler.stop_listening()
            return "Voice listening stopped."
        elif command == "start":
            if not self.voice_handler.listening:
                self.start_voice_listening()
                return "Voice listening started."
            else:
                return "Voice listening is already active."
        
        return "Voice control command not recognized."
    
    def get_help_text(self):
        """Get help text with available commands"""
        help_text = """🤖 Smart AI Assistant Pro - Available Commands:

📱 Application Control:
   • "open photoshop" / "open discord" / "open chrome"
   • "open [app name]" - tries to find and open any application

🌤️ Weather:
   • "weather in [city]" - get current weather
   • "forecast for [city]" - get weather forecast

🔍 Web Search:
   • "search [query]" - Google search
   • "youtube [query]" - YouTube search
   • "wikipedia [topic]" - Wikipedia lookup
   • "open [website.com]" - open specific website

🖥️ System Control:
   • "volume up/down/mute" - control system volume
   • "brightness up/down" - control screen brightness
   • "list processes" - show running processes
   • "system info" - show CPU, memory, disk usage
   • "kill process [name]" - terminate a process

🎤 Voice Control (if enabled):
   • "stop listening" - disable voice recognition
   • "start listening" - enable voice recognition

🔧 Assistant Commands:
   • "help" - show this help text
   • "list plugins" - show all available plugins
   • "exit" - quit the assistant

💡 You can also just talk naturally, and I'll try to understand what you want!"""
        
        return help_text
    
    def list_all_plugins(self):
        """List all available plugins"""
        result = "📋 Available Plugins:\n\n"
        
        # Advanced plugins
        if self.plugin_manager.plugins:
            result += "🚀 Advanced Plugins:\n"
            for plugin in self.plugin_manager.list_plugins():
                status = "✅" if plugin['enabled'] else "❌"
                result += f"   {status} {plugin['name']}: {plugin['description']}\n"
                if plugin['commands']:
                    result += f"      Commands: {', '.join(plugin['commands'])}\n"
            result += "\n"
        
        # Legacy plugins
        if self.plugins:
            result += "🔧 Legacy Plugins:\n"
            for name, plugin in self.plugins.items():
                result += f"   • {name}: {getattr(plugin, 'description', 'Legacy plugin')}\n"
        
        return result

    def open_application(self, app_name):
        try:
            app_paths = {
                "photoshop": r'C:\\Program Files\\Adobe\\Adobe Photoshop 2023\\Photoshop.exe',
                "discord": "discord.exe",
                "chrome": "chrome.exe"
            }

            if app_name in app_paths:
                os.system(f'start "" "{app_paths[app_name]}"')
                return f"Opening {app_name}..."
            else:
                from utils import open_found_app
                return open_found_app(app_name)
        except Exception as e:
            return f"Error opening {app_name}: {e}"

    def process_command(self, user_input):
        print("Processing...")
        
        # Get AI response
        ai_response = self.ask_ollama(user_input)

        # Classify intent and handle action
        intent = self.classify_intent(user_input, ai_response)
        result = self.handle_action(intent)

        # If no specific action was taken, return AI response
        if intent["action"] == "unknown":
            final_result = ai_response or "Command not understood. Say 'help' for available commands."
        else:
            final_result = result

        # Speak result if voice is enabled
        if self.voice_enabled and self.voice_handler and self.config.get("tts_enabled", True):
            try:
                # Limit speech to reasonable length
                speech_text = final_result[:500] + "..." if len(final_result) > 500 else final_result
                self.voice_handler.speak(speech_text)
            except Exception as e:
                print(f"TTS error: {e}")

        return final_result

    def voice_command_callback(self, command):
        """Callback function for voice commands"""
        print(f"\n🎤 Voice command: {command}")
        result = self.process_command(command)
        print(f"Assistant: {result}")

    def start_voice_listening(self):
        """Start continuous voice listening"""
        if not self.voice_handler:
            print("Voice system not initialized.")
            return
        
        print(f"Starting voice listening with wake word: '{self.voice_wake_word}'")
        self.voice_handler.start_listening_background(
            self.voice_command_callback, 
            self.voice_wake_word
        )

    def start(self):
        """Start the assistant in interactive mode"""
        if self.voice_enabled:
            self.voice_interactive_mode()
        else:
            self.text_interactive_mode()
    
    def voice_only_mode(self):
        """Start in voice-only mode"""
        if not self.voice_handler:
            self.initialize_voice()
        
        print("🎙️ Voice-only mode active. Say 'assistant' to wake me up!")
        print("Say 'exit' or 'quit' to stop.")
        
        try:
            while True:
                command = self.voice_handler.listen_for_wake_word(self.voice_wake_word)
                if command and ("exit" in command.lower() or "quit" in command.lower()):
                    break
                
                if command:
                    response = self.process_input(command)
                    self.voice_handler.speak(response)
        
        except KeyboardInterrupt:
            print("\n👋 Voice mode stopped!")
    
    def text_only_mode(self):
        """Start in text-only mode"""
        print("💬 Text-Only Mode Active")
        print("Type 'help' for available commands or 'exit' to quit.")
        
        try:
            while True:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    break
                
                if user_input:
                    response = self.process_input(user_input)
                    print(f"🤖 Assistant: {response}")
        
        except KeyboardInterrupt:
            print("\n👋 Text mode stopped!")
    
    def voice_interactive_mode(self):
        """Interactive mode with voice support"""
        print("🎙️ Voice mode active! You can type or speak commands.")
        print("Say 'assistant' to use voice, or just type your commands.")
        print("Type 'exit' or say 'exit' to quit.")
        
        if self.voice_handler:
            # Start voice listening in background
            voice_thread = threading.Thread(target=self._voice_listener, daemon=True)
            voice_thread.start()
        
        try:
            while True:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    break
                
                if user_input:
                    response = self.process_input(user_input)
                    print(f"🤖 Assistant: {response}")
                    if self.voice_handler:
                        self.voice_handler.speak(response)
        
        except KeyboardInterrupt:
            print("\n👋 Interactive mode stopped!")
    
    def text_interactive_mode(self):
        """Interactive mode text-only"""
        self.text_only_mode()
    
    def _voice_listener(self):
        """Background voice listener for interactive mode"""
        try:
            while True:
                command = self.voice_handler.listen_for_wake_word(self.voice_wake_word)
                if command and command not in ['exit', 'quit']:
                    response = self.process_input(command)
                    print(f"\n🎙️ Voice: {command}")
                    print(f"🤖 Assistant: {response}")
                    self.voice_handler.speak(response)
                    print("💬 You: ", end="", flush=True)  # Re-prompt
        except Exception:
            pass  # Silent exit on thread termination

    def process_input(self, user_input):
        """Process input - alias for process_command for consistency"""
        return self.process_command(user_input)

def main():
    parser = argparse.ArgumentParser(description="Run Smart AI Assistant Pro")
    parser.add_argument("command", nargs="*", help="Run a command with the assistant.")
    parser.add_argument("--voice", action="store_true", help="Enable voice mode")
    parser.add_argument("--test-voice", action="store_true", help="Test voice system")
    args = parser.parse_args()

    assistant = SmartAssistantPro()
    
    # Override voice setting if specified
    if args.voice:
        assistant.voice_enabled = True
        assistant.initialize_voice()
    
    # Test voice system if requested
    if args.test_voice:
        if assistant.voice_handler:
            assistant.voice_handler.test_voice_system()
        else:
            print("Voice system not available for testing.")
        return

    if args.command:
        command_text = " ".join(args.command)
        print("Assistant:", assistant.process_command(command_text))
    else:
        print("🤖 Smart AI Assistant Pro is running!")
        print("Type 'help' for available commands or 'exit' to quit.")
        
        if assistant.voice_enabled:
            assistant.start_voice_listening()
            print(f"🎤 Voice recognition active. Say '{assistant.voice_wake_word}' to activate.")
        
        while True:
            try:
                user_input = input("\n💬 You: ")
                if user_input.lower() in ["exit", "quit", "bye"]:
                    if assistant.voice_handler:
                        assistant.voice_handler.stop_listening()
                    print("👋 Goodbye!")
                    break
                
                result = assistant.process_command(user_input)
                print(f"🤖 Assistant: {result}")
                
            except KeyboardInterrupt:
                if assistant.voice_handler:
                    assistant.voice_handler.stop_listening()
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
