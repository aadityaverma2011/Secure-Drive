import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import subprocess
import os
import shutil
import io
import logging
from PIL import Image
import hashlib
import random
from options import (
    prompt_password, unlock_partition, mount_partition, unmount_partition, 
    list_files, move_file, open_file, change_password, encrypt_file, decrypt_file, pre_checks,
    derive_key
)

# Set up logging
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

# Define the mount points
MOUNT_POINT = "/mnt/private_partition"
SDA1_MOUNT_POINT = "/mnt/sda1"

class PartitionManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Partition Manager")
        self.root.geometry("400x400")

        self.password = None

        # Main Frame
        self.frame = tk.Frame(root)
        self.frame.pack(pady=20)

        # Buttons
        self.unlock_btn = tk.Button(self.frame, text="Unlock Partition", command=self.unlock_partition, width=20)
        self.unlock_btn.grid(row=0, column=0, pady=10)

        self.list_files_btn = tk.Button(self.frame, text="List Files", command=self.list_files, width=20)
        self.list_files_btn.grid(row=1, column=0, pady=10)

        self.move_file_btn = tk.Button(self.frame, text="Move and Encrypt File", command=self.move_and_encrypt_file, width=20)
        self.move_file_btn.grid(row=2, column=0, pady=10)

        self.open_file_btn = tk.Button(self.frame, text="Open and Decrypt File", command=self.open_and_decrypt_file, width=20)
        self.open_file_btn.grid(row=3, column=0, pady=10)

        self.change_password_btn = tk.Button(self.frame, text="Change Password", command=self.change_password, width=20)
        self.change_password_btn.grid(row=4, column=0, pady=10)

        self.exit_btn = tk.Button(self.frame, text="Exit", command=self.exit_app, width=20)
        self.exit_btn.grid(row=5, column=0, pady=10)

    def unlock_partition(self):
        self.password = tk.simpledialog.askstring("Password", "Enter the encryption password:", show="*")
        if self.password:
            try:
                pre_checks()  # Run pre-checks
                unlock_partition(self.password)
                mount_partition()  # Mount automatically after unlocking
                messagebox.showinfo("Success", "Partition unlocked and mounted successfully!")
            except Exception as e:
                logging.error(f"Failed to unlock and mount partition: {e}")
                messagebox.showerror("Error", f"Failed to unlock and mount partition: {e}")

    def list_files(self):
        try:
            # Check if partition is mounted before listing files
            if not os.path.ismount(MOUNT_POINT):
                messagebox.showwarning("Warning", "Partition is not mounted.")
                return

            files = os.listdir(MOUNT_POINT)
            if files:
                messagebox.showinfo("Files", "\n".join(files))
            else:
                messagebox.showinfo("Files", "No files found in the partition.")
        except Exception as e:
            logging.error(f"Failed to list files: {e}")
            messagebox.showerror("Error", f"Failed to list files: {e}")

    def move_and_encrypt_file(self):
        try:
            # Check if partition is mounted before allowing file actions
            if not os.path.ismount(MOUNT_POINT):
                messagebox.showwarning("Warning", "Partition is not mounted.")
                return

            file_path = filedialog.askopenfilename(title="Select File to Encrypt and Move")
            if file_path:
                password = simpledialog.askstring("Encryption Password", "Enter the encryption password for this file:", show="*")
                confirm_password = simpledialog.askstring("Encryption Password", "Re-enter the encryption password:", show="*")
                if password != confirm_password:
                    messagebox.showerror("Error", "Passwords do not match.")
                    return

                destination = os.path.join(MOUNT_POINT, "." + os.path.basename(file_path) + ".enc")
                encrypted_file = encrypt_file(file_path, password)
                shutil.move(encrypted_file, destination)
                messagebox.showinfo("Success", f"File '{os.path.basename(file_path)}' encrypted and moved.")
        except Exception as e:
            logging.error(f"Failed to move and encrypt file: {e}")
            messagebox.showerror("Error", f"Failed to move and encrypt file: {e}")



    def open_and_decrypt_file(self):
        try:
            # Check if partition is mounted before allowing file actions
            if not os.path.ismount(MOUNT_POINT):
                messagebox.showwarning("Warning", "Partition is not mounted.")
                return

            file_path = filedialog.askopenfilename(initialdir=MOUNT_POINT, title="Select File to Decrypt")
            
            if file_path:
                if file_path.endswith(".enc"):
                    password = simpledialog.askstring("Decryption Password", "Enter the decryption password:", show="*")
                    decrypted_data = decrypt_file(file_path, password)
                    if decrypted_data:
                        with Image.open(io.BytesIO(decrypted_data)) as img:
                            img.show()
                        messagebox.showinfo("Success", "File decrypted and opened successfully!")
                    else:
                        messagebox.showerror("Error", "Failed to decrypt file. Incorrect password or corrupt file.")
                else:
                    messagebox.showerror("Error", "The selected file is not encrypted.")
        except Exception as e:
            logging.error(f"Failed to open and decrypt file: {e}")
            messagebox.showerror("Error", f"Failed to open and decrypt file: {e}")

    def change_password(self):
        try:
            change_password()
        except Exception as e:
            logging.error(f"Failed to change password: {e}")
            messagebox.showerror("Error", f"Failed to change password: {e}")

    def exit_app(self):
        """Unmount partition and exit the application."""
        try:
            if os.path.ismount(MOUNT_POINT):
                unmount_partition()
            self.root.quit()
        except Exception as e:
            logging.error(f"Failed to unmount partition during exit: {e}")
            messagebox.showerror("Error", f"Failed to unmount partition during exit: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PartitionManagerGUI(root)
    root.mainloop()
