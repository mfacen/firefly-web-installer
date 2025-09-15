import subprocess
import sys
import os
import importlib.util
from pathlib import Path

def create_virtual_environment():
    """Create a virtual environment for the application"""
    venv_path = Path("firefly_venv")
    
    if not venv_path.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print("Virtual environment created!")
    
    return venv_path

def get_venv_python(venv_path):
    """Get the python executable from virtual environment"""
    if os.name == 'nt':  # Windows
        return venv_path / "Scripts" / "python.exe"
    else:  # Linux/Mac
        return venv_path / "bin" / "python"

def get_venv_pip(venv_path):
    """Get the pip executable from virtual environment"""
    if os.name == 'nt':  # Windows
        return venv_path / "Scripts" / "pip.exe"
    else:  # Linux/Mac
        return venv_path / "bin" / "pip"

def check_and_install_package(package_name, import_name=None, venv_path=None):
    """Check if package is installed in venv, install if not"""
    if import_name is None:
        import_name = package_name
    
    if venv_path:
        # Use virtual environment python
        venv_python = get_venv_python(venv_path)
        venv_pip = get_venv_pip(venv_path)
        
        # Check if package is installed in venv
        result = subprocess.run([
            str(venv_python), "-c", f"import {import_name}"
        ], capture_output=True)
        
        if result.returncode != 0:
            print(f"Installing {package_name} in virtual environment...")
            subprocess.run([str(venv_pip), "install", package_name], check=True)
            print(f"{package_name} installed successfully!")
        else:
            print(f"{package_name} already installed in virtual environment.")
    else:
        # Fallback to system check
        spec = importlib.util.find_spec(import_name)
        if spec is None:
            print(f"Installing {package_name}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package_name], check=True)
            print(f"{package_name} installed successfully!")
        else:
            print(f"{package_name} already installed.")

def setup_environment():
    """Setup all required dependencies"""
    required_packages = [
        ('pyserial', 'serial'),
        ('esptool', 'esptool'),
    ]
    
    print("Setting up Firefly Uploader environment...")
    
    # Create virtual environment
    try:
        venv_path = create_virtual_environment()
    except Exception as e:
        print(f"Error creating virtual environment: {e}")
        print("Trying system-wide installation...")
        venv_path = None
    
    print("Checking and installing required packages...")
    
    for package, import_name in required_packages:
        try:
            check_and_install_package(package, import_name, venv_path)
        except Exception as e:
            print(f"Error installing {package}: {e}")
            return False, None
    
    print("All dependencies installed successfully!")
    return True, venv_path

def run_uploader(venv_path=None):
    """Run the main uploader application"""
    try:
        if venv_path:
            # Get path to uploader.py from user
            uploader_path = get_uploader_path()
            if not uploader_path:
                print("No uploader.py file selected. Exiting...")
                return
            
            # Run using virtual environment python
            venv_python = get_venv_python(venv_path)
            subprocess.run([str(venv_python), str(uploader_path)])
        else:
            # Import and run normally
            import uploader
            import tkinter as tk
            
            root = tk.Tk()
            app = uploader.UploaderApp(root)
            root.mainloop()
        
    except ImportError as e:
        print(f"Error importing modules: {e}")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"Error running uploader: {e}")
        input("Press Enter to exit...")

def get_uploader_path():
    """Get the path to uploader.py from user"""
    try:
        import tkinter as tk
        from tkinter import filedialog
        
        # Create a temporary root window (hidden)
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        print("Please select the uploader.py file...")
        
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select uploader.py file",
            filetypes=[
                ("Python files", "*.py"),
                ("All files", "*.*")
            ],
            initialdir=os.getcwd()  # Start in current directory
        )
        
        root.destroy()  # Clean up the temporary window
        
        if file_path:
            print(f"Selected: {file_path}")
            return Path(file_path)
        else:
            print("No file selected.")
            return None
            
    except ImportError:
        # Fallback to console input if tkinter not available
        return get_uploader_path_console()
    except Exception as e:
        print(f"Error opening file dialog: {e}")
        return get_uploader_path_console()

def get_uploader_path_console():
    """Console fallback for getting uploader.py path"""
    print("\nPlease enter the path to uploader.py:")
    print("(You can drag and drop the file here, or type the full path)")
    
    while True:
        user_input = input("Path: ").strip()
        
        if not user_input:
            print("No path entered. Try again or press Ctrl+C to exit.")
            continue
        
        # Remove quotes if user drag-dropped the file
        user_input = user_input.strip('"\'')
        
        uploader_path = Path(user_input)
        
        if uploader_path.exists() and uploader_path.suffix == '.py':
            print(f"Found: {uploader_path}")
            return uploader_path
        else:
            print(f"File not found or not a Python file: {uploader_path}")
            print("Please try again...")

if __name__ == "__main__":
    success, venv_path = setup_environment()
    if success:
        run_uploader(venv_path)
    else:
        print("Failed to setup environment. Please check your internet connection.")
        input("Press Enter to exit...")