#!/usr/bin/env python3
"""
Smart AI Assistant Launcher
A simple launcher script for the Smart Local AI Assistant
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import speech_recognition
        import pyttsx3
        import requests
        import bs4
        return True
    except ImportError as e:
        return False, str(e)

def install_dependencies():
    """Install required dependencies"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True
    except subprocess.CalledProcessError:
        return False

def launch_gui():
    """Launch the GUI application"""
    try:
        from gui_app import SmartAIAssistantGUI
        root = tk.Tk()
        app = SmartAIAssistantGUI(root)
        root.mainloop()
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch GUI: {str(e)}")
        return False

def main():
    """Main launcher function"""
    print("🤖 Smart Local AI Assistant Launcher")
    print("=====================================")
    
    # Check if we're in the right directory
    if not os.path.exists("gui_app.py"):
        print("❌ Error: gui_app.py not found!")
        print("Please run this script from the Smart Local AI Assistant directory.")
        input("Press Enter to exit...")
        return
    
    # Check dependencies
    deps_result = check_dependencies()
    if deps_result != True:
        print("⚠️  Missing dependencies detected!")
        print("Installing required packages...")
        
        if install_dependencies():
            print("✅ Dependencies installed successfully!")
        else:
            print("❌ Failed to install dependencies!")
            print("Please run: pip install -r requirements.txt")
            input("Press Enter to exit...")
            return
    
    print("🚀 Launching Smart AI Assistant...")
    
    # Launch the GUI
    if launch_gui():
        print("✅ Application closed successfully!")
    else:
        print("❌ Application encountered an error!")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
