#!/usr/bin/env python3
"""
Smart Local AI Assistant - GUI Application
A beautiful desktop application with voice control and advanced capabilities.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys
import os
import json
from datetime import datetime
import queue
import subprocess

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from voice_handler import VoiceHandler
    from plugin_loader import load_plugins
    from plugins.enhanced_websearch import create_plugin as create_web_plugin
    from plugins.advanced_desktop import create_plugin as create_desktop_plugin
except ImportError as e:
    print(f"Import error: {e}")

class SmartAIAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Smart Local AI Assistant")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2b2b2b')
        
        # Initialize components
        self.voice_handler = None
        self.plugin_loader = None
        self.plugins = {}
        self.is_listening = False
        self.response_queue = queue.Queue()
        
        # Load configuration
        self.load_config()
        
        # Create the GUI
        self.create_gui()
        
        # Initialize plugins
        self.initialize_plugins()
        
        # Start the response processor
        self.process_responses()
        
    def load_config(self):
        """Load configuration from config.json"""
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                "wake_word": "assistant",
                "voice_enabled": True,
                "enabled_plugins": ["enhanced_websearch", "advanced_desktop"]
            }
    
    def create_gui(self):
        """Create the main GUI interface"""
        
        # Main header
        header_frame = tk.Frame(self.root, bg='#1e1e1e', height=80)
        header_frame.pack(fill='x', padx=10, pady=5)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="🤖 Smart Local AI Assistant", 
            font=('Arial', 20, 'bold'),
            fg='#00ff88',
            bg='#1e1e1e'
        )
        title_label.pack(pady=20)
        
        # Status frame
        status_frame = tk.Frame(self.root, bg='#2b2b2b', height=60)
        status_frame.pack(fill='x', padx=10, pady=5)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="🔴 Initializing...",
            font=('Arial', 12),
            fg='#ffaa00',
            bg='#2b2b2b'
        )
        self.status_label.pack(side='left', pady=15)
        
        # Voice control button
        self.voice_btn = tk.Button(
            status_frame,
            text="🎤 Start Voice Control",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#007acc',
            activebackground='#005c99',
            command=self.toggle_voice_control,
            padx=20,
            pady=5
        )
        self.voice_btn.pack(side='right', pady=10, padx=10)
        
        # Main content area
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left panel - Input and controls
        left_panel = tk.Frame(main_frame, bg='#1e1e1e', width=400)
        left_panel.pack(side='left', fill='y', padx=5, pady=5)
        left_panel.pack_propagate(False)
        
        # Input section
        input_label = tk.Label(
            left_panel,
            text="💬 Enter Command or Question:",
            font=('Arial', 12, 'bold'),
            fg='#00ff88',
            bg='#1e1e1e'
        )
        input_label.pack(pady=(20, 10))
        
        # Text input
        self.input_text = tk.Text(
            left_panel,
            height=4,
            font=('Arial', 11),
            bg='#3a3a3a',
            fg='white',
            insertbackground='white',
            wrap='word'
        )
        self.input_text.pack(fill='x', padx=20, pady=5)
        
        # Send button
        send_btn = tk.Button(
            left_panel,
            text="🚀 Send Command",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#00aa44',
            activebackground='#008833',
            command=self.send_command,
            padx=20,
            pady=8
        )
        send_btn.pack(pady=10)
        
        # Plugin status section
        plugin_label = tk.Label(
            left_panel,
            text="🔌 Available Plugins:",
            font=('Arial', 12, 'bold'),
            fg='#00ff88',
            bg='#1e1e1e'
        )
        plugin_label.pack(pady=(30, 10))
        
        # Plugin list
        self.plugin_listbox = tk.Listbox(
            left_panel,
            font=('Arial', 10),
            bg='#3a3a3a',
            fg='white',
            selectbackground='#007acc',
            height=8
        )
        self.plugin_listbox.pack(fill='x', padx=20, pady=5)
        
        # Right panel - Output
        right_panel = tk.Frame(main_frame, bg='#1e1e1e')
        right_panel.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # Output section
        output_label = tk.Label(
            right_panel,
            text="📋 Assistant Response:",
            font=('Arial', 12, 'bold'),
            fg='#00ff88',
            bg='#1e1e1e'
        )
        output_label.pack(pady=(20, 10))
        
        # Response display
        self.response_display = scrolledtext.ScrolledText(
            right_panel,
            font=('Consolas', 11),
            bg='#0a0a0a',
            fg='#00ff88',
            insertbackground='#00ff88',
            wrap='word',
            state='disabled'
        )
        self.response_display.pack(fill='both', expand=True, padx=20, pady=5)
        
        # Quick actions
        actions_frame = tk.Frame(right_panel, bg='#1e1e1e')
        actions_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Button(
            actions_frame,
            text="🔍 Web Search",
            font=('Arial', 10),
            bg='#007acc',
            fg='white',
            command=lambda: self.quick_command("search current news")
        ).pack(side='left', padx=5)
        
        tk.Button(
            actions_frame,
            text="🖥️ System Info",
            font=('Arial', 10),
            bg='#aa4400',
            fg='white',
            command=lambda: self.quick_command("system info")
        ).pack(side='left', padx=5)
        
        tk.Button(
            actions_frame,
            text="📋 Clear",
            font=('Arial', 10),
            bg='#666666',
            fg='white',
            command=self.clear_response
        ).pack(side='right', padx=5)
        
        # Footer
        footer_frame = tk.Frame(self.root, bg='#1e1e1e', height=40)
        footer_frame.pack(fill='x', padx=10, pady=5)
        footer_frame.pack_propagate(False)
        
        footer_label = tk.Label(
            footer_frame,
            text="Smart Local AI Assistant v2.0 | Enhanced with Web Search & Desktop Control",
            font=('Arial', 9),
            fg='#888888',
            bg='#1e1e1e'
        )
        footer_label.pack(pady=10)
        
    def initialize_plugins(self):
        """Initialize all plugins"""
        try:
            # Initialize enhanced web search plugin
            self.web_plugin = create_web_plugin()
            self.plugins['enhanced_websearch'] = self.web_plugin
            
            # Initialize advanced desktop plugin
            self.desktop_plugin = create_desktop_plugin()
            self.plugins['advanced_desktop'] = self.desktop_plugin
            
            # Update plugin list
            self.update_plugin_list()
            
            # Update status
            self.update_status("🟢 Ready - Plugins loaded successfully")
            
        except Exception as e:
            self.update_status(f"⚠️ Plugin initialization error: {str(e)}")
            self.log_response(f"Error initializing plugins: {str(e)}")
    
    def update_plugin_list(self):
        """Update the plugin list display"""
        self.plugin_listbox.delete(0, tk.END)
        for name, plugin in self.plugins.items():
            status = "✅" if plugin else "❌"
            display_name = getattr(plugin, 'name', name) if plugin else name
            self.plugin_listbox.insert(tk.END, f"{status} {display_name}")
    
    def toggle_voice_control(self):
        """Toggle voice control on/off"""
        if not self.is_listening:
            self.start_voice_control()
        else:
            self.stop_voice_control()
    
    def start_voice_control(self):
        """Start voice control"""
        try:
            if not self.voice_handler:
                from voice_handler import VoiceHandler
                self.voice_handler = VoiceHandler()
            
            self.is_listening = True
            self.voice_btn.config(
                text="🔴 Stop Voice Control",
                bg='#cc0000',
                activebackground='#990000'
            )
            self.update_status("🎤 Listening for voice commands...")
            
            # Start voice listening in a separate thread
            voice_thread = threading.Thread(target=self.voice_listening_loop)
            voice_thread.daemon = True
            voice_thread.start()
            
        except Exception as e:
            self.update_status(f"⚠️ Voice control error: {str(e)}")
            messagebox.showerror("Voice Control Error", f"Could not start voice control:\n{str(e)}")
    
    def stop_voice_control(self):
        """Stop voice control"""
        self.is_listening = False
        self.voice_btn.config(
            text="🎤 Start Voice Control",
            bg='#007acc',
            activebackground='#005c99'
        )
        self.update_status("🟢 Voice control stopped")
    
    def voice_listening_loop(self):
        """Voice listening loop"""
        while self.is_listening:
            try:
                if self.voice_handler:
                    command = self.voice_handler.listen_for_command()
                    if command and command.strip():
                        self.response_queue.put(('voice_command', command))
                        self.response_queue.put(('log', f"🎤 Voice command: {command}"))
            except Exception as e:
                self.response_queue.put(('log', f"Voice error: {str(e)}"))
    
    def send_command(self):
        """Send text command"""
        command = self.input_text.get("1.0", tk.END).strip()
        if command:
            self.input_text.delete("1.0", tk.END)
            self.process_command(command)
    
    def quick_command(self, command):
        """Execute a quick command"""
        self.process_command(command)
    
    def process_command(self, command):
        """Process a command using appropriate plugin"""
        self.log_response(f"\n💬 User: {command}")
        self.update_status("🔄 Processing command...")
        
        # Process in separate thread to avoid blocking UI
        thread = threading.Thread(target=self.execute_command, args=(command,))
        thread.daemon = True
        thread.start()
    
    def execute_command(self, command):
        """Execute command with plugins"""
        try:
            command_lower = command.lower()
            response = ""
            
            # Determine which plugin to use
            if any(keyword in command_lower for keyword in ['search', 'google', 'news', 'weather', 'youtube', 'instant']):
                if 'enhanced_websearch' in self.plugins:
                    response = self.plugins['enhanced_websearch'].handle_command(command)
                else:
                    response = "❌ Web search plugin not available"
                    
            elif any(keyword in command_lower for keyword in ['system', 'process', 'window', 'clipboard', 'screenshot', 'hardware']):
                if 'advanced_desktop' in self.plugins:
                    response = self.plugins['advanced_desktop'].handle_command(command)
                else:
                    response = "❌ Desktop plugin not available"
                    
            else:
                # Try both plugins for general commands
                if 'enhanced_websearch' in self.plugins:
                    response = self.plugins['enhanced_websearch'].handle_command(command)
                elif 'advanced_desktop' in self.plugins:
                    response = self.plugins['advanced_desktop'].handle_command(command)
                else:
                    response = "❌ No suitable plugin found for this command"
            
            self.response_queue.put(('response', response))
            self.response_queue.put(('status', "🟢 Command completed"))
            
        except Exception as e:
            error_msg = f"❌ Error processing command: {str(e)}"
            self.response_queue.put(('response', error_msg))
            self.response_queue.put(('status', "⚠️ Command failed"))
    
    def process_responses(self):
        """Process responses from the queue"""
        try:
            while True:
                try:
                    msg_type, content = self.response_queue.get_nowait()
                    
                    if msg_type == 'response':
                        self.log_response(f"🤖 Assistant: {content}")
                    elif msg_type == 'log':
                        self.log_response(content)
                    elif msg_type == 'status':
                        self.update_status(content)
                    elif msg_type == 'voice_command':
                        self.process_command(content)
                        
                except queue.Empty:
                    break
                    
        except Exception as e:
            print(f"Queue processing error: {e}")
        
        # Schedule next check
        self.root.after(100, self.process_responses)
    
    def log_response(self, message):
        """Add message to response display"""
        self.response_display.config(state='normal')
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.response_display.insert(tk.END, f"[{timestamp}] {message}\n\n")
        
        # Auto-scroll to bottom
        self.response_display.see(tk.END)
        self.response_display.config(state='disabled')
    
    def update_status(self, status):
        """Update status label"""
        self.status_label.config(text=status)
    
    def clear_response(self):
        """Clear the response display"""
        self.response_display.config(state='normal')
        self.response_display.delete("1.0", tk.END)
        self.response_display.config(state='disabled')

def main():
    """Main function to run the GUI application"""
    root = tk.Tk()
    
    # Set window icon (if available)
    try:
        root.iconbitmap("icon.ico")
    except:
        pass
    
    # Create and run the application
    app = SmartAIAssistantGUI(root)
    
    # Add welcome message
    app.log_response("🚀 Smart Local AI Assistant Started!")
    app.log_response("💡 You can type commands or use voice control")
    app.log_response("🔍 Try: 'search latest news' or 'system info'")
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main()
