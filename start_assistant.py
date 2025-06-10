#!/usr/bin/env python3
"""
Smart Local Assistant Launcher
Enhanced AI Assistant with Voice Control and Advanced Plugin System

Usage:
    python start_assistant.py [mode]
    
Modes:
    pro     - Start the enhanced assistant with voice and all features (default)
    basic   - Start the original basic assistant
    voice   - Start with voice-only mode
    text    - Start with text-only mode
    setup   - Run initial setup and dependency check
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'speech_recognition',
        'pyttsx3',
        'pyaudio',
        'psutil',
        'beautifulsoup4',
        'wikipedia',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                return False
    
    print("✅ All dependencies are ready!")
    return True

def show_banner():
    """Show startup banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    🤖 Smart Local Assistant                  ║
║                   Enhanced AI Assistant with Learning        ║
║                                                              ║
║  🎙️  Voice Recognition  |  🔌 Advanced Plugins             ║
║  🌐 Web Search         |  ⚙️  System Control              ║
║  🌤️  Weather Info      |  🧠 Self-Learning Capabilities     ║
║  🚀 Ollama Integration |  📚 Knowledge Base                ║
╚══════════════════════════════════════════════════════════════╝
    """)

def main():
    parser = argparse.ArgumentParser(description='Smart Local Assistant Launcher')
    parser.add_argument('mode', nargs='?', default='learning', 
                       choices=['learning', 'pro', 'basic', 'voice', 'text', 'setup'],
                       help='Launch mode (default: learning)')
    parser.add_argument('--no-voice', action='store_true', 
                       help='Disable voice recognition')
    parser.add_argument('--no-learning', action='store_true', 
                       help='Disable auto-learning')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    show_banner()
    
    if args.mode == 'setup':
        print("🛠️  Running setup...")
        success = check_dependencies()
        if success:
            print("✅ Setup completed successfully!")
            print("You can now run: python start_assistant.py")
        else:
            print("❌ Setup failed. Please install missing dependencies manually.")
        return
    
    # Check dependencies before starting
    if not check_dependencies():
        print("❌ Cannot start assistant. Please run: python start_assistant.py setup")
        return
    
    print(f"🚀 Starting Smart Assistant in {args.mode.upper()} mode...")
    
    try:
        if args.mode == 'basic':
            print("📝 Starting Basic Assistant (Original)...")
            import main
            # The original main.py will handle the execution
            
        elif args.mode == 'pro':
            print("🎯 Starting Pro Assistant (Enhanced)...")
            
            # Import and configure
            from main_pro import SmartAssistantPro
            from voice_handler import VoiceHandler
            import json
            
            # Load config
            with open('config.json', 'r') as f:
                config = json.load(f)
              # Override voice setting if needed
            if args.no_voice:
                config['voice']['enabled'] = False
            
            # Create and start assistant
            assistant = SmartAssistantPro(config)
            assistant.start()
            
        elif args.mode == 'voice':
            print("🎙️  Starting Voice-Only Mode...")
            from main_pro import SmartAssistantPro
            import json
            
            with open('config.json', 'r') as f:
                config = json.load(f)
            
            config['voice']['enabled'] = True
            config['ui']['show_startup_banner'] = False
            assistant = SmartAssistantPro(config)
            assistant.voice_only_mode()
            
        elif args.mode == 'text':
            print("💬 Starting Text-Only Mode...")
            from main_pro import SmartAssistantPro
            import json
            
            with open('config.json', 'r') as f:
                config = json.load(f)
            
            config['voice']['enabled'] = False
            
            assistant = SmartAssistantPro(config)
            assistant.text_only_mode()
            
        elif args.mode == 'learning':
            print("🧠 Starting Learning Assistant (Self-Learning AI)...")
            
            # Import the learning assistant
            from main_learning import SmartAssistantProLearning
            import json
            
            # Load config
            with open('config.json', 'r') as f:
                config = json.load(f)
            
            # Override settings based on command line args
            if args.no_voice:
                config['voice']['enabled'] = False
            if args.no_learning:
                config['learning']['enabled'] = False
            
            # Create and start the learning assistant
            assistant = SmartAssistantProLearning(config)
            assistant.start()
            
    except KeyboardInterrupt:
        print("\n👋 Assistant shutting down...")
    except Exception as e:
        print(f"❌ Error starting assistant: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
