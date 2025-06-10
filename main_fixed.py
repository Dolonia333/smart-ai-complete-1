import plugin_loader
import requests
import os
import json
import sys
import argparse

class SmartAssistant:
    def __init__(self):
        self.plugins = {}
        self.config = self.load_config()
        self.load_plugins()

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
                "fallback_to_simple": True
            }

    def load_plugins(self):
        if os.path.exists("plugins"):
            self.plugins.update(plugin_loader.load_plugins("plugins"))

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

        return {"action": "unknown", "text": text}

    def extract_city(self, text):
        if " in " in text:
            return text.split(" in ")[-1].strip()
        elif " for " in text:
            return text.split(" for ")[-1].strip()
        return "London"

    def handle_action(self, intent):
        action = intent["action"]

        if action == "open_app":
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
        else:
            return "I don't understand that command."

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
        ai_response = self.ask_ollama(user_input)

        intent = self.classify_intent(user_input, ai_response)
        result = self.handle_action(intent)

        if intent["action"] == "unknown":
            return ai_response or "Command not understood."
        return result

def main():
    parser = argparse.ArgumentParser(description="Run SmartAssistant commands.")
    parser.add_argument("command", nargs="*", help="Run a command with the assistant.")
    args = parser.parse_args()

    assistant = SmartAssistant()

    if args.command:
        command_text = " ".join(args.command)
        print("Assistant:", assistant.process_command(command_text))
    else:
        print("Smart AI Assistant is running. Type 'exit' to quit.")
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() == "exit":
                print("Goodbye!")
                break
            print("Assistant:", assistant.process_command(user_input))

if __name__ == "__main__":
    main()
