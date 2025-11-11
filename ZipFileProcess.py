'''
Copyright(c) Liang Yiyan, Pekin University, 2025. All rights reserved.

The following functions are mainly responsible for generating or reading zip files.
These functions often have unique functionalities and may not be suitable for all application scenarios.
Therefore, I would prefer to see them as a special example.
Perhaps we can refer to them when processing zip files in the future.

Function Table:
GenerateZIPFile(SourceDir: str, ZipFilePath: str, Totalitem: int = 20, 
                RecordFile: str = RECORD_FILE, RandomSeed: int = RANDOM_SEED) 
-- Randomly select a certain number of files from the source directory and package them into a zip file, 
    ensuring no duplicates with previously packed files.
GetFileNamesinZIP(ZipFilePath: str, SavePath: str = None) -> list
-- Extract all file names from a zip file and optionally save them to a JSON file.
'''

import os
import json
import random
import zipfile

from FileProcess import LogMessage
from FileProcess import GetFileNamesinDir

# The default record file to store packed file names
RECORD_FILE = "PackedFiles.json"
# The default random seed for reproducibility
RANDOM_SEED = 42

# Randomly select a certain number of files to package
def GenerateZIPFile(SourceDir: str, ZipFilePath: str, Totalitem: int = 20, RecordFile: str = RECORD_FILE, RandomSeed: int = RANDOM_SEED) -> None:
    # Determine whether the source directory exists
    if not os.path.exists(SourceDir):
        LogMessage(f"Source directory does not exist: {SourceDir}", Type="ERROR")
        return
    
    # Retrieve all file names in the source directory
    AllFiles = GetFileNamesinDir(SourceDir)

    # Read the names of files that have already been packed if possible
    PackedFiles = []
    if os.path.exists(RecordFile):
        try:
            with open(RecordFile, "r", encoding="utf-8") as f:
                PackedFiles = json.load(f)
            # Deduplicate the packed files list
            PackedFiles = list(set(PackedFiles))

        except Exception as e:
            LogMessage(f"Error reading packed file names from: {RecordFile}. Error: {str(e)}", Type="ERROR")

    #  Filter out already packed files
    AvailableFiles = [f for f in AllFiles if f not in PackedFiles]

    # If there are less than Totalitem available files, adjust the number to pack
    if len(AvailableFiles) < Totalitem:
        Totalitem = len(AvailableFiles)

    # Randomly select files to pack
    random.seed(RandomSeed)
    SelectedFiles = random.sample(AvailableFiles, Totalitem)

    # Create a zip file and add selected files
    try:
        with zipfile.ZipFile(ZipFilePath, 'w') as zipf:
            for file in SelectedFiles:
                zipf.write(os.path.join(SourceDir, file), file)
        LogMessage(f"Successfully created zip file: {ZipFilePath} with {Totalitem} files.")
    
    except Exception as e:
        LogMessage(f"Error creating zip file: {ZipFilePath}. Error: {str(e)}", Type="ERROR")
        return
    
    # Update the packed files record
    PackedFiles.extend(SelectedFiles)
    try:
        with open(RecordFile, "w", encoding="utf-8") as f:
            json.dump(PackedFiles, f, ensure_ascii=False, indent=4)
        LogMessage(f"Updated packed file names record: {RecordFile}")

    except Exception as e:
        LogMessage(f"Error updating packed file names record: {RecordFile}. Error: {str(e)}", Type="ERROR")


# Extract all file names from a zip file
def GetFileNamesinZIP(ZipFilePath: str, SavePath: str = None) -> list:
    FileNames = []
    try:
        with zipfile.ZipFile(ZipFilePath, 'r') as zip:
            FileNames = zip.namelist()
        LogMessage(f"Successfully retrieved file names from zip file: {ZipFilePath}")
    
    except Exception as e:
        LogMessage(f"Error retrieving file names from zip file: {ZipFilePath}. Error: {str(e)}", Type="ERROR")
        return []

    if SavePath:
        with open(SavePath, "w", encoding="utf-8") as f:
            json.dump(FileNames, f, ensure_ascii=False, indent=4)
        LogMessage(f"File names from zip saved to: {SavePath}")

    return FileNames