# rename_images

Renames image files with the oldest date found in EXIF metadata and file properties

Supports recursion of subdirectories and customizable formatting of file names

___
```
USAGE:
    python RenameImages.py [-r] [-f "formatting"] dir
    -r                :  Recurse into all subdirectories (optional)
    -f "format"       :  Custom formatting of file names (optional)
    dir               :  Folder containing images (required)


FORMATTING:
    Must be contained in quotations ""
    Reserved characters will be ignored  \ / : * ? " < > | 
    Date and time variables (must match case):  YYYY, YY, MM, DD, Hh, Mm, Ss
    Default formatting:  YYYY-MM-DD Hh-Mm-Ss


EXAMPLES:
    python RenameImages.py E:\Pictures
    python RenameImages.py -r E:\Pictures
    python RenameImages.py -f "YY-MM-DD Hh-Mm" E:\Pictures
    python RenameImages.py -f "YYYY.MM.DD_Hh.Mm.Ss" E:\Pictures
    python RenameImages.py -r -f "Vacation MM DD, YYYY" E:\Pictures
```
___