'''
Copyright(c) Liang Yiyan, Pekin University, 2025. All rights reserved.

Since all the questions we obtained in the previous process were images, 
we need to first perform an OCR operation to extract the text from the images.
However, we found that there were some inexplicable illusions when using large models for OCR, 
so we did not directly choose to use models such as Qwen for OCR, 
but instead switched to the architecture of MinerU.
Although MinerU also incorporated model assistance during OCR, 
its technical report indicates that they minimized the occurrence of illusions as much as possible through a complex workflow. 
The fact is indeed true, but there are still some cases where MinerU recognizes some text as headers, 
resulting in the loss of this part of the data in the final recognition result. 
We will address this issue in the subsequent workflow.

NOTE:
The MinerU API has a feature that requires the URL address of the uploaded image rather than the file itself.
Please ensure that the image you want to upload has a public access address.
You can use some online platforms to achieve this.

DISCLAIMER:
Please note that this program is only for scientific research and learning purposes.
The author shall not be held legally responsible for any consequences resulting from improper use of the program.

Function Table:
RenderImageURL(ServerBaseURL: str = SERVERURL, ImagePath: str = None) -> str -- Render the absolute URL for the image
UploadImagetoMinerU(ImageURL: str = None, Retries: int = 3) -> str -- Upload image to MinerU and get the OCR task ID
GetOCRResURLfromMinerU(TaskID: str, Retries: int = 3) -> str -- Retrieve the URL of the OCR result ZIP file from MinerU
RetrieveOCRResult(TaskID: str, SavePath: str, Retries: int = 3) -> bool -- Get the OCR result content from MinerU
'''

import os
import re
import time
import zipfile
import requests

from FileProcess import LogMessage

# Your MinerU API Token here
APITOKEN = ""
# Your server base URL here
SERVERURL = ""

# The default path to save OCR results
DEFAULT_SAVE_PATH = "./OCRResults/"

# The base URL for MinerU API
# There is no need to modify this unless the official API address changes
# Or you are using a private deployment of MinerU
BASEURL = "https://mineru.net/api/v4/extract/task"
RESBASEURL = "https://mineru.net/api/v4/extract/task/"

# The headers for MinerU API requests
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {APITOKEN}"
}

# Render the absolute URL that is accessible publicly for the image to be uploaded
def RenderImageURL(ServerBaseURL: str = SERVERURL, ImagePath: str = None) -> str:
    # Ensure that ImagePath conforms to URL absolute path syntax
    ImageRelURL = re.sub(r'\\+', '/', ImagePath)
    # Combine the base URL and relative path to form the absolute URL
    if ImageRelURL.startswith('/') and ServerBaseURL.endswith('/'):
        ImageAbsURL = ServerBaseURL[:-1] + ImageRelURL
    elif not ImageRelURL.startswith('/') and not ServerBaseURL.endswith('/'):
        ImageAbsURL = ServerBaseURL + '/' + ImageRelURL
    else:
        ImageAbsURL = ServerBaseURL + ImageRelURL
    
    return ImageAbsURL

# Upload image to MinerU and get the OCR task ID
def UploadImagetoMinerU(ImageURL: str = None, Retries: int = 3) -> str:
    LogMessage(f"Uploading image to MinerU: {ImageURL}", Type="INFO")

    # If no image URL is provided, return None
    if ImageURL is None:
        LogMessage("No image URL provided for upload.", Type="ERROR")
        return None

    # Prepare the payload for the API request
    Payload = {
        "url": ImageURL,
        "model_version": "vlm",
        "is_ocr": True
    }

    for attempt in range(1, Retries + 1):
        try:
            # Send the POST request to MinerU API
            Response = requests.post(url=BASEURL, headers=HEADERS, json=Payload)
            # Sleep for a short time to avoid hitting rate limits
            time.sleep(0.5)

            # Check if the request was successful
            if Response.status_code == 200:
                # Parse the JSON response
                ResponseData = Response.json()
                # Get the task ID from the response
                TaskID = ResponseData.get("data", {}).get("task_id", "")

                return TaskID
            
            else:
                LogMessage(f"Attempt {attempt}: Failed to upload image to MinerU.", Type="ERROR") 
                LogMessage(f"Status Code: {Response.status_code}. Response: {Response.text}", Type="ERROR")

        except Exception as e:
            LogMessage(f"Exception occurred during upload attempt {attempt}: {e}", Type="ERROR")

    return None

# For each question, we need to perform two OCR operations, 
# one for the question image and the other for question analysis.

