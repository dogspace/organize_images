#==============================================================================================
# Author:  https://github.com/dogspace
#
# Renames image files with the oldest date found in EXIF metadata and file properties
# Supports recursion of subdirectories and customizable formatting of file names
#=============================================================================================


import os
import sys
import exifread
from datetime import datetime


valid_extensions   = [".jpg", ".jpeg", ".png", ".bmp"]
folder_count = 1
image_count = 0
skip_count = 0
proceed_prompt = False


# Prints help message
def display_help():
    print(f"""
THIS PROGRAM:  Renames image files with the oldest date found in EXIF metadata and file properties\n
    USAGE:
      python RenameImages.py [-r] [-f "formatting"] dir
      -r                :  Recurse into all subdirectories (optional)
      -f "format"       :  Custom formatting of file names (optional)
      dir               :  Folder containing images (required)\n
    FORMATTING:
      Must be contained in quotations ""
      Reserved characters will be ignored  \ / : * ? " < > | 
      Date and time variables (must match case):  YYYY, YY, MM, DD, Hh, Mm, Ss
      * Default formatting:  YYYY-MM-DD Hh-Mm-Ss\n
    EXAMPLES:
      python RenameImages.py E:\Pictures
      python RenameImages.py -r E:\Pictures
      python RenameImages.py -f "YY-MM-DD Hh-Mm" E:\Pictures
      python RenameImages.py -f "YYYY.MM.DD_Hh.Mm.Ss" E:\Pictures
      python RenameImages.py -r -f "Vacation MM DD, YYYY" E:\Pictures\n
    """)

# Returns earliest date found in file properties and EXIF metadata
def get_date(filepath):
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
    date_values = {}
    # Ensure a valid date was found, separate into dictionary for easy formatting
    date_values = {}
    if len(dates) == 0:
        print(f"\n\nERROR: NO DATES FOUND FOR {filepath}")
    elif len(dates[0]) != 19:
        print(f"\n\nERROR: INVALID DATE LENGTH FOR {filepath}")
    else:
        date_str = dates[0]
        date_values = {
            "YYYY": date_str[0:4],
            "YY":   date_str[2:4],
            "MM":   date_str[5:7],
            "DD":   date_str[8:10],
            "Hh":   date_str[11:13],
            "Mm":   date_str[14:16],
            "Ss":   date_str[17:] }
    return date_values

# Loops through folder(s), renames image files
def parse_folder(folder, recurse, formatting):
    global folder_count, image_count, skip_count, proceed_prompt
    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        # Check if folder, recurse if enabled
        if os.path.isdir(filepath) and recurse:
            folder_count = folder_count + 1
            parse_folder(filepath, recurse, formatting)
        else:
            # Check file extension
            file_ext = os.path.splitext(filename)[1]
            is_image = file_ext.lower() in valid_extensions
            if is_image:
                image_count = image_count + 1
                # Get earliest date, format to create new filename/filepath
                date_values = get_date(filepath)
                if date_values == {}:
                    return
                new_filename = formatting
                for key in date_values.keys():
                    if key in new_filename:
                        new_filename = new_filename.replace(key, date_values[key])
                new_filepath = os.path.join(folder, new_filename + file_ext)
                # If the new filename already exists, append incrementing numbers
                # Compare old/new filepaths to maintain formatting if the script is run more than once
                if os.path.exists(new_filepath) and filepath != new_filepath:
                    dup_count = 1
                    while True:
                        temp_filename = new_filename + " (" + str(dup_count) + ")"
                        temp_filepath = os.path.join(folder, temp_filename + file_ext)
                        if os.path.exists(temp_filepath) and filepath != temp_filepath:
                            dup_count = dup_count + 1
                        else:
                            new_filename = temp_filename
                            new_filepath = temp_filepath
                            break
                    # Confirm that the user wants to proceed after 50 duplicates
                    if dup_count > 50 and proceed_prompt == False:
                        print("\n\nWARNING: OVER 50 DUPLICATE DATES SO FAR")
                        while True:
                            prompt = input("Proceed?  (Y/n):  ")
                            if len(prompt) > 0:
                                if prompt[0].lower() == "y":
                                    proceed_prompt = True
                                    break
                                elif prompt[0].lower() == "n":
                                    return
                                else:
                                    continue
                    # Force exit after 1000 duplicate names
                    if dup_count > 1000:
                        print("\n\nERROR: OVER 1000 DUPLICATE DATES, EXITING")
                        return
                # Rename image file
                if filepath != new_filepath:
                    os.rename(filepath, new_filepath)
            else:
                skip_count = skip_count + 1
    return

# Processes user input
def main():
    recurse_flag = "-r" in sys.argv
    format_flag = "-f" in sys.argv
    formatting = "YYYY-MM-DD Hh-Mm-Ss"
    folder_path = ""
    # Process user input
    if len(sys.argv) >= 2:
        if recurse_flag and format_flag and len(sys.argv) >= 5:
            formatting = "".join(i for i in sys.argv[3] if i not in r'\/:*?"<>|')
            folder_path = "".join(sys.argv[4:])
        elif format_flag and len(sys.argv) >= 4:
            formatting = "".join(i for i in sys.argv[2] if i not in r'\/:*?"<>|')
            folder_path = "".join(sys.argv[3:])
        elif recurse_flag and len(sys.argv) >= 3:
            folder_path = "".join(sys.argv[2:])
        else:
            folder_path = "".join(sys.argv[1:])
    # Ensure folder path is valid
    if os.path.isdir(folder_path) and folder_path != "/":
        parse_folder(folder_path, recurse_flag, formatting)
        print(f"\nFolders scanned: {folder_count}   |   Images renamed: {image_count}   |   Files skipped: {skip_count}\n\n")
    else:
        display_help()
    return


if __name__ == "__main__": main()
