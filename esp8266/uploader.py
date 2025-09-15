import threading
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import serial.tools.list_ports
import subprocess
import sys
import os
import threading
import time
import webbrowser  # Import the webbrowser module to open links


#####    ATENCION  Como esta ahora el esp32 hay que cambiar ya que esta solo subiendo el firmware
#####    ATENCION  y el spiffs no se sube. Hay que cambiar el comando de esptool para que suba el spiffs
#####    ATENCION y los otros archivos que hacen falta. Me funciono porque no era uno nuevo.


class UploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Firefly Firmware Uploader")
        self.root.geometry("500x700")  # Increased window size
        self.ser = None  # Initialize the serial object as None

        # Handle the window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Label
        tk.Label(root, text="Select USB Port and Upload Firmware", font=("Arial", 14)).pack(pady=10)

        # Dropdown for USB ports
        tk.Label(root, text="USB Port:").pack()
        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.Combobox(root, textvariable=self.port_var, state="readonly")
        self.port_dropdown.bind("<<ComboboxSelected>>", self.on_port_change)  # Bind the event
        self.port_dropdown.pack(pady=5)

        # Refresh button for USB ports
        tk.Button(root, text="Refresh Ports", command=self.refresh_ports).pack(pady=5)

        # File selection buttons
        tk.Button(root, text="Select Firmware File (firefly.bin)", command=self.select_firmware_file).pack(pady=5)
        self.firmware_path = tk.StringVar(value="Not selected")
        tk.Label(root, textvariable=self.firmware_path, wraplength=450, fg="blue").pack(pady=5)

        tk.Button(root, text="Select File System File (littlefs.bin)", command=self.select_filesystem_file).pack(pady=5)
        self.filesystem_path = tk.StringVar(value="Not selected")
        tk.Label(root, textvariable=self.filesystem_path, wraplength=450, fg="blue").pack(pady=5)

        # Wi-Fi credentials input fields
        # tk.Label(root, text="Wi-Fi Name:").pack()
        # self.wifi_name = tk.Entry(root, width=30)
        # self.wifi_name.pack(pady=5)

        # tk.Label(root, text="Wi-Fi Password:").pack()
        # self.wifi_pass = tk.Entry(root, width=30, show="*")
        # self.wifi_pass.pack(pady=5)

        # # Add a button to manually send Wi-Fi credentials
        # tk.Button(root, text="Send Wi-Fi Credentials", command=self.send_wifi_credentials, bg="blue", fg="white").pack(pady=10)
 
        # Add a button to manually listen to IP address
        #tk.Button(root, text="Listen for IP Address", command=self.listen_for_http, bg="blue", fg="white").pack(pady=10)
 
        # Upload button
        tk.Button(root, text="Upload Firmware", command=self.start_upload, bg="green", fg="white").pack(pady=10)

        # Progress bar
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        # Status label
        self.status_label = tk.Label(root, text="Status: Ready", fg="blue")
        self.status_label.pack(pady=5)

        # Populate ports initially
        self.refresh_ports()

    def update_progress(self, percent):
        """Update progress bar on main thread"""
        self.progress["value"] = percent
        self.root.update_idletasks()  # Force GUI update

    def refresh_ports(self):
        # Get list of available serial ports
        ports = [port.device for port in serial.tools.list_ports.comports()]
        if not ports:
            self.port_dropdown["values"] = ["No ports found"]
            self.port_var.set("No ports found")
        else:
            self.port_dropdown["values"] = ports
            self.port_var.set(ports[0])
            try:
                self.ser = serial.Serial(port=self.port_var.get() , baudrate=115200, timeout=1)  # Open the first port for testing
                self.status_label.config(text="Status: Connected", fg="green")

            except serial.SerialException as e:
                #print the error message including the name of the port

                self.status_label.config(text="Failed to open port "+ ports[0], fg="red")
                self.ser = None

    def on_port_change(self, event=None):
        """Handle changes in the selected port."""
        selected_port = self.port_var.get()
        if selected_port == "No ports found":
            self.status_label.config(text="Status: No ports found", fg="red")
            return

        try:
            # Attempt to open the selected port
            if self.ser:
                self.ser.close()  # Close any previously opened port
            self.ser = serial.Serial(port=selected_port, baudrate=115200, timeout=1)
            self.status_label.config(text=f"Status: Connected to {selected_port}", fg="green")
        except serial.SerialException as e:
            self.status_label.config(text=f"Failed to open port {selected_port}", fg="red")
            self.ser = None
            
    def select_firmware_file(self):
        # Open file dialog to select the firmware file
        file_path = filedialog.askopenfilename(title="Select Firmware File", filetypes=[("Binary Files", "*.bin")])
        if file_path:
            self.firmware_path.set(file_path)

    def select_filesystem_file(self):
        # Open file dialog to select the filesystem file
        file_path = filedialog.askopenfilename(title="Select File System File", filetypes=[("Binary Files", "*.bin")])
        if file_path:
            self.filesystem_path.set(file_path)

    def start_upload(self):
        # Run the upload process in a separate thread to avoid freezing the UI
        threading.Thread(target=self.upload_firmware).start()

    def upload_firmware(self):
        selected_port = self.port_var.get()
        firmware_file = self.firmware_path.get()
        filesystem_file = self.filesystem_path.get()
        partitions_file = os.path.join(os.path.dirname(firmware_file), "partitions.bin")
        bootloader_file = os.path.join(os.path.dirname(firmware_file), "bootloader.bin")
        boot_app0_file = os.path.join(os.path.dirname(firmware_file), "boot_app0.bin")

        if not selected_port or selected_port == "No ports found":
            messagebox.showerror("Error", "Please select a valid USB port.")
            return

        if firmware_file == "Not selected" or filesystem_file == "Not selected":
            messagebox.showerror("Error", "Please select both the firmware and filesystem files.")
            return

        # Check if chip is ESP32 or ESP8266
        self.status_label.config(text="Status: Detecting Device...", fg="orange")
        self.update_progress(10)  # Show some initial progress
        
        try:
            cmd = ["esptool", "--port", selected_port, "chip_id"]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            
            output = result.stdout + result.stderr
            print(f"Esptool output: {output}")
            
            self.update_progress(20)  # Device detected
            
            if "ESP32" in output or "esp32" in output.lower():
                self.status_label.config(text="Status: ESP32 Detected", fg="green")
                cmd = [
                    "esptool",
                    "--port", selected_port,
                    "--chip", "esp32",
                    "write_flash",
                    "-z",
                    "0x1000", bootloader_file,
                    "0x8000", partitions_file,
                    "0xe000", boot_app0_file,
                    "0x10000", firmware_file,
                    "0x290000", filesystem_file
                ]
            elif "ESP8266" in output or "esp8266" in output.lower():
                self.status_label.config(text="Status: ESP8266 Detected", fg="green")
                cmd = [
                    "esptool",
                    "--port", selected_port,
                    "--chip", "esp8266",
                    "write_flash",
                    "-z",
                    "0x000", firmware_file,
                    "0x300000", filesystem_file
                ]
            else:
                self.status_label.config(text="Status: Assuming ESP8266 (detection unclear)", fg="orange")
                cmd = [
                    "esptool",
                    "--port", selected_port,
                    "--chip", "esp8266",
                    "write_flash",
                    "-z",
                    "0x000", firmware_file,
                    "0x300000", filesystem_file
                ]
        except subprocess.TimeoutExpired:
            self.status_label.config(text="Status: Device Detection Timeout", fg="red")
            messagebox.showerror("Error", "Device detection timed out.")
            return
        except Exception as e:
            self.status_label.config(text="Status: Detection Error", fg="red")
            messagebox.showerror("Error", f"Error detecting device: {str(e)}")
            return

    self.status_label.config(text="Status: Uploading...", fg="orange")
    self.update_progress(30)  # Starting upload

    print("Executing command:", cmd)
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                 text=True, universal_newlines=True, bufsize=1)

        progress_value = 30
        total_files = len([f for f in [bootloader_file, partitions_file, boot_app0_file, firmware_file, filesystem_file] if os.path.exists(f)])
        progress_per_file = 60 / total_files if total_files > 0 else 60  # 60% for upload, rest for detection/completion

        current_file = 0
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                line = output.strip()
                print(line)  # Debug output
                
                # Better progress parsing
                if "Writing at" in line or "Writing" in line:
                    try:
                        # Try to extract percentage from different formats
                        if "(" in line and "%" in line:
                            # Format: "Writing at 0x00010000... (50 %)"
                            percent_part = line.split("(")[-1].split(")")[0]
                            if "%" in percent_part:
                                percent_str = percent_part.replace("%", "").strip()
                                file_percent = int(percent_str)
                                # Calculate overall progress
                                overall_progress = 30 + (current_file * progress_per_file) + (file_percent * progress_per_file / 100)
                                self.root.after(0, lambda p=min(90, overall_progress): self.update_progress(p))
                        else:
                            # Fallback: just increment progress gradually
                            progress_value = min(progress_value + 1, 90)
                            self.root.after(0, lambda p=progress_value: self.update_progress(p))
                    except (ValueError, IndexError) as e:
                        print(f"Could not parse progress from: {line}")
                        continue
                
                # Detect when starting a new file
                if "Writing" in line and "0x" in line:
                    if any(addr in line for addr in ["0x1000", "0x8000", "0xe000", "0x10000", "0x290000", "0x300000"]):
                        current_file += 1
                        base_progress = 30 + ((current_file - 1) * progress_per_file)
                        self.root.after(0, lambda p=base_progress: self.update_progress(p))
                        self.status_label.config(text=f"Status: Writing file {current_file}/{total_files}...", fg="orange")

        process.wait()
        
        if process.returncode == 0:
            self.update_progress(100)
            self.status_label.config(text="Status: Upload Successful!", fg="green")
            messagebox.showinfo("Success", "Firmware uploaded successfully!")
        else:
            self.status_label.config(text="Status: Upload Failed", fg="red")
            # Get remaining error output
            stderr_output = process.stderr.read() if process.stderr else "Unknown error"
            messagebox.showerror("Error", f"Upload failed:\n{stderr_output}")
            
    except Exception as e:
        self.status_label.config(text="Status: Error", fg="red")
        messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
    finally:
        if self.ser:
            self.ser.close()
            self.ser = None
    
    def send_wifi_credentials(self):
        try:
            port = self.port_var.get()
            self.status_label.config(text="Status: Connecting to Serial...", fg="orange")
            ser = serial.Serial(port, baudrate=115200, timeout=30)
    
            # Send Wi-Fi credentials
            wifi_name = self.wifi_name.get()
            wifi_pass = self.wifi_pass.get()
            ser.write(f"wifi_ssid,{wifi_name}\n".encode("utf-8"))
            ser.write(f"wifi_pass,{wifi_pass}\n".encode("utf-8"))
    
            # Send the "reset" command
            ser.write("reset\n".encode("utf-8"))
            ser.flush()  # Clear the serial buffer
            self.status_label.config(text="Status: Wi-Fi Credentials Sent and Device Reset!", fg="green")
            time.sleep(10)  # Wait for a second to ensure the command is sent
            #messagebox.showinfo("Success", "Wi-Fi credentials sent successfully! Resetting Device...")
    
            # Start a separate thread to listen for serial messages
            self.status_label.config(text="Status: Listening for IP Address...", fg="blue")
            threading.Thread(target=self.listen_for_http, args=(ser,), daemon=True).start()
    
        except Exception as e:
            self.status_label.config(text="Status: Serial Connection Failed", fg="red")
            messagebox.showerror("Error", f"Failed to send Wi-Fi credentials or listen for IP:\n{str(e)}")
    
    def listen_for_http(self):
        try:
            if not self.ser:
                port = self.port_var.get()
                self.ser = serial.Serial(port, baudrate=115200, timeout=3)
            while True:
                if self.ser.in_waiting > 0:  # Check if data is available
                    line = self.ser.readline().decode("utf-8").strip()
                    print("Serial Output:", line)  # Debugging
                    if line.startswith("http:"):
                        # Display the IP address as a clickable link
                        self.status_label.config(text="Device Interface Found!", fg="green")
                        link_label = tk.Label(
                            self.root, text=line, fg="blue", cursor="hand2", font=("Arial", 12, "underline")
                        )
                        link_label.pack(pady=10)

                        # Bind the link to open in the default web browser
                        link_label.bind("<Button-1>", lambda e: webbrowser.open(line))
                        break
        except Exception as e:
            self.status_label.config(text="Status: Error Reading Serial", fg="red")
            messagebox.showerror("Error", f"An error occurred while reading serial data:\n{str(e)}")

    def on_close(self):
        """Handle application close event."""
        if self.ser:
            try:
                self.ser.close()  # Ensure the serial port is closed
                print("Serial port closed.")
            except Exception as e:
                print(f"Error closing serial port: {e}")
        self.root.destroy()  # Close the Tkinter window

if __name__ == "__main__":
    root = tk.Tk()
    app = UploaderApp(root)
    root.mainloop()
