import inspect

def print_directories(module_name):
    try:
        module = __import__(module_name)
        module_dir = dir(module)
        
        for name in module_dir:
            obj = getattr(module, name)
            if inspect.ismodule(obj):
                print(f"Directory: {name}")
                
    except ImportError:
        print(f"Error: Module '{module_name}' not found.")

if __name__ == "__main__":
    # Replace 'module_name' with the name of the module you want to inspect
    module_name = "math"
    print_directories(module_name)
