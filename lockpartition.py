import os
import subprocess

def lock_partition(partition, password):
    """
    Locks the specified partition with a password using LUKS.
    """
    try:
        # Step 1: Check if cryptsetup is installed
        if not subprocess.call(["which", "cryptsetup"], stdout=subprocess.DEVNULL) == 0:
            print("Error: cryptsetup is not installed. Please install it and try again.")
            return

        print(f"Encrypting partition {partition}...")

        # Step 2: Encrypt the partition with the provided password
        encrypt_command = f"echo {password} | sudo cryptsetup luksFormat {partition} -q --batch-mode"
        subprocess.run(encrypt_command, shell=True, check=True)
        print("Encryption completed successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Error during encryption: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def unlock_partition(partition, password, mount_point):
    """
    Unlocks the specified LUKS-encrypted partition using the password.
    """
    try:
        mapper_name = "private_partition"

        # Step 1: Unlock the partition
        unlock_command = f"echo {password} | sudo cryptsetup open {partition} {mapper_name} -q"
        subprocess.run(unlock_command, shell=True, check=True)
        print("Partition unlocked successfully.")

        # Step 2: Mount the unlocked partition
        os.makedirs(mount_point, exist_ok=True)
        mount_command = f"sudo mount /dev/mapper/{mapper_name} {mount_point}"
        subprocess.run(mount_command, shell=True, check=True)
        print(f"Partition mounted at {mount_point}.")

    except subprocess.CalledProcessError as e:
        print(f"Error during unlocking: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def main():
    private_partition = input("Enter the private partition (e.g., /dev/sda2): ")
    action = input("Do you want to lock or unlock the partition? (lock/unlock): ").strip().lower()

    password = "1234"
    mount_point = "/mnt/private"

    if action == "lock":
        lock_partition(private_partition, password)
    elif action == "unlock":
        unlock_partition(private_partition, password, mount_point)
    else:
        print("Invalid action. Please choose 'lock' or 'unlock'.")

if __name__ == "__main__":
    main()
