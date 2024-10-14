import os
import shutil
from . import logging


def create_rtlo_file(input_file, output_directory, spoofed_extension):
    filename, extension = os.path.splitext(os.path.abspath(input_file))
    reverse = spoofed_extension[::-1]
    newname = os.path.join(
        output_directory, f"{os.path.basename(filename)}\u202e{reverse}{extension}"
    )

    if os.path.isfile(newname):
        logging.info("[yellow]Removing old file: {}[/]".format(newname), extra={"markup": True})
        os.remove(newname)

    try:
        shutil.copy(input_file, newname)
    except Exception as e:
        logging.error("[bold red]Error during spoofing extension using RTLO: {}[/]".format(e), extra={"markup": True})
        return None

    return os.path.abspath(newname)
