'''
Copyright(c) Liang Yiyan, Pekin University, 2025. All rights reserved.

This program includes some common file related operations for subsequent program calls.
For each function, we provide the 'SavePath' parameter to export the results in JSON file.
If you don't set this parameter, the result will only be returned. 
Additionally, the running log of the program will be stored in 'Process.log' file.
NOTE: These programs will not output any information in the terminal.

Function Table:
LogMessage(Message, Type="INFO") -- Write LOGS to default log file
GetFileNamesinDir(DirPath, SavePath=None) -> list -- Retrieve all file names in the file directory
GetFileName(FilePath) -> str -- Return the content before the last point
EncodeImageToBase64(ImagePath) -> str -- Encode the image to base64 string
'''

import os
import json
import base64
import logging

LOG_FILE = "Process.log"
# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Write LOGS to default log file
def LogMessage(Message: str, Type:str="INFO"):
    if Type == "INFO":
        logging.info(Message)
    elif Type == "WARNING":
        logging.warning(Message)
    elif Type == "ERROR":
        logging.error(Message)
    else:
        logging.debug(Message)
    
# Retrieve all file names in the file directory
def GetFileNamesinDir(DirPath:str, SavePath:str=None) -> list:
    try:
        FileNames = os.listdir(DirPath)
        LogMessage(f"Successfully retrieved file names from directory: {DirPath}")

        if SavePath:
            with open(SavePath, 'w') as f:
                json.dump(FileNames, f)
            LogMessage(f"File names saved to: {SavePath}")

        return FileNames
    except Exception as e:
        LogMessage(f"Error retrieving file names from directory: {DirPath}. Error: {str(e)}", Type="ERROR")
        return []
    
# Return the content before the last point
def GetFileName(FilePath:str) -> str:
    try:
        FilePath = os.path.basename(FilePath)
        FileName = os.path.splitext(FilePath)[0]
        LogMessage(f"Successfully retrieved file name from path: {FilePath}")
        return FileName
    
    except Exception as e:
        LogMessage(f"Error retrieving file name from path: {FilePath}. Error: {str(e)}", Type="ERROR")
        return ""

# Encode the image to base64 string
def EncodeImageToBase64(ImagePath:str) -> str:
    try:
        with open(ImagePath, "rb") as ImageFile:
            EncodedString = base64.b64encode(ImageFile.read()).decode('utf-8')
        return EncodedString
        
    except FileNotFoundError:
        LogMessage(f"Image file not found: {ImagePath}", Type="ERROR")
        return None
        
    except Exception as e:
        LogMessage(f"Error reading image file: {ImagePath}. Error: {str(e)}", Type="ERROR")
        return None