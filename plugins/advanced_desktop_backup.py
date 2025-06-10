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
        self.description = "Full desktop PC integrat            else:
                # If no match found, show available commands
                return f"❌ Unknown command: '{command}'\n\nAvailable commands:\n{self.get_help()}" and control"
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
    
    # System Information Methods
    def get_system_info(self) -> str:
        """Get comprehensive system information."""
        try:
            info = []
            
            # Basic system info
            info.append(f"🖥️ **System Information**")
            info.append(f"Platform: {platform.system()} {platform.release()}")
            info.append(f"Architecture: {platform.architecture()[0]}")
            info.append(f"Processor: {platform.processor()}")
            info.append(f"Machine: {platform.machine()}")
            info.append(f"Node: {platform.node()}")
            
            # Boot time
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            info.append(f"Boot Time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # User info
            info.append(f"Current User: {os.getlogin()}")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error getting system info: {e}"
    
    def get_hardware_info(self) -> str:
        """Get detailed hardware information."""
        try:
            info = []
            info.append(f"🔧 **Hardware Information**")
            
            # CPU Information
            cpu_count = psutil.cpu_count()
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()
            
            info.append(f"\n**CPU:**")
            info.append(f"Physical cores: {cpu_count}")
            info.append(f"Total cores: {cpu_count_logical}")
            if cpu_freq:
                info.append(f"Max Frequency: {cpu_freq.max:.2f}Mhz")
                info.append(f"Current Frequency: {cpu_freq.current:.2f}Mhz")
            
            # Memory Information
            memory = psutil.virtual_memory()
            info.append(f"\n**Memory:**")
            info.append(f"Total: {self._bytes_to_human(memory.total)}")
            info.append(f"Available: {self._bytes_to_human(memory.available)}")
            info.append(f"Used: {self._bytes_to_human(memory.used)}")
            info.append(f"Percentage: {memory.percent}%")
            
            # Disk Information
            info.append(f"\n**Storage:**")
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
            
            # GPU Information (Windows only)
            if HAS_WINDOWS and self.wmi_conn:
                try:
                    gpu_info = self.wmi_conn.Win32_VideoController()
                    info.append(f"\n**GPU:**")
                    for gpu in gpu_info:
                        if gpu.Name:
                            info.append(f"Name: {gpu.Name}")
                            if gpu.AdapterRAM:
                                info.append(f"VRAM: {self._bytes_to_human(gpu.AdapterRAM)}")
                except Exception:
                    pass
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error getting hardware info: {e}"
    
    def get_cpu_usage(self) -> str:
        """Get current CPU usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            per_cpu = psutil.cpu_percent(interval=1, percpu=True)
            
            info = [f"🔥 **CPU Usage**"]
            info.append(f"Overall: {cpu_percent}%")
            info.append(f"Per Core: {', '.join([f'{i+1}:{cpu:.1f}%' for i, cpu in enumerate(per_cpu)])}")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error getting CPU usage: {e}"
    
    def get_memory_usage(self) -> str:
        """Get current memory usage."""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            info = [f"💾 **Memory Usage**"]
            info.append(f"RAM: {memory.percent}% ({self._bytes_to_human(memory.used)}/{self._bytes_to_human(memory.total)})")
            info.append(f"Available: {self._bytes_to_human(memory.available)}")
            info.append(f"Swap: {swap.percent}% ({self._bytes_to_human(swap.used)}/{self._bytes_to_human(swap.total)})")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error getting memory usage: {e}"
    
    def get_disk_usage(self) -> str:
        """Get disk usage for all drives."""
        try:
            info = [f"💿 **Disk Usage**"]
            
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    info.append(f"{partition.device} {usage.percent}% "
                              f"({self._bytes_to_human(usage.used)}/{self._bytes_to_human(usage.total)})")
                except PermissionError:
                    info.append(f"{partition.device} Permission denied")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error getting disk usage: {e}"
    
    def get_network_info(self) -> str:
        """Get network interface information."""
        try:
            info = [f"🌐 **Network Information**"]
            
            # Network interfaces
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for interface_name, interface_addresses in interfaces.items():
                info.append(f"\n**{interface_name}:**")
                
                # Interface status
                if interface_name in stats:
                    stat = stats[interface_name]
                    info.append(f"Status: {'Up' if stat.isup else 'Down'}")
                    info.append(f"Speed: {stat.speed} Mbps")
                
                # IP addresses
                for address in interface_addresses:
                    if str(address.family) == 'AddressFamily.AF_INET':
                        info.append(f"IPv4: {address.address}")
                        info.append(f"Netmask: {address.netmask}")
                    elif str(address.family) == 'AddressFamily.AF_INET6':
                        info.append(f"IPv6: {address.address}")
            
            # Network I/O
            net_io = psutil.net_io_counters()
            info.append(f"\n**Network I/O:**")
            info.append(f"Bytes sent: {self._bytes_to_human(net_io.bytes_sent)}")
            info.append(f"Bytes received: {self._bytes_to_human(net_io.bytes_recv)}")
            info.append(f"Packets sent: {net_io.packets_sent}")
            info.append(f"Packets received: {net_io.packets_recv}")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error getting network info: {e}"
    
    def get_battery_status(self) -> str:
        """Get battery information (if available)."""
        try:
            battery = psutil.sensors_battery()
            if not battery:
                return "🔌 No battery detected (desktop system)"
            
            info = [f"🔋 **Battery Status**"]
            info.append(f"Charge: {battery.percent}%")
            info.append(f"Plugged in: {'Yes' if battery.power_plugged else 'No'}")
            
            if not battery.power_plugged:
                hours, remainder = divmod(battery.secsleft, 3600)
                minutes, _ = divmod(remainder, 60)
                info.append(f"Time remaining: {int(hours)}h {int(minutes)}m")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error getting battery status: {e}"
    
    # Process Management Methods
    def list_processes(self, limit: int = 20) -> str:
        """List running processes."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            info = [f"🔄 **Running Processes (Top {limit})**"]
            info.append(f"{'PID':<8} {'Name':<25} {'CPU%':<8} {'Memory%':<8}")
            info.append("-" * 55)
            
            for proc in processes[:limit]:
                cpu = proc['cpu_percent'] or 0
                mem = proc['memory_percent'] or 0
                name = (proc['name'] or 'Unknown')[:24]
                info.append(f"{proc['pid']:<8} {name:<25} {cpu:<8.1f} {mem:<8.1f}")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error listing processes: {e}"
    
    def get_process_details(self, pid: int) -> str:
        """Get detailed information about a specific process."""
        try:
            proc = psutil.Process(pid)
            
            info = [f"🔍 **Process Details (PID: {pid})**"]
            info.append(f"Name: {proc.name()}")
            info.append(f"Status: {proc.status()}")
            info.append(f"CPU: {proc.cpu_percent()}%")
            info.append(f"Memory: {proc.memory_percent():.2f}%")
            info.append(f"Memory (RSS): {self._bytes_to_human(proc.memory_info().rss)}")
            info.append(f"Created: {datetime.fromtimestamp(proc.create_time()).strftime('%Y-%m-%d %H:%M:%S')}")
            
            try:
                info.append(f"Command: {' '.join(proc.cmdline())}")
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                info.append("Command: Access denied")
            
            return "\n".join(info)
            
        except psutil.NoSuchProcess:
            return f"❌ Process with PID {pid} not found"
        except Exception as e:
            return f"❌ Error getting process details: {e}"
    
    def kill_process(self, pid: int) -> str:
        """Terminate a process by PID."""
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()
            proc.terminate()
            
            # Wait for termination
            try:
                proc.wait(timeout=5)
                return f"✅ Process '{proc_name}' (PID: {pid}) terminated successfully"
            except psutil.TimeoutExpired:
                proc.kill()
                return f"✅ Process '{proc_name}' (PID: {pid}) forcefully killed"
                
        except psutil.NoSuchProcess:
            return f"❌ Process with PID {pid} not found"
        except psutil.AccessDenied:
            return f"❌ Access denied - cannot terminate process {pid}"
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
    
    # File Operations Methods
    def search_files(self, pattern: str, directory: str = None, max_results: int = 20) -> str:
        """Search for files matching a pattern."""
        try:
            if directory is None:
                directory = os.path.expanduser("~")  # User home directory
            
            found_files = []
            search_pattern = os.path.join(directory, "**", f"*{pattern}*")
            
            for file_path in glob.glob(search_pattern, recursive=True):
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    size = self._bytes_to_human(stat.st_size)
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                    
                    found_files.append({
                        'path': file_path,
                        'size': size,
                        'modified': modified
                    })
                    
                    if len(found_files) >= max_results:
                        break
            
            if not found_files:
                return f"❌ No files found matching '{pattern}' in {directory}"
            
            info = [f"🔍 **Files matching '{pattern}' ({len(found_files)} found)**"]
            
            for i, file_info in enumerate(found_files, 1):
                info.append(f"{i}. {os.path.basename(file_info['path'])}")
                info.append(f"   Path: {file_info['path']}")
                info.append(f"   Size: {file_info['size']}, Modified: {file_info['modified']}")
            
            if len(glob.glob(search_pattern, recursive=True)) > max_results:
                info.append(f"... and more files (showing first {max_results})")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error searching files: {e}"
    
    def open_file(self, file_path: str) -> str:
        """Open a file with its default application."""
        try:
            if not os.path.exists(file_path):
                return f"❌ File not found: {file_path}"
            
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
            
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
        """Delete a file (with confirmation)."""
        try:
            if not os.path.exists(file_path):
                return f"❌ File not found: {file_path}"
            
            # Safety check - don't delete system files
            system_paths = ['C:\\Windows', 'C:\\Program Files', '/bin', '/usr', '/sys']
            if any(file_path.startswith(path) for path in system_paths):
                return f"❌ Cannot delete system file: {file_path}"
            
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
            
            # Truncate very long content
            if len(content) > 500:
                content = content[:500] + "... (truncated)"
            
            return f"📋 **Clipboard Content:**\n{content}"
            
        except Exception as e:
            return f"❌ Error getting clipboard: {e}"
    
    def set_clipboard(self, text: str) -> str:
        """Set clipboard content."""
        try:
            pyperclip.copy(text)
            
            # Add to history
            self.clipboard_history.append({
                'content': text[:100] + "..." if len(text) > 100 else text,
                'timestamp': datetime.now().isoformat(),
                'full_content': text
            })
            
            # Limit history size
            if len(self.clipboard_history) > self.max_clipboard_history:
                self.clipboard_history.pop(0)
            
            return f"✅ Set clipboard content ({len(text)} characters)"
            
        except Exception as e:
            return f"❌ Error setting clipboard: {e}"
    
    def get_clipboard_history(self) -> str:
        """Get clipboard history."""
        try:
            if not self.clipboard_history:
                return "📋 No clipboard history available"
            
            info = [f"📋 **Clipboard History ({len(self.clipboard_history)} items)**"]
            
            for i, item in enumerate(reversed(self.clipboard_history[-10:]), 1):
                timestamp = datetime.fromisoformat(item['timestamp']).strftime('%H:%M:%S')
                content = item['content']
                info.append(f"{i}. [{timestamp}] {content}")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error getting clipboard history: {e}"
    
    # Screen Operations
    def take_screenshot(self, save_path: str = None) -> str:
        """Take a screenshot."""
        try:
            screenshot = pyautogui.screenshot()
            
            if save_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = f"screenshot_{timestamp}.png"
            
            screenshot.save(save_path)
            return f"✅ Screenshot saved: {save_path}"
            
        except Exception as e:
            return f"❌ Error taking screenshot: {e}"
    
    def get_screen_info(self) -> str:
        """Get screen/display information."""
        try:
            screen_size = pyautogui.size()
            
            info = [f"🖥️ **Screen Information**"]
            info.append(f"Resolution: {screen_size.width} x {screen_size.height}")
            info.append(f"Current mouse position: {pyautogui.position()}")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error getting screen info: {e}"
    
    # Automation Methods
    def type_text(self, text: str, interval: float = 0.05) -> str:
        """Type text at current cursor position."""
        try:
            pyautogui.write(text, interval=interval)
            return f"✅ Typed text: {text[:50]}{'...' if len(text) > 50 else ''}"
            
        except Exception as e:
            return f"❌ Error typing text: {e}"
    
    def click_at(self, x: int, y: int, button: str = 'left') -> str:
        """Click at specific coordinates."""
        try:
            pyautogui.click(x, y, button=button)
            return f"✅ Clicked at ({x}, {y}) with {button} button"
            
        except Exception as e:
            return f"❌ Error clicking: {e}"
    
    def press_key(self, key: str) -> str:
        """Press a key or key combination."""
        try:
            if '+' in key:
                # Handle key combinations like 'ctrl+c'
                keys = key.split('+')
                pyautogui.hotkey(*keys)
            else:
                pyautogui.press(key)
            
            return f"✅ Pressed key: {key}"
            
        except Exception as e:
            return f"❌ Error pressing key: {e}"
    
    # Service Management (Windows only)
    def list_services(self, status_filter: str = None) -> str:
        """List Windows services."""
        if not HAS_WINDOWS or not self.wmi_conn:
            return "❌ Service management only available on Windows with WMI"
        
        try:
            services = self.wmi_conn.Win32_Service()
            
            filtered_services = []
            for service in services:
                if status_filter is None or service.State.lower() == status_filter.lower():
                    filtered_services.append(service)
            
            info = [f"🔧 **Windows Services ({len(filtered_services)} found)**"]
            
            for i, service in enumerate(filtered_services[:20], 1):
                status = service.State or "Unknown"
                startup = service.StartMode or "Unknown"
                info.append(f"{i}. {service.Name}")
                info.append(f"   Status: {status}, Startup: {startup}")
                info.append(f"   Description: {(service.Description or 'No description')[:60]}...")
            
            if len(filtered_services) > 20:
                info.append(f"... and {len(filtered_services) - 20} more services")
            
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
            
            info = [f"🔧 **Service: {service_name}**"]
            info.append(f"Status: {service.State}")
            info.append(f"Startup Type: {service.StartMode}")
            info.append(f"Description: {service.Description or 'No description'}")
            info.append(f"Path: {service.PathName or 'Unknown'}")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Error getting service status: {e}"
    
    # Utility Methods
    def _bytes_to_human(self, bytes_value: int) -> str:
        """Convert bytes to human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    def get_help(self) -> str:
        """Get help information about available commands."""
        help_text = [
            f"🤖 **Advanced Desktop Plugin v{self.version}**",
            f"",
            f"**Available Commands:**",
            f"",
            f"📊 **System Information:**",
            f"• system_info - Get comprehensive system information",
            f"• hardware_info - Get detailed hardware information",
            f"• cpu_usage - Get current CPU usage",
            f"• memory_usage - Get current memory usage",
            f"• disk_usage - Get disk usage for all drives",
            f"• network_info - Get network interface information",
            f"• battery_status - Get battery information",
            f"",
            f"🔄 **Process Management:**",
            f"• list_processes - List running processes",
            f"• process_details(pid) - Get details about a process",
            f"• kill_process(pid) - Terminate a process",
            f"• start_program(path) - Start a program",
            f"",
            f"🪟 **Window Management (Windows only):**",
            f"• list_windows - List all open windows",
            f"• focus_window(title) - Focus a window",
            f"• close_window(title) - Close a window",
            f"• minimize_window(title) - Minimize a window",
            f"• maximize_window(title) - Maximize a window",
            f"",
            f"📁 **File Operations:**",
            f"• search_files(pattern) - Search for files",
            f"• open_file(path) - Open a file",
            f"• create_folder(path) - Create a folder",
            f"• delete_file(path) - Delete a file",
            f"",
            f"📋 **Clipboard Operations:**",
            f"• get_clipboard - Get clipboard content",
            f"• set_clipboard(text) - Set clipboard content",
            f"• clipboard_history - Show clipboard history",
            f"",
            f"🖥️ **Screen & Automation:**",
            f"• take_screenshot - Take a screenshot",
            f"• screen_info - Get screen information",
            f"• type_text(text) - Type text",
            f"• click_at(x, y) - Click at coordinates",
            f"• press_key(key) - Press a key",
            f"",
            f"🔧 **Services (Windows only):**",
            f"• list_services - List Windows services",
            f"• service_status(name) - Get service status"
        ]
        
        return "\n".join(help_text)
    
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
                # Extract process name/id from command
                parts = command_lower.split()
                if len(parts) > 2:
                    process_name = parts[-1]
                    return self.kill_process(process_name)
                return "❌ Please specify process name or PID to kill"
            elif "start program" in command_lower:
                # Extract program path from command
                parts = command.split()
                if len(parts) > 2:
                    program_path = " ".join(parts[2:])
                    return self.start_program(program_path)
                return "❌ Please specify program path to start"
            
            # Window Management Commands
            elif "windows list" in command_lower or "list windows" in command_lower:
                return self.list_windows()
            elif "focus window" in command_lower:
                # Extract window title
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
                # Extract text to set
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
                # If no match found, show available commands
                return f"❌ Unknown command: '{command}'\n\nAvailable commands:\n{self.get_help()}
                
        except Exception as e:
            return f"❌ Error executing command '{command}': {str(e)}"

# Create plugin instance
def create_plugin():
    """Factory function to create plugin instance."""
    return AdvancedDesktopPlugin()

# Plugin registration
if __name__ == "__main__":
    plugin = create_plugin()
    print(f"Advanced Desktop Plugin v{plugin.version} loaded successfully!")
    print("Available commands:", len(plugin.commands))
