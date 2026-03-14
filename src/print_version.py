import sys

def version_getter(version_file):
    """Retreives the current version tag of the hivebox app (and image)"""
    try:
        with open(version_file, "r", encoding="utf-8") as file:
            version = file.readline()
    except FileNotFoundError:
        print("Version file not found.")
        sys.exit(1)
    return version

if __name__ == "__main__":
    # Print version and exit
    print(version_getter("version.txt"))
    sys.exit(0)
