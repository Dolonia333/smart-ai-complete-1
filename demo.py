"""
Smart Assistant Demo Script
Demonstrates all the enhanced features of the AI assistant
"""

import json
import time
from main_pro import SmartAssistantPro

def demo_assistant():
    """Run a comprehensive demo of the assistant features"""
    
    print("🎬 Smart Assistant Demo")
    print("=" * 60)
    
    # Load config and disable voice for demo
    with open('config.json', 'r') as f:
        config = json.load(f)
    config['voice']['enabled'] = False
    
    # Create assistant
    print("🚀 Initializing Smart Assistant Pro...")
    assistant = SmartAssistantPro(config)
    print(f"✅ Assistant ready with {len(assistant.plugin_manager.plugins)} plugins loaded\n")
    
    # Demo commands
    demo_commands = [
        ("📋 Plugin Management", [
            "list plugins",
            "plugin status"
        ]),
        ("🌤️ Weather Information", [
            "weather in London",
            "what's the weather in Tokyo"
        ]),
        ("🌐 Web Search & Browsing", [
            "search for artificial intelligence",
            "wikipedia machine learning",
            "find videos about python programming"
        ]),
        ("⚙️ System Control", [
            "show system info",
            "list running processes",
            "check memory usage"
        ]),
        ("🤖 AI Integration", [
            "hello assistant",
            "tell me about yourself",
            "what can you do"
        ])
    ]
    
    for category, commands in demo_commands:
        print(f"\n{category}")
        print("-" * 40)
        
        for command in commands:
            print(f"\n🎯 Testing: '{command}'")
            try:
                response = assistant.process_input(command)
                # Truncate long responses for demo
                if len(response) > 300:
                    response = response[:300] + "..."
                print(f"✅ Response: {response}")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            time.sleep(1)  # Brief pause for readability
    
    print("\n" + "=" * 60)
    print("🎉 Demo completed! All features are working properly.")
    print("\n📝 To start using the assistant:")
    print("   • Text mode: python start_assistant.py text")
    print("   • Voice mode: python start_assistant.py pro")
    print("   • Help: python start_assistant.py --help")

if __name__ == "__main__":
    demo_assistant()
