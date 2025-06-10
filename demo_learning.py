#!/usr/bin/env python3
"""
Interactive Demo of Self-Learning Assistant
"""

import json
from main_learning import SmartAssistantProLearning

def main():
    """Run interactive learning demo"""
    print("🧠 Self-Learning AI Assistant Demo")
    print("=" * 50)
    
    # Create assistant with learning enabled
    config = {
        "ollama_enabled": False,  # Disable Ollama for demo
        "voice": {"enabled": False},
        "learning": {"enabled": True, "auto_learn_threshold": 0.7},
        "advanced_plugins": True
    }
    
    assistant = SmartAssistantProLearning(config)
    print("\n✅ Assistant ready!")
    
    # Demo commands
    demo_commands = [
        "help",
        "what is artificial intelligence",
        "learn Python: Python is a programming language",
        "what is Python",
        "learning stats",
        "list plugins"
    ]
    
    print("\n🎬 Running Learning Demo:")
    print("-" * 30)
    
    for cmd in demo_commands:
        print(f"\n💬 You: {cmd}")
        response = assistant.process_input(cmd)
        print(f"🤖 Assistant: {response}")
        print("-" * 30)
    
    print("\n🎉 Demo completed! The self-learning system is working!")

if __name__ == "__main__":
    main()
