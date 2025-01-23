import subprocess
import sys

def install_xfs_tools():
    """Install the necessary tools for XFS filesystem handling."""
    try:
        # Update package list
        print("Updating package list...")
        subprocess.run(["sudo", "apt", "update"], check=True)

        # Install xfsprogs
        print("Installing xfsprogs package...")
        subprocess.run(["sudo", "apt", "install", "-y", "xfsprogs"], check=True)

        print("xfsprogs installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during installation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_xfs_tools()
