import os
import subprocess
import psutil
import time
from advanced_plugin_manager import BasePlugin

class SystemPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.description = "Control system functions like volume, brightness, processes"
        self.commands = ["volume", "brightness", "processes", "system", "task", "kill", "cpu", "memory", "disk"]
    
    def handle_command(self, command: str, **kwargs) -> str:
        """Handle system control commands"""
        command_lower = command.lower()
        
        if "volume" in command_lower:
            return self.handle_volume(command)
        elif "brightness" in command_lower:
            return self.handle_brightness(command)
        elif any(word in command_lower for word in ["process", "task", "kill"]):
            return self.handle_processes(command)
        elif any(word in command_lower for word in ["cpu", "memory", "disk", "system info"]):
            return self.get_system_info()
        elif "shutdown" in command_lower:
            return self.shutdown_system(command)
        elif "restart" in command_lower:
            return self.restart_system()
        else:
            return "Available system commands: volume, brightness, processes, system info, shutdown, restart"
    
    def handle_volume(self, command: str) -> str:
        """Control system volume"""
        try:
            if "up" in command.lower() or "increase" in command.lower():
                os.system("powershell -c \"(New-Object -ComObject WScript.Shell).SendKeys([char]175)\"")
                return "Volume increased"
            elif "down" in command.lower() or "decrease" in command.lower():
                os.system("powershell -c \"(New-Object -ComObject WScript.Shell).SendKeys([char]174)\"")
                return "Volume decreased"
            elif "mute" in command.lower():
                os.system("powershell -c \"(New-Object -ComObject WScript.Shell).SendKeys([char]173)\"")
                return "Volume muted/unmuted"
            else:
                return "Volume commands: 'volume up', 'volume down', 'volume mute'"
        except Exception as e:
            return f"Error controlling volume: {e}"
    
    def handle_brightness(self, command: str) -> str:
        """Control screen brightness (Windows specific)"""
        try:
            if "up" in command.lower() or "increase" in command.lower():
                # Use powershell to increase brightness
                result = subprocess.run([
                    "powershell", "-Command",
                    "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,100)"
                ], capture_output=True, text=True)
                return "Brightness increased (this may not work on all systems)"
            elif "down" in command.lower() or "decrease" in command.lower():
                result = subprocess.run([
                    "powershell", "-Command",
                    "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,50)"
                ], capture_output=True, text=True)
                return "Brightness decreased (this may not work on all systems)"
            else:
                return "Brightness commands: 'brightness up', 'brightness down'"
        except Exception as e:
            return f"Error controlling brightness: {e}"
    
    def handle_processes(self, command: str) -> str:
        """Handle process-related commands"""
        try:
            if "list" in command.lower() or "show" in command.lower():
                return self.list_top_processes()
            elif "kill" in command.lower():
                return self.kill_process(command)
            else:
                return "Process commands: 'list processes', 'kill process [name]'"
        except Exception as e:
            return f"Error handling processes: {e}"
    
    def list_top_processes(self) -> str:
        """List top CPU consuming processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] is not None:
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            result = "Top 10 processes by CPU usage:\n"
            for i, proc in enumerate(processes[:10]):
                result += f"{i+1}. {proc['name']} (PID: {proc['pid']}) - CPU: {proc['cpu_percent']:.1f}% Memory: {proc['memory_percent']:.1f}%\n"
            
            return result
        except Exception as e:
            return f"Error listing processes: {e}"
    
    def kill_process(self, command: str) -> str:
        """Kill a process by name or PID"""
        try:
            # Extract process name from command
            words = command.split()
            if len(words) < 3:
                return "Usage: kill process [process_name or PID]"
            
            target = words[2]
            
            # Try to convert to PID first
            try:
                pid = int(target)
                proc = psutil.Process(pid)
                proc.terminate()
                return f"Process {pid} ({proc.name()}) terminated"
            except ValueError:
                # Not a number, treat as process name
                killed = []
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if target.lower() in proc.info['name'].lower():
                            proc.terminate()
                            killed.append(f"{proc.info['name']} (PID: {proc.info['pid']})")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                if killed:
                    return f"Terminated processes: {', '.join(killed)}"
                else:
                    return f"No processes found matching '{target}'"
                    
        except Exception as e:
            return f"Error killing process: {e}"
    
    def get_system_info(self) -> str:
        """Get system information"""
        try:
            # CPU info
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory info
            memory = psutil.virtual_memory()
            
            # Disk info
            disk = psutil.disk_usage('/')
            
            info = f"System Information:\n"
            info += f"🖥️ CPU: {cpu_count} cores, {cpu_percent}% usage\n"
            info += f"🧠 Memory: {memory.percent}% used ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)\n"
            info += f"💾 Disk: {disk.percent}% used ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)\n"
            
            return info
        except Exception as e:
            return f"Error getting system info: {e}"
    
    def shutdown_system(self, command: str) -> str:
        """Shutdown the system"""
        if "confirm" in command.lower() or "yes" in command.lower():
            try:
                os.system("shutdown /s /t 10")
                return "System will shutdown in 10 seconds. Run 'shutdown /a' to abort."
            except Exception as e:
                return f"Error shutting down: {e}"
        else:
            return "To confirm shutdown, say: 'shutdown confirm' or 'shutdown yes'"
    
    def restart_system(self) -> str:
        """Restart the system"""
        try:
            os.system("shutdown /r /t 10")
            return "System will restart in 10 seconds. Run 'shutdown /a' to abort."
        except Exception as e:
            return f"Error restarting: {e}"
