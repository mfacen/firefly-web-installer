import serial.tools.list_ports
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

def flash(port):
    cmd = [
        "esptool.py",
        "--chip", "esp32",
        "--port", port,
        "--baud", "921600",
        "--before", "default_reset",
        "--after", "hard_reset",
        "write_flash", "-z",
        "--flash_mode", "dio",
        "--flash_freq", "40m",
        "--flash_size", "4MB",
        "0x1000", "bootloader.bin",
        "0x8000", "partitions.bin",
        "0xe000", "boot_app0.bin",
        "0x10000", "firmware.bin",
        "0x00310000", "spiffs.bin"
    ]
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Starting ESP32 flash on port {port}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 50)
    
    try:
        # Run with real-time output
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True,
            cwd=script_dir,
            bufsize=1
        )
        
        # Print output line by line
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                sys.stdout.flush()
        
        return_code = process.wait()
        
        if return_code == 0:
            print("=" * 50)
            print("✅ FLASHING COMPLETED SUCCESSFULLY!")
            messagebox.showinfo("Success", "ESP32 flashing completed!")
        else:
            print("=" * 50)
            print("❌ FLASHING FAILED!")
            messagebox.showerror("Error", f"Flashing failed with return code {return_code}")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        messagebox.showerror("Error", f"Flashing failed:\n{e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        messagebox.showerror("Error", f"Unexpected error:\n{e}")

def main():
    ports = [port.device for port in serial.tools.list_ports.comports()]
    root = tk.Tk()
    root.title("ESP32 Flash Tool")

    tk.Label(root, text="Select USB Port:").pack(padx=10, pady=5)
    port_var = tk.StringVar(value=ports[0] if ports else "")
    combo = ttk.Combobox(root, textvariable=port_var, values=ports, state="readonly")
    combo.pack(padx=10, pady=5)

    def on_flash():
        if port_var.get():
            flash(port_var.get())
        else:
            messagebox.showwarning("No Port", "Please select a USB port.")

    tk.Button(root, text="Flash ESP32", command=on_flash).pack(padx=10, pady=10)
    root.mainloop()

if __name__ == "__main__":
    main()