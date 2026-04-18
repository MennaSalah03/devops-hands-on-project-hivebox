""" Getting the version tag and printing it """
import sys
import os

def version_getter(version_file):
    """Retreives the current version tag of the hivebox app (and image)"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(os.path.join(base_dir, version_file), "r", encoding="utf-8") as file:
            version = file.readline().rstrip()
    except FileNotFoundError:
        print("Version file not found.")
        sys.exit(1)
    return version

if __name__ == "__main__":
    # Print version and exit
    print(version_getter("version.txt"))
    sys.exit(0)