# Usage Examples:
# QuestionImageURL = RenderImageURL(SERVERURL, Question["QuestionImagePath"])
# QuestionTaskID = UploadImagetoMinerU(QuestionImageURL)
# AnswerImageURL = RenderImageURL(SERVERURL, Question["AnswerImagePath"])
# AnswerTaskID = UploadImagetoMinerU(AnswerImageURL)

# Retrieve the URL of the OCR result ZIP file from MinerU using the Task ID
def GetOCRResURLfromMinerU(TaskID: str, Retries: int = 3) -> str:
    # Construct the result URL
    ResultURL = RESBASEURL + TaskID

    # Retry mechanism for robustness
    for attempt in range(1, Retries + 1):
        try:
            # Send the GET request to MinerU API
            Response = requests.get(url=ResultURL, headers=HEADERS)

            # Check if the request was successful
            if Response.status_code == 200:
                # Parse the JSON response
                ResponseData = Response.json()
                # Get the data from the response
                Data = ResponseData.get("data", {})
                State = Data.get("state", "")

                # Check if the OCR task is done
                if State == "done":
                    # Get the full ZIP URL from the response
                    ZIPURL = Data.get("full_zip_url", "")
                    if ZIPURL != "":
                        return ZIPURL
                    
                    # If URL is empty, log error and retry
                    LogMessage(f"OCR task completed but no ZIP URL found for Task ID: {TaskID}", Type="ERROR")
                    # Wait before retrying
                    time.sleep(1)

                else:
                    # OCR task not done yet, log info and retry
                    LogMessage(f"OCR task not done yet for Task ID: {TaskID}. Current state: {State}", Type="INFO")
                    # Wait for some time before checking again
                    time.sleep(10)

            else:
                # Failed to retrieve OCR result from MinerU
                LogMessage(f"Attempt {attempt}: Failed to retrieve OCR result from MinerU.", Type="ERROR") 
                LogMessage(f"Status Code: {Response.status_code}. Response: {Response.text}", Type="ERROR")
                # Wait before retrying
                time.sleep(1)

        except Exception as e:
            LogMessage(f"Exception occurred during result retrieval attempt {attempt}: {e}", Type="ERROR")
            continue

    return None

# Get the OCR result content from MinerU using the task ID
# And copy the key files to the specified directory
def RetrieveOCRResult(TaskID: str, SavePath: str = DEFAULT_SAVE_PATH, Retries: int = 3) -> bool:
    LogMessage(f"Retrieving OCR result from MinerU for Task ID: {TaskID}", Type="INFO")

    # If no Task ID is provided, return None
    if TaskID is None or TaskID == "":
        LogMessage("No Task ID provided for OCR result retrieval.", Type="ERROR")
        return False
    
    for attempt in range(1, Retries + 1):
        # Obtain the result ZIP URL from MinerU
        ResultURL = GetOCRResURLfromMinerU(TaskID, Retries=Retries)
        if ResultURL is None:
            LogMessage(f"Failed to obtain OCR result URL for Task ID: {TaskID}", Type="ERROR")
            return None, False
        
        # Download the ZIP file from the obtained URL
        ZIPFile = requests.get(ResultURL)

        # Check if the ZIP file was downloaded successfully
        if ZIPFile.status_code != 200:
            LogMessage(f"Attempt {attempt}: Failed to download OCR result ZIP file.", Type="ERROR") 
            LogMessage(f"Status Code: {ZIPFile.status_code}. Response: {ZIPFile.text}", Type="ERROR")
            # Wait before retrying
            time.sleep(1)
            continue

        # Save the ZIP file temporarily
        with open("Result.zip", "wb") as f:
            f.write(ZIPFile.content)

        # Try to extract the content from the ZIP file
        try:
            with zipfile.ZipFile("result.zip", "r") as ZIPREF:
                # Copy full.md, layout.json and images folder(if exists) to SavePath
                ZIPREF.extract("full.md", SavePath)
                ZIPREF.extract("layout.json", SavePath)
                if "images/" in ZIPREF.namelist():
                    ZIPREF.extractall(
                        path=SavePath, 
                        members=[name for name in ZIPREF.namelist() if name.startswith("images/")]
                    )

            # Delete the temporary ZIP file
            os.remove("Result.zip")
                
            return True
        
        except Exception as e:
            LogMessage(f"Exception occurred while extracting OCR result ZIP file: {e}", Type="ERROR")
            # Wait before retrying
            time.sleep(1)
            continue

    return False
