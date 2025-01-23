import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import shutil
import io
import logging
from PIL import Image
from options import (
    prompt_password, unlock_partition, mount_partition, unmount_partition, 
    list_files, move_file, open_file, change_password, encrypt_file, decrypt_file
)

# Set up logging
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

# Define the mount point
MOUNT_POINT = "/mnt/private_partition"

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

        self.mount_btn = tk.Button(self.frame, text="Mount Partition", command=self.mount_partition, width=20)
        self.mount_btn.grid(row=1, column=0, pady=10)

        self.list_files_btn = tk.Button(self.frame, text="List Files", command=self.list_files, width=20)
        self.list_files_btn.grid(row=2, column=0, pady=10)

        self.move_file_btn = tk.Button(self.frame, text="Move and Encrypt File", command=self.move_and_encrypt_file, width=20)
        self.move_file_btn.grid(row=3, column=0, pady=10)

        self.open_file_btn = tk.Button(self.frame, text="Open and Decrypt File", command=self.open_and_decrypt_file, width=20)
        self.open_file_btn.grid(row=4, column=0, pady=10)

        self.change_password_btn = tk.Button(self.frame, text="Change Password", command=self.change_password, width=20)
        self.change_password_btn.grid(row=5, column=0, pady=10)

        self.unmount_btn = tk.Button(self.frame, text="Unmount Partition", command=self.unmount_partition, width=20)
        self.unmount_btn.grid(row=6, column=0, pady=10)

        self.exit_btn = tk.Button(self.frame, text="Exit", command=self.root.quit, width=20)
        self.exit_btn.grid(row=7, column=0, pady=10)

    def unlock_partition(self):
        self.password = tk.simpledialog.askstring("Password", "Enter the encryption password:", show="*")
        if self.password:
            try:
                unlock_partition(self.password)
                messagebox.showinfo("Success", "Partition unlocked successfully!")
            except Exception as e:
                logging.error(f"Failed to unlock partition: {e}")
                messagebox.showerror("Error", f"Failed to unlock partition: {e}")

    def mount_partition(self):
        try:
            # Ensure partition is not already mounted
            if os.path.ismount(MOUNT_POINT):
                messagebox.showwarning("Warning", f"Partition is already mounted at {MOUNT_POINT}")
                return
            
            mount_partition()
            messagebox.showinfo("Success", f"Partition mounted at {MOUNT_POINT}")
        except Exception as e:
            logging.error(f"Failed to mount partition: {e}")
            messagebox.showerror("Error", f"Failed to mount partition: {e}")

    def unmount_partition(self):
        try:
            # Ensure partition is mounted before attempting to unmount
            if not os.path.ismount(MOUNT_POINT):
                messagebox.showwarning("Warning", "Partition is not mounted.")
                return

            unmount_partition()
            messagebox.showinfo("Success", "Partition unmounted successfully!")
        except Exception as e:
            logging.error(f"Failed to unmount partition: {e}")
            messagebox.showerror("Error", f"Failed to unmount partition: {e}")

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
                destination = os.path.join(MOUNT_POINT, "." + os.path.basename(file_path) + ".enc")
                encrypted_file = encrypt_file(file_path, self.password)
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
                    decrypted_data = decrypt_file(file_path, self.password)
                    with Image.open(io.BytesIO(decrypted_data)) as img:
                        img.show()
                    messagebox.showinfo("Success", "File decrypted and opened successfully!")
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


if __name__ == "__main__":
    root = tk.Tk()
    app = PartitionManagerGUI(root)
    root.mainloop()
