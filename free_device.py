import subprocess
import os
import sys

def run_command(command):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(command)}: {e}")
        print(e.stderr.strip())
        sys.exit(1)

def unmount_device(device):
    """Unmount all partitions of the specified device."""
    try:
        print(f"Checking mount points for {device}...")
        mount_points = run_command(['lsblk', '-o', 'MOUNTPOINT', '-nr', device])
        if mount_points:
            print(f"Unmounting {device}...")
            run_command(['sudo', 'umount', '-l', device + '*'])
            print(f"All partitions of {device} unmounted successfully.")
        else:
            print(f"No mount points found for {device}.")
    except Exception as e:
        print(f"Error unmounting device: {e}")
        sys.exit(1)

def kill_device_processes(device):
    """Kill any processes accessing the device."""
    try:
        print(f"Checking for processes using {device}...")
        lsof_output = run_command(['sudo', 'lsof', device])
        for line in lsof_output.splitlines()[1:]:  # Skip the header
            parts = line.split()
            pid = parts[1]
            print(f"Killing process {pid} using {device}...")
            run_command(['sudo', 'kill', '-9', pid])
        print(f"All processes using {device} have been killed.")
    except subprocess.CalledProcessError:
        print(f"No processes are using {device}.")
    except Exception as e:
        print(f"Error killing processes: {e}")
        sys.exit(1)

def release_device_locks(device):
    """Release any locks on the device."""
    try:
        print(f"Releasing locks on {device}...")
        run_command(['sudo', 'blockdev', '--flushbufs', device])
        print(f"Locks on {device} released successfully.")
    except Exception as e:
        print(f"Error releasing locks: {e}")
        sys.exit(1)

def main():
    print("=== Device Busy Resolution Script ===")
    device = input("Enter the device name (e.g., '/dev/sda'): ").strip()
    if not os.path.exists(device):
        print(f"Error: Device {device} does not exist.")
        sys.exit(1)

    unmount_device(device)
    kill_device_processes(device)
    release_device_locks(device)

    print(f"Device {device} should now be free for operations.")

if __name__ == "__main__":
    main()
