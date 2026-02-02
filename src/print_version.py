import sys

def version_printer(version_file):
    try:
        with open(version_file, "r") as file:
            version = file.readline()
            print(version)
    except FileNotFoundError:
        print("Version file not found.")
        sys.exit(1)

if __name__ == "__main__":
    # Print version and exit
        version_printer("version.txt")
        sys.exit(0)