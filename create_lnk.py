# python lnk.py output.lnk C:/Windows/System32/cmd.exe -i "c:/windows/system32/notepad.exe" --mode Minimized -w C:/Windows/System32

import sys
import pylnk
import argparse
from datetime import datetime

def create_lnk(name, target, mode, args, description, icon, workingDir, is_dir = False):

    if len(name) < 4 or name[-4:] != ".lnk":
        name = "{0}.lnk".format(name)

    target = target.replace("/", "\\").rstrip("\\").split("\\")
    target_file = target[-1]
    target_drive = target[0]

    if icon is not None:
        icon = icon.replace("/", "\\").rstrip("\\")

    lnk = populate_lnk(name, target, mode, args, description, icon, workingDir)
    levels = list(pylnk.path_levels("\\".join(target)))
    elements = [pylnk.RootEntry(pylnk.ROOT_MY_COMPUTER), pylnk.DriveEntry(target_drive)]
    for level in target:
        entry = build_entry(level)
        elements.append(entry)
    entry = build_entry(target_file)
    if not is_dir:
        entry.type = pylnk.TYPE_FILE
    elements.append(entry)

    lnk.shell_item_id_list = pylnk.LinkTargetIDList()
    lnk.shell_item_id_list.items = elements
    write_lnk(lnk)

    return 0
    
def populate_lnk(name, target, mode, args, description, icon, workingDir):
    lnk = pylnk.create(name)
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
        lnk.icon_index = 0

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
    entry = pylnk.PathSegmentEntry()
    entry.type = pylnk.TYPE_FOLDER
    entry.file_size = 0

    n = datetime.now()
    entry.modified = n
    entry.created = n
    entry.accessed = n

    entry.short_name = name
    entry.full_name = entry.short_name

    return entry

def write_lnk(lnk):
    with open(lnk.file, 'wb') as f:
        lnk.write(f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='lnk.py', description='Create a Shortcut (.lnk)', usage='%(prog)s sample.lnk c:/windows/system32/cmd.exe')
    parser.add_argument('-d', '--directory', action='store_true', dest='is_dir', 
                        default=False, help='Target is a directory')
    parser.add_argument('name', action='store', help='Name of shortcut file')
    parser.add_argument('target', action='store', help='Target file path')
    parser.add_argument('-a', '--arguments', action='store', dest='arguments', help='Arguments to add to the target, e.g. /c powershell.exe -ep bypass')
    parser.add_argument('--mode', default='Minimized', const='Minimized', nargs='?', choices=['Maximized', 'Normal', 'Minimized'], help='Set the type of window mode for the lnk file, default: %(default)s)')
    parser.add_argument('--desc', action='store', dest='description', help='Description for the lnk file')
    parser.add_argument('-i', '--icon', action='store', dest='icon', help='Icon for the lnk file, e.g. c:/windows/system32/notepad.exe')
    parser.add_argument('-w', '--working', action='store', dest='working', help='Specify the working directory, e.g. c:/users/public/')
    args = parser.parse_args()

    create_lnk(args.name, args.target, args.mode, args.arguments, args.description, args.icon, args.working, args.is_dir)

    sys.exit()