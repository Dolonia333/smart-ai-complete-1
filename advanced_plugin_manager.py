import os
import importlib
import inspect
import json
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

class BasePlugin(ABC):
    """Base class for all plugins"""
    
    def __init__(self):
        self.name = self.__class__.__name__.lower().replace('plugin', '')
        self.description = getattr(self, 'description', 'No description available')
        self.commands = getattr(self, 'commands', [])
        self.enabled = True
    
    @abstractmethod
    def handle_command(self, command: str, **kwargs) -> str:
        """Handle a command for this plugin"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            'name': self.name,
            'description': self.description,
            'commands': self.commands,
            'enabled': self.enabled
        }
    
    def can_handle(self, command: str) -> bool:
        """Check if this plugin can handle the given command"""
        command_lower = command.lower()
        return any(cmd.lower() in command_lower for cmd in self.commands)

class AdvancedPluginManager:
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = plugins_dir
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_modules: Dict[str, Any] = {}
        self.plugin_registry_file = os.path.join(plugins_dir, "registry.json")
        self.load_plugins()
    
    def load_plugins(self):
        """Load all plugins from the plugins directory"""
        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir)
            return
        
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                self.load_plugin(filename[:-3])
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin"""
        try:
            module_path = f"{self.plugins_dir}.{plugin_name}"
            
            # Reload if already loaded
            if module_path in self.plugin_modules:
                importlib.reload(self.plugin_modules[module_path])
            else:
                self.plugin_modules[module_path] = importlib.import_module(module_path)
            
            module = self.plugin_modules[module_path]
            
            # Look for plugin classes that inherit from BasePlugin
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BasePlugin) and 
                    obj is not BasePlugin):
                    plugin_instance = obj()
                    self.plugins[plugin_instance.name] = plugin_instance
                    print(f"Loaded plugin: {plugin_instance.name}")
                    return True
            
            # Fallback: look for legacy plugins with handle_command function
            if hasattr(module, 'handle_command'):
                # Create a wrapper for legacy plugins
                class LegacyPluginWrapper(BasePlugin):
                    def __init__(self, module, name):
                        super().__init__()
                        self.module = module
                        self.name = name
                        self.description = getattr(module, 'description', f'Legacy plugin: {name}')
                        self.commands = getattr(module, 'commands', [name])
                    
                    def handle_command(self, command: str, **kwargs) -> str:
                        return self.module.handle_command(command)
                
                wrapper = LegacyPluginWrapper(module, plugin_name)
                self.plugins[wrapper.name] = wrapper
                print(f"Loaded legacy plugin: {wrapper.name}")
                return True
            
            print(f"No valid plugin class found in {plugin_name}")
            return False
            
        except Exception as e:
            print(f"Error loading plugin {plugin_name}: {e}")
            return False
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Get a specific plugin by name"""
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all loaded plugins with their info"""
        return [plugin.get_info() for plugin in self.plugins.values()]
    
    def find_plugin_for_command(self, command: str) -> Optional[BasePlugin]:
        """Find the best plugin to handle a command"""
        command_lower = command.lower()
        
        # First, try exact matches
        for plugin in self.plugins.values():
            if not plugin.enabled:
                continue
            if plugin.can_handle(command):
                return plugin
        
        # Then try keyword matching
        for plugin in self.plugins.values():
            if not plugin.enabled:
                continue
            if plugin.name in command_lower:
                return plugin
        
        return None
    
    def execute_command(self, command: str, **kwargs) -> str:
        """Execute a command using the appropriate plugin"""
        plugin = self.find_plugin_for_command(command)
        if plugin:
            try:
                return plugin.handle_command(command, **kwargs)
            except Exception as e:
                return f"Error executing plugin {plugin.name}: {e}"
        return "No suitable plugin found for this command."
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a specific plugin"""
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
        return self.load_plugin(plugin_name)
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True
            return True
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False
            return True
        return False
    
    def save_registry(self):
        """Save plugin registry to file"""
        registry = {
            name: {
                'enabled': plugin.enabled,
                'description': plugin.description,
                'commands': plugin.commands
            }
            for name, plugin in self.plugins.items()
        }
        
        try:
            with open(self.plugin_registry_file, 'w') as f:
                json.dump(registry, f, indent=2)
        except Exception as e:
            print(f"Error saving plugin registry: {e}")
    
    def load_registry(self):
        """Load plugin registry from file"""
        if not os.path.exists(self.plugin_registry_file):
            return
        
        try:
            with open(self.plugin_registry_file, 'r') as f:
                registry = json.load(f)
            
            for name, config in registry.items():
                if name in self.plugins:
                    self.plugins[name].enabled = config.get('enabled', True)
        except Exception as e:
            print(f"Error loading plugin registry: {e}")
