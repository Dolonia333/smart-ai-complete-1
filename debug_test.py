#!/usr/bin/env python3
print("=== Enhanced Plugin Test Starting ===")

import sys
import os
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# Add current directory to path
sys.path.insert(0, os.getcwd())
print("Added current directory to Python path")

try:
    print("Attempting to import enhanced_websearch...")
    from plugins.enhanced_websearch import EnhancedWebSearchPlugin
    print("✅ Enhanced WebSearch plugin imported successfully")
    
    search_plugin = EnhancedWebSearchPlugin()
    print(f"📋 Available commands: {search_plugin.commands}")
    print("Enhanced WebSearch plugin initialized")
    
except Exception as e:
    print(f"❌ Enhanced WebSearch import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\nAttempting to import advanced_desktop...")
    from plugins.advanced_desktop import AdvancedDesktopPlugin
    print("✅ Advanced Desktop plugin imported successfully")
    
    desktop_plugin = AdvancedDesktopPlugin()
    print(f"🖥️ Available commands: {desktop_plugin.commands}")
    print("Advanced Desktop plugin initialized")
    
except Exception as e:
    print(f"❌ Advanced Desktop import failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")
