import os
import subprocess
import sys

PASSWORD = "1234"
MAX_SIZE_GB = 35

def run_command(command):
    """Run a shell command and handle errors."""
    try:
        subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        sys.exit(1)

def get_drive_size(drive):
    """Get the size of the drive in GB."""
    try:
        output = subprocess.check_output(f"lsblk -b -dn -o SIZE {drive}", shell=True).decode().strip()
        size_bytes = int(output)
        size_gb = size_bytes / (1024 ** 3)
        return round(size_gb, 2)
    except Exception as e:
        print(f"Failed to get drive size: {e}")
        sys.exit(1)

def encrypt_partition(drive):
    """Encrypt the specified drive using LUKS."""
    print(f"Encrypting {drive} with LUKS...")
    run_command(f"echo -n {PASSWORD} | sudo cryptsetup luksFormat {drive}")
    print(f"{drive} encrypted successfully!")

def main():
    print("Welcome to LockDrive!")
    drive = input("Enter the drive name (e.g., '/dev/sda2') you want to encrypt: ").strip()

    if not os.path.exists(drive):
        print(f"Error: Drive {drive} does not exist.")
        sys.exit(1)

    # Check the size of the drive
    size_gb = get_drive_size(drive)
    print(f"Drive {drive} selected with size: {size_gb} GB.")

    if size_gb > MAX_SIZE_GB:
        print(f"Error: Drive size exceeds the maximum allowed size of {MAX_SIZE_GB} GB.")
        sys.exit(1)

    confirm = input(f"Are you sure you want to encrypt {drive}? This will erase all data. (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Operation canceled.")
        sys.exit(0)

    encrypt_partition(drive)
    print("Drive encryption complete.")

if __name__ == "__main__":
    main()
