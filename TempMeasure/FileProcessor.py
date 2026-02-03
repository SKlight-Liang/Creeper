'''
Copyright(c) Liang Yiyan, Pekin University, 2025. All rights reserved.

These programs are used to temporarily process some files.
The reason why we need to perform these processes may be because the output file format is not satisfactory, 
or there are some special situations that we have not considered.
Therefore, many programs here are likely to be used only once,
and I will not write them in a more general form.
If you are interested, you may take a look and find that they are really simple.
After all, they just need to be usable. No one will pay attention to how they are implemented.

DISCLAIMER:
Please note that this program is only for scientific research and learning purposes.
The author shall not be held legally responsible for any consequences resulting from improper use of the program.

Function Table:
MoveFolders(FolderNames: str, SourcePath: str, TargetPath: str) -> None
-- Move specified folders from source path to target path
'''

import os
import json

from FileProcess import LogMessage

# This function is used to move one folder to another place
# The names of the folder we want to copy will be given in a JSON file
# That means, the original folder we want to move is: SourcePath/FolderName
# And we want to move it to: TargetPath/FolderName
def MoveFolders(FolderNames: str = None, SourcePath: str = None, TargetPath: str = None) -> None:
    if not os.path.exists(FolderNames):
        LogMessage(f"Folder names JSON file does not exist: {FolderNames}", Type="Error")
        return
    
    # Load the folder names from the JSON file
    with open(FolderNames, "r", encoding="utf-8") as infile:
        NamesList = json.load(infile)

    # Ensure the target path exists
    if not os.path.exists(TargetPath):
        os.makedirs(TargetPath)

    SuccessCount = 0
    for Name in NamesList:
        SourceFolder = os.path.join(SourcePath, Name)
        TargetFolder = os.path.join(TargetPath, Name)

        if os.path.exists(SourceFolder):
            os.rename(SourceFolder, TargetFolder)
            SuccessCount += 1

    LogMessage(f"Moved {SuccessCount} folders to {TargetPath}", Type="INFO")
