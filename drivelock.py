import os
import subprocess
import sys

MOUNT_POINT = "/mnt/private_partition"
PARTITION = "/dev/sda2"  # Adjust this based on your setup

def run_command(command):
    """Run a shell command and handle errors."""
    try:
        subprocess.run(command, check=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e.stderr.decode().strip()}")

def force_kill_processes():
    """Kill all processes accessing the partition."""
    print(f"Checking for processes accessing {MOUNT_POINT}...")
    try:
        result = subprocess.run(
            ["sudo", "lsof", "+D", MOUNT_POINT],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        processes = result.stdout.splitlines()
        if len(processes) > 1:  # Ignore header line
            print(f"Processes found: {len(processes) - 1}. Killing...")
            for line in processes[1:]:
                pid = line.split()[1]  # PID is in the second column
                run_command(["sudo", "kill", "-9", pid])
            print("All processes killed.")
        else:
            print("No processes are accessing the partition.")
    except Exception as e:
        print(f"Failed to check or kill processes: {e}")

def lock_partition():
    """Force unmount and lock the partition."""
    print("Locking the partition...")
    try:
        # Force unmount the partition
        print(f"Forcefully unmounting {MOUNT_POINT}...")
        run_command(["sudo", "umount", "-f", MOUNT_POINT])
        
        # Revoke access to the partition
        print(f"Locking device {PARTITION}...")
        run_command(["sudo", "chmod", "000", PARTITION])
        print("Partition locked successfully.")
    except Exception as e:
        print(f"Failed to lock the partition: {e}")

def unlock_partition(password):
    """Unlock and mount the encrypted partition."""
    try:
        # Unlock the device
        print(f"Unlocking device {PARTITION}...")
        run_command(["sudo", "chmod", "660", PARTITION])

        # Mount the partition
        if not os.path.exists(MOUNT_POINT):
            os.makedirs(MOUNT_POINT)
        run_command(["sudo", "mount", PARTITION, MOUNT_POINT])
        print(f"Partition mounted successfully at {MOUNT_POINT}.")
    except Exception as e:
        print(f"Failed to unlock and mount the partition: {e}")

def encrypt_partition(password):
    """Encrypt the partition with LUKS if not already encrypted."""
    try:
        print(f"Encrypting {PARTITION} with LUKS...")
        run_command(["sudo", "cryptsetup", "luksFormat", PARTITION])
        print("Partition encrypted successfully.")
    except Exception as e:
        print(f"Failed to encrypt the partition: {e}")

def unencrypt_partition(file_system="ext4"):
    """Remove the LUKS encryption and reformat the partition."""
    try:
        # First, ensure the partition is unmounted
        print(f"Attempting to unmount {MOUNT_POINT}...")
        run_command(["sudo", "umount", MOUNT_POINT])

        # Close the LUKS container if it's open
        print(f"Closing LUKS container for {PARTITION}...")
        run_command(["sudo", "cryptsetup", "close", f"luks-{PARTITION}"])

        # Reformat the partition to the specified file system
        print(f"Reformatting {PARTITION} to {file_system}...")
        if file_system == "xfs":
            run_command(["sudo", "mkfs.xfs", PARTITION])
        elif file_system == "ext4":
            run_command(["sudo", "mkfs.ext4", PARTITION])
        # Add more filesystems as needed
        else:
            print(f"Unsupported file system: {file_system}. Defaulting to ext4.")
            run_command(["sudo", "mkfs.ext4", PARTITION])

        print(f"Partition {PARTITION} has been unencrypted and reformatted to {file_system}.")
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to unencrypt the partition: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def main():
    print("Partition Protection System")
    while True:
        print("\nOptions:")
        print("1. Lock the partition")
        print("2. Unlock the partition")
        print("3. Encrypt the partition")
        print("4. Unencrypt the partition (Reformat to a file system)")
        print("5. Exit")
        choice = input("Enter your choice (1/2/3/4/5): ").strip()

        if choice == "1":
            force_kill_processes()
            lock_partition()
        elif choice == "2":
            password = input("Enter the unlock password: ").strip()
            unlock_partition(password)
        elif choice == "3":
            password = input("Enter a new encryption password: ").strip()
            encrypt_partition(password)
        elif choice == "4":
            file_system = input("Enter the desired file system (ext4/xfs): ").strip()
            unencrypt_partition(file_system)
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
