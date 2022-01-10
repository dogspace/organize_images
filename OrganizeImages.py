#==============================================================================================
# Author:  https://github.com/dogspace
#
# Renames image files with the earliest date found (usually the date the image was taken).
# Moves all files located in subfolders into the image_folder. Deletes empty subfolders.
#=============================================================================================


import os
import sys
import exifread
from shutil import move
from datetime import datetime


valid_extensions   = [".jpg", ".jpeg", ".png", ".bmp"]
file_count = 0
skip_count = 0
move_count = 0
loop_count = 0

# Returns earliest date found in file properties and EXIF metadata
def get_dates(filepath):
    dates = []
    # Get last modified and created dates
    date_modified = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y.%m.%d %H.%M.%S")
    date_created = datetime.fromtimestamp(os.path.getctime(filepath)).strftime("%Y.%m.%d %H.%M.%S")
    dates.append(date_modified)
    dates.append(date_created)

    # Get metadata dates
    image = open(filepath, 'rb')
    tags = exifread.process_file(image, details=False)
    if "EXIF DateTimeDigitized" in tags.keys(): dates.append(str(tags["EXIF DateTimeDigitized"]))
    if "EXIF DateTimeOriginal" in tags.keys():  dates.append(str(tags["EXIF DateTimeOriginal"]))
    if "Image DateTime" in tags.keys():         dates.append(str(tags["Image DateTime"]))
    image.close()

    # Replace invalid chars, filter out invalid dates, sort oldest to newest
    dates = [d.replace(":", ".") for d in dates if "0000" not in d and len(d.strip()) > 0]
    dates.sort()
    if len(dates) < 1: print("\n\n\n!!!!!!!!!!!!!!!!!!!! DATES IS EMPTY !!!!!!!!!!!!!!!!!!!!n\n\n")
    return dates[0]

# Loops through folder, renames and/or moves files
def parse_folder(folder, rename_files, combine_subfolders):
    global file_count, skip_count, move_count, loop_count
    loop_count = loop_count + 1
    if loop_count > 2: return   #TEMP TEMP TEMP TEMP

    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        # Recurse if folder
        if os.path.isdir(filepath):
            parse_folder(filepath, rename_files, combine_subfolders)
        else:
            file_count = file_count + 1
            # Check file extension
            file_ext = os.path.splitext(filename)[1]
            is_image = file_ext.lower() in valid_extensions

            # Rename image files with date
            if rename_files:
                if is_image:
                    new_filename = get_dates(filepath)
                    print(f"{filename}  {new_filename}")
                    # RENAME FILES WIP
                else:
                    skip_count = skip_count + 1
                    print(f"[SKIPPING INVALID TYPE]  {filepath}")

            # Move file to provided folder
            if combine_subfolders:
                move_count = move_count + 1
                # MOVE FILES WIP
                
    print(f"\nFiles scanned:   {file_count}")
    print(f"Files renamed:   {file_count - skip_count}")
    print(f"Files skipped:   {skip_count}")
    print(f"Files moved:     {move_count}")
    print(f"Loops run:       {loop_count}")
    return

# Prints help message
def display_help():
    print(f"""
ERROR WITH ARGUMENT SYNTAX  :(
Please see the help message below.\n
    THIS PROGRAM:
      Used to organize an image folder. See arguments for details.\n
    OPTIONAL ARGUMENTS:
      -rename
          Renames image files with the earliest date found (usually the date the image was taken).
      -combine
          Moves all files located in subfolders into the image_folder. Deletes empty subfolders.\n
    REQUIRED ARGUMENTS:
      Path of image folder\n
    USAGE:
      python OrganizeImages.py [-rename] [-combine] image_folder\n
    EXAMPLES:
      python OrganizeImages.py -rename C:\\Users\\username\Desktop\Pictures
      python OrganizeImages.py -combine C:\\Users\\username\Desktop\Pictures
      python OrganizeImages.py -rename -combine C:\\Users\\username\Desktop\Pictures
    """)

# Processes user input
def main():
    flags = ["-rename", "-combine"]
    if len(sys.argv) >= 3 and sys.argv[1] in flags:
        # Get the folder path
        arg_path = " ".join(sys.argv[3:]) if sys.argv[2] in flags else " ".join(sys.argv[2:])
        # Ensure folder path is valid
        if os.path.isdir(arg_path):
            # Confirm that the user wants to proceed
            if sys.argv[1] in flags and sys.argv[2] in flags:
                print(f"This will rename images and combine all subfolders in  {arg_path}")
            elif "-rename" in sys.argv:
                print(f"This will rename images in  {arg_path}")
            else:
                print(f"This will combine all subfolders in  {arg_path}")
            answer = ""
            while answer.lower() != "y" and answer.lower() != "n":
                answer = input("Proceed?  (Y/n):  ")
            if answer == "n": sys.exit()
            # Parse folder
            parse_folder(arg_path, "-rename" in sys.argv, "-combine" in sys.argv)
        else:
            display_help()
    else:
        display_help()
    return


if __name__ == "__main__": main()
