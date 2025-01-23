import subprocess
import time

def list_drives():
    """List all available drives on the system."""
    try:
        print("Fetching connected drives...")
        result = subprocess.run(['lsblk', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT'], capture_output=True, text=True, check=True)
        print("\nAvailable drives:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error fetching drives: {e}")
        exit(1)

def validate_drive(drive):
    """Validate that the selected drive exists and meets safety criteria."""
    try:
        result = subprocess.run(['lsblk', '-b', '-o', 'NAME,SIZE', f'/dev/{drive}'], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        if len(lines) < 2:
            print(f"Drive /dev/{drive} not found!")
            return False

        size_bytes = int(lines[1].split()[1])
        size_gb = size_bytes / (1024 ** 3)

        if size_gb > 35:
            print("Error: Drive size exceeds the 35GB safety limit. Operation aborted.")
            return False

        print(f"Drive /dev/{drive} selected with size: {size_gb:.2f} GB.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error validating drive: {e}")
        return False

def confirm_action(message):
    """Prompt the user to confirm an action."""
    while True:
        response = input(f"{message} (yes/no): ").strip().lower()
        if response in ['yes', 'no']:
            return response == 'yes'
        print("Please enter 'yes' or 'no'.")

def create_partitions(device):
    """Partition the drive into public and private sections."""
    try:
        print(f"Partitioning {device}...")
        subprocess.run(['sudo', 'wipefs', '--all', device], check=True)
        subprocess.run(['sudo', 'parted', '-s', device, 'mklabel', 'gpt'], check=True)
        subprocess.run(['sudo', 'parted', '-s', device, 'mkpart', 'public', 'fat32', '0%', '5GB'], check=True)
        subprocess.run(['sudo', 'parted', '-s', device, 'mkpart', 'private', 'xfs', '5GB', '100%'], check=True)

        # Force kernel to reread the partition table
        print("Partitions created. Forcing kernel to reread partition table...")
        subprocess.run(['sudo', 'partprobe', device], check=True)
        
        # Adding a short delay for the system to update
        time.sleep(2)
        print(f"Partitions created successfully on {device}.")
    except subprocess.CalledProcessError as e:
        print(f"Error creating partitions: {e}")
        exit(1)

def format_partitions(device):
    """Format the public and private partitions."""
    try:
        public_partition = f"{device}1"
        private_partition = f"{device}2"
        
        print("Verifying partitions...")
        result = subprocess.run(['lsblk', '-o', 'NAME', device], capture_output=True, text=True, check=True)
        if public_partition.split('/dev/')[-1] not in result.stdout or private_partition.split('/dev/')[-1] not in result.stdout:
            print("Error: Partitions not found. Please check the device and try again.")
            exit(1)

        subprocess.run(['sudo', 'mkfs.vfat', '-F', '32', public_partition], check=True)
        print(f"Public partition {public_partition} formatted as FAT32.")

        subprocess.run(['sudo', 'mkfs.xfs', '-f', private_partition], check=True)
        print(f"Private partition {private_partition} formatted as XFS.")
    except subprocess.CalledProcessError as e:
        print(f"Error formatting partitions: {e}")
        exit(1)

def main():
    print("=== USB Drive Partitioning Script ===")
    list_drives()

    drive = input("Enter the drive name (e.g., 'sdb') you want to partition: ").strip()
    if not drive or not validate_drive(drive):
        print("Invalid drive selection. Exiting.")
        return

    device_path = f"/dev/{drive}"

    if not confirm_action(f"Are you sure you want to partition {device_path}? This will erase all data."):
        print("Operation cancelled by the user.")
        return

    create_partitions(device_path)
    format_partitions(device_path)

    print(f"Drive {device_path} has been successfully partitioned and formatted!")
    print("Public partition: FAT32 (5GB)")
    print("Private partition: XFS (remaining space)")

if __name__ == "__main__":
    main()
