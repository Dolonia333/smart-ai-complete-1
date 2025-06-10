"""
Advanced Desktop Integration Plugin
Provides comprehensive desktop PC control and monitoring capabilities.
Author: GitHub Copilot
"""

import os
import sys
import psutil
import platform
import subprocess
import time
import json
import glob
from datetime import datetime
from typing import Dict, List, Optional, Any
import pyautogui
import pyperclip
from PIL import Image
import threading

try:
    import win32api
    import win32con
    import win32gui
    import win32process
    import wmi
    HAS_WINDOWS = True
except ImportError:
    HAS_WINDOWS = False
    print("Windows-specific features disabled - pywin32/wmi not available")

class AdvancedDesktopPlugin:
    """Advanced desktop integration with full PC control capabilities."""
    
    def __init__(self):
        self.name = "Advanced Desktop"
        self.version = "2.0.0"
        self.description = "Full desktop PC integration and control"
        self.enabled = True
        
        # Initialize WMI connection for Windows
        self.wmi_conn = None
        if HAS_WINDOWS:
            try:
                self.wmi_conn = wmi.WMI()
            except Exception as e:
                print(f"WMI initialization failed: {e}")
        
        # PyAutoGUI safety settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # Command mappings
        self.commands = {
            # System Information
            "system_info": self.get_system_info,
            "hardware_info": self.get_hardware_info,
            "cpu_usage": self.get_cpu_usage,
            "memory_usage": self.get_memory_usage,
            "disk_usage": self.get_disk_usage,
            "network_info": self.get_network_info,
            "battery_status": self.get_battery_status,
            
            # Process Management
            "list_processes": self.list_processes,
            "process_details": self.get_process_details,
            "kill_process": self.kill_process,
            "start_program": self.start_program,
            
            # Window Management
            "list_windows": self.list_windows,
            "focus_window": self.focus_window,
            "close_window": self.close_window,
            "minimize_window": self.minimize_window,
            "maximize_window": self.maximize_window,
            
            # File Operations
            "search_files": self.search_files,
            "open_file": self.open_file,
            "create_folder": self.create_folder,
            "delete_file": self.delete_file,
            
            # Clipboard Operations
            "get_clipboard": self.get_clipboard,
            "set_clipboard": self.set_clipboard,
            "clipboard_history": self.get_clipboard_history,
            
            # Screen Operations
            "take_screenshot": self.take_screenshot,
            "screen_info": self.get_screen_info,
            
            # Automation
            "type_text": self.type_text,
            "click_at": self.click_at,
            "key_press": self.press_key,
            
            # Services
            "list_services": self.list_services,
            "service_status": self.get_service_status,
        }
        
        # Clipboard history (simple implementation)
        self.clipboard_history = []
        self.max_clipboard_history = 50
        
    def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """Execute a desktop command."""
        try:
            if command not in self.commands:
                return {
                    "success": False,
                    "error": f"Unknown command: {command}",
                    "available_commands": list(self.commands.keys())
                }
            
            result = self.commands[command](**kwargs)
            return {
                "success": True,
                "command": command,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "command": command,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def handle_command(self, command: str, **kwargs) -> str:
        """Handle command in natural language format (for compatibility with demo)."""
        try:
            # Parse natural language commands to map to specific methods
            command_lower = command.lower().strip()
            
            # System Information Commands
            if "system info" in command_lower or "system information" in command_lower:
                return self.get_system_info()
            elif "hardware info" in command_lower or "hardware" in command_lower:
                return self.get_hardware_info()
            elif "cpu usage" in command_lower or "cpu" in command_lower:
                return self.get_cpu_usage()
            elif "memory usage" in command_lower or "memory" in command_lower:
                return self.get_memory_usage()
            elif "disk usage" in command_lower or "disk" in command_lower:
                return self.get_disk_usage()
            elif "network" in command_lower or "network status" in command_lower:
                return self.get_network_info()
            elif "battery" in command_lower:
                return self.get_battery_status()
            
            # Process Management Commands
            elif "processes" in command_lower or "list processes" in command_lower:
                return self.list_processes()
            elif "kill process" in command_lower:
                parts = command_lower.split()
                if len(parts) > 2:
                    process_name = parts[-1]
                    return self.kill_process(process_name)
                return "❌ Please specify process name or PID to kill"
            elif "start program" in command_lower:
                parts = command.split()
                if len(parts) > 2:
                    program_path = " ".join(parts[2:])
                    return self.start_program(program_path)
                return "❌ Please specify program path to start"
            
            # Window Management Commands
            elif "windows list" in command_lower or "list windows" in command_lower:
                return self.list_windows()
            elif "focus window" in command_lower:
                parts = command.split()
                if len(parts) > 2:
                    window_title = " ".join(parts[2:])
                    return self.focus_window(window_title)
                return "❌ Please specify window title to focus"
            elif "close window" in command_lower:
                parts = command.split()
                if len(parts) > 2:
                    window_title = " ".join(parts[2:])
                    return self.close_window(window_title)
                return "❌ Please specify window title to close"
            
            # Clipboard Commands
            elif "clipboard set" in command_lower:
                parts = command.split("set", 1)
                if len(parts) > 1:
                    text = parts[1].strip()
                    return self.set_clipboard(text)
                return "❌ Please specify text to set in clipboard"
            elif "clipboard get" in command_lower or "clipboard" in command_lower:
                return self.get_clipboard()
            elif "clipboard history" in command_lower:
                return self.get_clipboard_history()
            
            # Screen Commands
            elif "screenshot" in command_lower:
                return self.take_screenshot()
            elif "screen info" in command_lower:
                return self.get_screen_info()
            
            # Services Commands
            elif "services" in command_lower or "list services" in command_lower:
                return self.list_services()
            elif "service status" in command_lower:
                parts = command.split()
                if len(parts) > 2:
                    service_name = parts[-1]
                    return self.get_service_status(service_name)
                return "❌ Please specify service name"
            
            # File Operations
            elif "search files" in command_lower:
                parts = command.split()
                if len(parts) > 2:
                    pattern = " ".join(parts[2:])
                    return self.search_files(pattern)
                return "❌ Please specify search pattern"
            elif "open file" in command_lower:
                parts = command.split()
                if len(parts) > 2:
                    file_path = " ".join(parts[2:])
                    return self.open_file(file_path)
                return "❌ Please specify file path to open"
            
            else:
                return f"❌ Unknown command: '{command}'\n\nUse 'help' to see available commands"
                
        except Exception as e:
            return f"❌ Error executing command '{command}': {str(e)}"
    
    # System Information Methods
    def get_system_info(self) -> str:
        """Get comprehensive system information."""
        try:
            info = []
            
            info.append("🖥️ **System Information**")
            info.append(f"Platform: {platform.system()} {platform.release()}")
            info.append(f"Architecture: {platform.architecture()[0]}")
            info.append(f"Processor: {platform.processor()}")
            info.append(f"Machine: {platform.machine()}")
            info.append(f"Node: {platform.node()}")
            
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            info.append(f"Boot Time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}")
            info.append(f"Current User: {os.getlogin()}")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error getting system info: {e}"
    
    def get_hardware_info(self) -> str:
        """Get detailed hardware information."""
        try:
            info = []
            info.append("🔧 **Hardware Information**")
            
            # CPU Information
            cpu_count = psutil.cpu_count()
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()
            
            info.append("\n**CPU:**")
            info.append(f"Physical cores: {cpu_count}")
            info.append(f"Total cores: {cpu_count_logical}")
            if cpu_freq:
                info.append(f"Max Frequency: {cpu_freq.max:.2f}Mhz")
                info.append(f"Current Frequency: {cpu_freq.current:.2f}Mhz")
            
            # Memory Information
            memory = psutil.virtual_memory()
            info.append("\n**Memory:**")
            info.append(f"Total: {self._bytes_to_human(memory.total)}")
            info.append(f"Available: {self._bytes_to_human(memory.available)}")
            info.append(f"Used: {self._bytes_to_human(memory.used)}")
            info.append(f"Percentage: {memory.percent}%")
            
            # Disk Information
            info.append("\n**Storage:**")
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    info.append(f"Drive {partition.device}")
                    info.append(f"  Total: {self._bytes_to_human(partition_usage.total)}")
                    info.append(f"  Used: {self._bytes_to_human(partition_usage.used)}")
                    info.append(f"  Free: {self._bytes_to_human(partition_usage.free)}")
                    info.append(f"  Percentage: {partition_usage.percent}%")
                except PermissionError:
                    info.append(f"Drive {partition.device}: Permission denied")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error getting hardware info: {e}"
    
    def get_cpu_usage(self) -> str:
        """Get current CPU usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_count_logical = psutil.cpu_count(logical=True)
            
            info = []
            info.append("🔧 **CPU Usage**")
            info.append(f"Overall Usage: {cpu_percent}%")
            info.append(f"Physical Cores: {cpu_count}")
            info.append(f"Logical Cores: {cpu_count_logical}")
            
            # Per-core usage
            per_cpu = psutil.cpu_percent(interval=1, percpu=True)
            info.append("\n**Per-Core Usage:**")
            for i, usage in enumerate(per_cpu):
                info.append(f"Core {i}: {usage}%")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error getting CPU usage: {e}"
    
    def get_memory_usage(self) -> str:
        """Get current memory usage."""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            info = []
            info.append("💾 **Memory Usage**")
            info.append(f"Total RAM: {self._bytes_to_human(memory.total)}")
            info.append(f"Available: {self._bytes_to_human(memory.available)}")
            info.append(f"Used: {self._bytes_to_human(memory.used)}")
            info.append(f"Percentage: {memory.percent}%")
            info.append(f"Free: {self._bytes_to_human(memory.free)}")
            
            info.append("\n**Swap Memory:**")
            info.append(f"Total: {self._bytes_to_human(swap.total)}")
            info.append(f"Used: {self._bytes_to_human(swap.used)}")
            info.append(f"Free: {self._bytes_to_human(swap.free)}")
            info.append(f"Percentage: {swap.percent}%")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error getting memory usage: {e}"
    
    def get_disk_usage(self) -> str:
        """Get disk usage for all partitions."""
        try:
            info = []
            info.append("💿 **Disk Usage**")
            
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    info.append(f"\n**Drive {partition.device}**")
                    info.append(f"Filesystem: {partition.fstype}")
                    info.append(f"Total: {self._bytes_to_human(partition_usage.total)}")
                    info.append(f"Used: {self._bytes_to_human(partition_usage.used)}")
                    info.append(f"Free: {self._bytes_to_human(partition_usage.free)}")
                    info.append(f"Percentage: {partition_usage.percent}%")
                except PermissionError:
                    info.append(f"\n**Drive {partition.device}**: Permission denied")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error getting disk usage: {e}"
    
    def get_network_info(self) -> str:
        """Get network information."""
        try:
            info = []
            info.append("🌐 **Network Information**")
            
            # Network interfaces
            interfaces = psutil.net_if_addrs()
            info.append(f"\n**Network Interfaces ({len(interfaces)} found):**")
            
            for interface_name, interface_addresses in interfaces.items():
                info.append(f"\n**{interface_name}:**")
                for address in interface_addresses:
                    if str(address.family) == 'AddressFamily.AF_INET':
                        info.append(f"  IP Address: {address.address}")
                        info.append(f"  Netmask: {address.netmask}")
                        info.append(f"  Broadcast IP: {address.broadcast}")
                    elif str(address.family) == 'AddressFamily.AF_PACKET':
                        info.append(f"  MAC Address: {address.address}")
                        info.append(f"  Netmask: {address.netmask}")
                        info.append(f"  Broadcast MAC: {address.broadcast}")
            
            # Network statistics
            net_io = psutil.net_io_counters()
            info.append("\n**Network Statistics:**")
            info.append(f"Bytes Sent: {self._bytes_to_human(net_io.bytes_sent)}")
            info.append(f"Bytes Received: {self._bytes_to_human(net_io.bytes_recv)}")
            info.append(f"Packets Sent: {net_io.packets_sent}")
            info.append(f"Packets Received: {net_io.packets_recv}")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error getting network info: {e}"
    
    def get_battery_status(self) -> str:
        """Get battery status."""
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                return "🔌 No battery detected (Desktop PC or no battery sensor)"
            
            info = []
            info.append("🔋 **Battery Status**")
            info.append(f"Charge: {battery.percent}%")
            info.append(f"Power plugged: {'Yes' if battery.power_plugged else 'No'}")
            
            if not battery.power_plugged:
                if battery.secsleft != psutil.POWER_TIME_UNLIMITED:
                    hours = battery.secsleft // 3600
                    minutes = (battery.secsleft % 3600) // 60
                    info.append(f"Time remaining: {hours}h {minutes}m")
                else:
                    info.append("Time remaining: Unlimited")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error getting battery status: {e}"
    
    # Process Management Methods
    def list_processes(self) -> str:
        """List running processes."""
        try:
            info = []
            info.append("⚙️ **Running Processes**")
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    proc_info['cpu_percent'] = proc.cpu_percent()
                    processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            info.append(f"\nTop 15 processes by CPU usage:")
            info.append("PID     | CPU%   | MEM%   | Name")
            info.append("-" * 50)
            
            for proc in processes[:15]:
                info.append(f"{proc['pid']:<7} | {proc['cpu_percent']:<6.1f} | {proc['memory_percent']:<6.1f} | {proc['name']}")
            
            info.append(f"\nTotal processes: {len(processes)}")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error listing processes: {e}"
    
    def get_process_details(self, pid: str) -> str:
        """Get details for a specific process."""
        try:
            pid = int(pid)
            proc = psutil.Process(pid)
            
            info = []
            info.append(f"🔍 **Process Details - PID {pid}**")
            info.append(f"Name: {proc.name()}")
            info.append(f"Status: {proc.status()}")
            info.append(f"CPU Percent: {proc.cpu_percent()}%")
            info.append(f"Memory Percent: {proc.memory_percent():.2f}%")
            info.append(f"Memory Usage: {self._bytes_to_human(proc.memory_info().rss)}")
            info.append(f"Create Time: {datetime.fromtimestamp(proc.create_time()).strftime('%Y-%m-%d %H:%M:%S')}")
            
            try:
                info.append(f"Command Line: {' '.join(proc.cmdline())}")
            except psutil.AccessDenied:
                info.append("Command Line: Access denied")
            
            return "\n".join(info)
            
        except psutil.NoSuchProcess:
            return f"❌ Process with PID {pid} not found"
        except ValueError:
            return f"❌ Invalid PID: {pid}"
        except Exception as e:
            return f"❌ Error getting process details: {e}"
    
    def kill_process(self, identifier: str) -> str:
        """Kill a process by PID or name."""
        try:
            # Try to convert to int (PID)
            try:
                pid = int(identifier)
                proc = psutil.Process(pid)
                proc.terminate()
                return f"✅ Process {pid} ({proc.name()}) terminated"
            except ValueError:
                # It's a process name
                killed_count = 0
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if proc.info['name'].lower() == identifier.lower():
                            proc.terminate()
                            killed_count += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                if killed_count > 0:
                    return f"✅ Terminated {killed_count} process(es) named '{identifier}'"
                else:
                    return f"❌ No processes found with name '{identifier}'"
                    
        except psutil.NoSuchProcess:
            return f"❌ Process not found: {identifier}"
        except psutil.AccessDenied:
            return f"❌ Access denied - cannot kill process: {identifier}"
        except Exception as e:
            return f"❌ Error killing process: {e}"
    
    def start_program(self, program_path: str, args: str = "") -> str:
        """Start a program or application."""
        try:
            command = f'"{program_path}" {args}'.strip()
            process = subprocess.Popen(command, shell=True)
            
            return f"✅ Started program: {program_path} (PID: {process.pid})"
            
        except Exception as e:
            return f"❌ Error starting program: {e}"
    
    # Window Management Methods (Windows only)
    def list_windows(self) -> str:
        """List all open windows."""
        if not HAS_WINDOWS:
            return "❌ Window management only available on Windows"
        
        try:
            windows = []
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if window_text:
                        windows.append((hwnd, window_text))
                return True
            
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            info = [f"🪟 **Open Windows ({len(windows)} found)**"]
            
            for i, (hwnd, title) in enumerate(windows[:15], 1):
                info.append(f"{i}. {title} (Handle: {hwnd})")
            
            if len(windows) > 15:
                info.append(f"... and {len(windows) - 15} more windows")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error listing windows: {e}"
    
    def focus_window(self, window_title: str) -> str:
        """Focus a window by title."""
        if not HAS_WINDOWS:
            return "❌ Window management only available on Windows"
        
        try:
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd == 0:
                return f"❌ Window '{window_title}' not found"
            
            win32gui.SetForegroundWindow(hwnd)
            return f"✅ Focused window: {window_title}"
            
        except Exception as e:
            return f"❌ Error focusing window: {e}"
    
    def close_window(self, window_title: str) -> str:
        """Close a window by title."""
        if not HAS_WINDOWS:
            return "❌ Window management only available on Windows"
        
        try:
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd == 0:
                return f"❌ Window '{window_title}' not found"
            
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            return f"✅ Closed window: {window_title}"
            
        except Exception as e:
            return f"❌ Error closing window: {e}"
    
    def minimize_window(self, window_title: str) -> str:
        """Minimize a window by title."""
        if not HAS_WINDOWS:
            return "❌ Window management only available on Windows"
        
        try:
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd == 0:
                return f"❌ Window '{window_title}' not found"
            
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            return f"✅ Minimized window: {window_title}"
            
        except Exception as e:
            return f"❌ Error minimizing window: {e}"
    
    def maximize_window(self, window_title: str) -> str:
        """Maximize a window by title."""
        if not HAS_WINDOWS:
            return "❌ Window management only available on Windows"
        
        try:
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd == 0:
                return f"❌ Window '{window_title}' not found"
            
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            return f"✅ Maximized window: {window_title}"
            
        except Exception as e:
            return f"❌ Error maximizing window: {e}"
    
    # File Operations
    def search_files(self, pattern: str, directory: str = None) -> str:
        """Search for files matching a pattern."""
        try:
            if directory is None:
                directory = os.path.expanduser("~")
            
            matches = []
            search_pattern = os.path.join(directory, "**", pattern)
            
            for filepath in glob.glob(search_pattern, recursive=True):
                matches.append(filepath)
                if len(matches) >= 20:  # Limit results
                    break
            
            info = []
            info.append(f"📁 **File Search Results for '{pattern}'**")
            info.append(f"Search directory: {directory}")
            info.append(f"Found {len(matches)} matches:")
            
            for match in matches:
                info.append(f"  {match}")
            
            if len(matches) >= 20:
                info.append("... (showing first 20 results)")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error searching files: {e}"
    
    def open_file(self, file_path: str) -> str:
        """Open a file with the default application."""
        try:
            if not os.path.exists(file_path):
                return f"❌ File not found: {file_path}"
            
            os.startfile(file_path)
            return f"✅ Opened file: {file_path}"
            
        except Exception as e:
            return f"❌ Error opening file: {e}"
    
    def create_folder(self, folder_path: str) -> str:
        """Create a new folder."""
        try:
            os.makedirs(folder_path, exist_ok=True)
            return f"✅ Created folder: {folder_path}"
            
        except Exception as e:
            return f"❌ Error creating folder: {e}"
    
    def delete_file(self, file_path: str) -> str:
        """Delete a file."""
        try:
            if not os.path.exists(file_path):
                return f"❌ File not found: {file_path}"
            
            os.remove(file_path)
            return f"✅ Deleted file: {file_path}"
            
        except Exception as e:
            return f"❌ Error deleting file: {e}"
    
    # Clipboard Operations
    def get_clipboard(self) -> str:
        """Get current clipboard content."""
        try:
            content = pyperclip.paste()
            if not content:
                return "📋 Clipboard is empty"
            
            # Add to history
            if content not in self.clipboard_history:
                self.clipboard_history.insert(0, content)
                self.clipboard_history = self.clipboard_history[:self.max_clipboard_history]
            
            return f"📋 **Clipboard Content:**\n{content}"
            
        except Exception as e:
            return f"❌ Error getting clipboard: {e}"
    
    def set_clipboard(self, text: str) -> str:
        """Set clipboard content."""
        try:
            pyperclip.copy(text)
            
            # Add to history
            if text not in self.clipboard_history:
                self.clipboard_history.insert(0, text)
                self.clipboard_history = self.clipboard_history[:self.max_clipboard_history]
            
            return f"✅ Set clipboard to: {text[:100]}{'...' if len(text) > 100 else ''}"
            
        except Exception as e:
            return f"❌ Error setting clipboard: {e}"
    
    def get_clipboard_history(self) -> str:
        """Get clipboard history."""
        try:
            if not self.clipboard_history:
                return "📋 No clipboard history available"
            
            info = []
            info.append(f"📋 **Clipboard History ({len(self.clipboard_history)} items)**")
            
            for i, item in enumerate(self.clipboard_history[:10], 1):
                preview = item[:50] + "..." if len(item) > 50 else item
                info.append(f"{i}. {preview}")
            
            if len(self.clipboard_history) > 10:
                info.append(f"... and {len(self.clipboard_history) - 10} more items")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error getting clipboard history: {e}"
    
    # Screen Operations
    def take_screenshot(self, filename: str = None) -> str:
        """Take a screenshot."""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            
            return f"📸 Screenshot saved: {filename}"
            
        except Exception as e:
            return f"❌ Error taking screenshot: {e}"
    
    def get_screen_info(self) -> str:
        """Get screen information."""
        try:
            screen_size = pyautogui.size()
            
            info = []
            info.append("🖥️ **Screen Information**")
            info.append(f"Resolution: {screen_size.width} x {screen_size.height}")
            
            # Get current mouse position
            mouse_pos = pyautogui.position()
            info.append(f"Mouse Position: ({mouse_pos.x}, {mouse_pos.y})")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error getting screen info: {e}"
    
    # Automation Methods
    def type_text(self, text: str) -> str:
        """Type text at the current cursor position."""
        try:
            pyautogui.typewrite(text)
            return f"⌨️ Typed: {text[:50]}{'...' if len(text) > 50 else ''}"
            
        except Exception as e:
            return f"❌ Error typing text: {e}"
    
    def click_at(self, x: int, y: int) -> str:
        """Click at specific coordinates."""
        try:
            pyautogui.click(x, y)
            return f"🖱️ Clicked at ({x}, {y})"
            
        except Exception as e:
            return f"❌ Error clicking: {e}"
    
    def press_key(self, key: str) -> str:
        """Press a specific key."""
        try:
            pyautogui.press(key)
            return f"⌨️ Pressed key: {key}"
            
        except Exception as e:
            return f"❌ Error pressing key: {e}"
    
    # Services Management (Windows only)
    def list_services(self) -> str:
        """List Windows services."""
        if not HAS_WINDOWS or not self.wmi_conn:
            return "❌ Service management only available on Windows with WMI"
        
        try:
            services = self.wmi_conn.Win32_Service()
            
            info = []
            info.append(f"🔧 **Windows Services ({len(services)} found)**")
            info.append("Name | State | Status | Start Mode")
            info.append("-" * 60)
            
            # Sort by name and show first 20
            sorted_services = sorted(services, key=lambda x: x.Name)
            for service in sorted_services[:20]:
                info.append(f"{service.Name[:20]:<20} | {service.State:<8} | {service.Status:<8} | {service.StartMode}")
            
            if len(services) > 20:
                info.append(f"... and {len(services) - 20} more services")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error listing services: {e}"
    
    def get_service_status(self, service_name: str) -> str:
        """Get status of a specific Windows service."""
        if not HAS_WINDOWS or not self.wmi_conn:
            return "❌ Service management only available on Windows with WMI"
        
        try:
            services = self.wmi_conn.Win32_Service(Name=service_name)
            
            if not services:
                return f"❌ Service '{service_name}' not found"
            
            service = services[0]
            
            info = []
            info.append(f"🔧 **Service Status: {service_name}**")
            info.append(f"Name: {service.Name}")
            info.append(f"Display Name: {service.DisplayName}")
            info.append(f"State: {service.State}")
            info.append(f"Status: {service.Status}")
            info.append(f"Start Mode: {service.StartMode}")
            info.append(f"Process ID: {service.ProcessId}")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error getting service status: {e}"
    
    # Helper Methods
    def _bytes_to_human(self, bytes_value: int) -> str:
        """Convert bytes to human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    def get_help(self) -> str:
        """Get help information for the plugin."""
        help_text = [
            "🖥️ **Advanced Desktop Integration Commands**",
            "",
            "🔧 **System Information:**",
            "• system_info - Get comprehensive system info",
            "• hardware_info - Get detailed hardware info", 
            "• cpu_usage - Get current CPU usage",
            "• memory_usage - Get current memory usage",
            "• disk_usage - Get disk usage for all drives",
            "• network_info - Get network information",
            "• battery_status - Get battery status (laptops)",
            "",
            "⚙️ **Process Management:**",
            "• list_processes - List running processes",
            "• process_details(pid) - Get details for specific process",
            "• kill_process(name/pid) - Kill a process",
            "• start_program(path) - Start a program",
            "",
            "🪟 **Window Management (Windows only):**",
            "• list_windows - List all open windows",
            "• focus_window(title) - Focus a window",
            "• close_window(title) - Close a window",
            "• minimize_window(title) - Minimize a window",
            "• maximize_window(title) - Maximize a window",
            "",
            "📁 **File Operations:**",
            "• search_files(pattern) - Search for files",
            "• open_file(path) - Open a file",
            "• create_folder(path) - Create a folder",
            "• delete_file(path) - Delete a file",
            "",
            "📋 **Clipboard Operations:**",
            "• get_clipboard - Get clipboard content",
            "• set_clipboard(text) - Set clipboard content",
            "• clipboard_history - Show clipboard history",
            "",
            "🖥️ **Screen & Automation:**",
            "• take_screenshot - Take a screenshot",
            "• screen_info - Get screen information",
            "• type_text(text) - Type text",
            "• click_at(x, y) - Click at coordinates",
            "• press_key(key) - Press a key",
            "",
            "🔧 **Services (Windows only):**",
            "• list_services - List Windows services",
            "• service_status(name) - Get service status"
        ]
        
        return "\n".join(help_text)

# Create plugin instance
def create_plugin():
    """Factory function to create plugin instance."""
    return AdvancedDesktopPlugin()

# Plugin registration
if __name__ == "__main__":
    plugin = create_plugin()
    print(f"Advanced Desktop Plugin v{plugin.version} loaded successfully!")
    print("Available commands:", len(plugin.commands))
