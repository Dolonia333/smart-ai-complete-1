#!/usr/bin/env python3
"""Simple verification test for plugins."""

import sys
sys.path.append('.')

try:
    print("Testing plugin imports...")
    
    # Test enhanced websearch plugin
    from plugins.enhanced_websearch import create_plugin as create_web
    web_plugin = create_web()
    print(f"✅ Web Search Plugin: {web_plugin.name}")
    
    # Test advanced desktop plugin  
    from plugins.advanced_desktop import create_plugin as create_desktop
    desktop_plugin = create_desktop()
    print(f"✅ Desktop Plugin: {desktop_plugin.name}")
    
    # Test handle_command methods
    print(f"✅ Web Search has handle_command: {hasattr(web_plugin, 'handle_command')}")
    print(f"✅ Desktop has handle_command: {hasattr(desktop_plugin, 'handle_command')}")
    
    print("\n🎉 All plugins imported successfully!")
    print("🚀 Ready for GitHub upload!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
