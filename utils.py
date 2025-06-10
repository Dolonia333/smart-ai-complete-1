import os

def find_executable(app_name, search_paths=None):
    if search_paths is None:
        search_paths = [r"C:\Program Files", r"C:\Program Files (x86)"]

    for path in search_paths:
        for root, dirs, files in os.walk(path):
            for file in files:
                if app_name.lower() in file.lower() and file.endswith(".exe"):
                    return os.path.join(root, file)
    return None

def open_found_app(app_name):
    path = find_executable(app_name)
    if path:
        os.system(f'start "" "{path}"')
        return f"Opening {app_name}..."
    else:
        return f"Could not find {app_name}."

def find_file(filename, search_path="."):
    for root, dirs, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)
    return None
