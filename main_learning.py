#!/usr/bin/env python3
"""
Smart Assistant Pro with Self-Learning Capabilities
Enhanced AI Assistant that can search, learn, and teach itself new information
"""

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
from learning_assistant import LearningAssistantMixin

class SmartAssistantProLearning(LearningAssistantMixin):
    def __init__(self, config=None):
        # Initialize learning capabilities first
        LearningAssistantMixin.__init__(self)
        
        self.plugins = {}
        self.config = config if config else self.load_config()
        self.plugin_manager = AdvancedPluginManager()
        self.voice_handler = None
        self.voice_enabled = self.config.get("voice", {}).get("enabled", False)
        self.voice_wake_word = self.config.get("voice", {}).get("wake_word", "assistant")
        self.load_legacy_plugins()
        
        # Initialize learning from config
        self.learning_enabled = self.config.get("learning", {}).get("enabled", True)
        self.auto_learn_threshold = self.config.get("learning", {}).get("auto_learn_threshold", 0.7)
        
        if self.voice_enabled:
            self.initialize_voice()
        
        print("🧠 Smart Assistant Pro with Learning initialized!")
        
        # Show learning status
        if self.learning_enabled:
            print("✅ Self-learning enabled - I can search and learn new information!")
        else:
            print("❌ Self-learning disabled")
    
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
                "voice": {"enabled": False, "wake_word": "assistant"},
                "learning": {"enabled": True, "auto_learn_threshold": 0.7},
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
        except Exception as e:
            print(f"Voice initialization failed: {e}")
            self.voice_enabled = False
    
    def ask_ollama(self, prompt):
        """Get response from Ollama with enhanced learning context"""
        if not self.config.get("ollama_enabled", True):
            return None
        
        try:
            # Add learning context to the prompt
            enhanced_prompt = self.enhance_prompt_with_context(prompt)
            
            # Standard Ollama request
            response = requests.post(
                self.config["ollama_url"],
                json={
                    "model": self.config["model"],
                    "prompt": enhanced_prompt,
                    "stream": False
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                print(f"Ollama error: {response.status_code}")
                return None
        except Exception as e:
            print(f"Ollama unavailable: {e}")
            return None
    
    def enhance_prompt_with_context(self, prompt: str) -> str:
        """Enhance prompt with relevant knowledge from knowledge base"""
        try:
            # Check if we have relevant knowledge
            kb_plugin = self.plugin_manager.get_plugin("knowledge_base")
            if not kb_plugin:
                return prompt
            
            # Search for relevant context
            context = kb_plugin.search_knowledge(prompt)
            
            if context and "I don't have information" not in context:
                enhanced_prompt = f"""Context from my knowledge base: {context}

User question: {prompt}

Please provide a comprehensive answer using the context above and your knowledge. If the context is relevant, incorporate it into your response."""
                return enhanced_prompt
            
            return prompt
            
        except Exception as e:
            print(f"Error enhancing prompt: {e}")
            return prompt
    
    def process_input(self, user_input: str) -> str:
        """
        Main input processing with intelligent learning
        This replaces the standard process_command with learning capabilities
        """
        print("🧠 Processing with learning...")
        
        # Handle special learning commands first
        if user_input.lower().startswith(("learn", "remember", "what is", "who is", "explain")):
            kb_plugin = self.plugin_manager.get_plugin("knowledge_base")
            if kb_plugin:
                result = kb_plugin.handle_command(user_input)
                
                # If knowledge base found an answer, return it
                if result and "I don't have information" not in result:
                    return result
        
        # Handle learning control commands
        user_lower = user_input.lower()
        if "learning stats" in user_lower or "learning statistics" in user_lower:
            return self.get_learning_stats()
        elif "enable learning" in user_lower:
            return self.enable_learning()
        elif "disable learning" in user_lower:
            return self.disable_learning()
        elif "clear learning cache" in user_lower:
            return self.clear_learning_cache()
        
        # Check if this is a learning-worthy query
        if self.should_attempt_learning(user_input):
            # Try to get knowledge from knowledge base first
            kb_result = self.check_knowledge_base(user_input)
            if kb_result:
                print("📚 Found in knowledge base")
                return kb_result
        
        # Process with standard AI/plugin system
        standard_result = self.process_command_standard(user_input)
        
        # Check if the result indicates lack of knowledge
        if self.indicates_unknown(standard_result) and self.should_attempt_learning(user_input):
            print("🔍 Attempting to learn...")
            learned_result = self.attempt_auto_learning(user_input)
            if learned_result:
                return learned_result
        
        # Post-process to extract and store any new knowledge
        if self.learning_enabled:
            self.extract_and_store_knowledge(user_input, standard_result)
        
        return standard_result
    
    def process_command_standard(self, user_input: str) -> str:
        """Standard command processing (original logic)"""
        print("Processing...")
        
        # Get AI response
        ai_response = self.ask_ollama(user_input)

        # Classify intent and handle action
        intent = self.classify_intent(user_input, ai_response)
        result = self.handle_action(intent)

        # If no specific action was taken, return AI response
        if intent["action"] == "unknown":
            final_result = ai_response or "I don't understand that command. Say 'help' for available commands."
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
    
    def classify_intent(self, text, ai_response=None):
        """Enhanced intent classification with learning awareness"""
        combined_text = text.lower()
        
        # Learning and knowledge commands (highest priority)
        if any(cmd in combined_text for cmd in ["what is", "who is", "explain", "define", "tell me about"]):
            return {"action": "knowledge_query", "text": text}
        
        # Advanced plugin handling (higher priority)
        for plugin in self.plugin_manager.plugins.values():
            if plugin.enabled and plugin.can_handle(text):
                return {"action": "advanced_plugin", "plugin": plugin, "text": text}
        
        # Application opening
        if any(word in combined_text for word in ["open", "launch", "start", "run"]):
            app_indicators = ["photoshop", "discord", "chrome", "firefox", "notepad", "calculator", "paint"]
            for app in app_indicators:
                if app in combined_text:
                    return {"action": "open_app", "app": app}
            
            # Generic app opening
            words = text.split()
            if len(words) >= 2 and words[0].lower() == "open":
                return {"action": "open_app", "app": words[1]}
        
        # Weather queries
        if any(word in combined_text for word in ["weather", "temperature", "forecast"]):
            return {"action": "weather", "city": self.extract_city(text)}
        
        # Legacy plugin handling
        if self.plugins:
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
    
    def handle_action(self, intent):
        """Enhanced action handling with learning support"""
        action = intent["action"]

        if action == "knowledge_query":
            # Handle knowledge queries with learning
            kb_plugin = self.plugin_manager.get_plugin("knowledge_base")
            if kb_plugin:
                return kb_plugin.handle_command(intent["text"])
            else:
                return "Knowledge base not available."

        elif action == "advanced_plugin":
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
            return self.get_enhanced_help_text()
        
        elif action == "list_plugins":
            return self.list_all_plugins()
        
        else:
            return "I don't understand that command. Say 'help' for available commands."
    
    def get_enhanced_help_text(self):
        """Get enhanced help text including learning capabilities"""
        help_text = """🤖 Smart AI Assistant Pro with Learning - Available Commands:

🧠 Learning & Knowledge:
   • "what is [topic]" - Ask about anything, I'll search and learn if needed
   • "who is [person]" - Learn about people
   • "explain [concept]" - Get detailed explanations
   • "learn [topic]: [information]" - Teach me manually
   • "remember [information]" - Store information
   • "learning stats" - Show learning statistics
   • "enable/disable learning" - Control auto-learning

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
   • "show system info" - display system information
   • "list processes" - show running processes

🎙️ Voice Control (if enabled):
   • "assistant" - wake word to activate voice mode
   • "stop listening" - disable voice recognition
   • "start listening" - enable voice recognition

🔌 Plugin Management:
   • "list plugins" - show all available plugins
   • "plugin status" - show plugin information
   • "enable/disable [plugin]" - control plugins

💡 Tips:
   - I can learn new information automatically when you ask about topics I don't know
   - Try asking "what is artificial intelligence" to see learning in action
   - Use "learning stats" to see what I've learned so far"""

        return help_text
    
    # Copy the remaining methods from the original SmartAssistantPro class
    def extract_city(self, text):
        if " in " in text:
            return text.split(" in ")[-1].strip()
        elif " for " in text:
            return text.split(" for ")[-1].strip()
        return "London"

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
    
    def list_all_plugins(self):
        """List all available plugins including learning status"""
        result = "📋 Available Plugins:\n"
        
        # Advanced plugins
        if self.plugin_manager.plugins:
            result += "🚀 Advanced Plugins:\n"
            for name, plugin in self.plugin_manager.plugins.items():
                status = "✅" if plugin.enabled else "❌"
                commands = ", ".join(plugin.commands[:5])  # Show first 5 commands
                result += f"   {status} {name}: {plugin.description}\n"
                result += f"      Commands: {commands}\n"
        
        # Legacy plugins
        if self.plugins:
            result += "🔧 Legacy Plugins:\n"
            for name, plugin in self.plugins.items():
                result += f"   • {name}: Legacy plugin\n"
        
        # Learning status
        if self.learning_enabled:
            result += "\n🧠 Learning Status: ✅ Enabled (I can search and learn new information)\n"
        else:
            result += "\n🧠 Learning Status: ❌ Disabled\n"
        
        return result
    
    def open_application(self, app_name):
        """Open an application by name"""
        try:
            app_mappings = {
                "photoshop": ["photoshop", "adobe photoshop"],
                "discord": ["discord"],
                "chrome": ["chrome", "google chrome"],
                "firefox": ["firefox", "mozilla firefox"],
                "notepad": ["notepad"],
                "calculator": ["calc", "calculator"],
                "paint": ["mspaint", "paint"]
            }
            
            if app_name in app_mappings:
                import subprocess
                for variant in app_mappings[app_name]:
                    try:
                        subprocess.Popen([variant])
                        return f"Opened {app_name}"
                    except FileNotFoundError:
                        continue
                return f"Could not find {app_name}"
            else:
                from utils import open_found_app
                return open_found_app(app_name)
        except Exception as e:
            return f"Error opening {app_name}: {e}"
    
    # Voice mode methods (copied from original)
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
        print("💬 Text-Only Mode Active (with Learning)")
        print("Type 'help' for available commands or 'exit' to quit.")
        print("💡 Try: 'what is quantum computing' to see learning in action!")
        
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

def main():
    """Main function to run the enhanced learning assistant"""
    parser = argparse.ArgumentParser(description='Smart Assistant Pro with Learning')
    parser.add_argument('--no-voice', action='store_true', help='Disable voice recognition')
    parser.add_argument('--no-learning', action='store_true', help='Disable auto-learning')
    parser.add_argument('--text-only', action='store_true', help='Run in text-only mode')
    
    args = parser.parse_args()
    
    # Load config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except:
        config = {}
    
    # Apply command line overrides
    if args.no_voice:
        config.setdefault('voice', {})['enabled'] = False
    if args.no_learning:
        config.setdefault('learning', {})['enabled'] = False
    
    # Create enhanced assistant
    assistant = SmartAssistantProLearning(config)
    
    try:
        if args.text_only:
            assistant.text_only_mode()
        else:
            assistant.start()
    except KeyboardInterrupt:
        print("\n👋 Assistant shutting down...")

if __name__ == "__main__":
    main()
