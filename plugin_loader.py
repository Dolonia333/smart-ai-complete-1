import os
import importlib

def load_plugins(plugin_folder="plugins"):
    plugins = {}
    for filename in os.listdir(plugin_folder):
        if filename.endswith(".py") and filename != "__init__.py":
            plugin_name = filename[:-3]  # Remove the .py extension
            module = importlib.import_module(f"{plugin_folder}.{plugin_name}")
            plugins[plugin_name] = module
    return plugins
