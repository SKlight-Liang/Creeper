'''
Copyright(c) Liang Yiyan, Pekin University, 2025. All rights reserved.

This program can search for similar images based on a given image.
Here we used ShutterStock.com's similar image search engine API to find similar images.
This API will return the URL of the images that are similar to the original image.
Of course, we will not use APIs to download images.
This is because the API has strict limitations on the speed of image downloads.

DISCLAIMER:
Please note that this program is only for scientific research and learning purposes.
The author shall not be held legally responsible for any consequences resulting from improper use of the program.
'''

import os
import time
import json
import requests

from FileProcess import LogMessage
from FileProcess import EncodeImageToBase64

# Time interval between requests to avoid hitting rate limits
# Note that Shutterstock has extremely strict restrictions on free APIs
# Only 5 requests are supported per minute
WAIT_TIME_BETWEEN_REQUESTS = 120
WAIT_TIME_BETWEEN_RETRIES = 30

# Your Shutterstock API Token here
API_TOKEN = ""
# Path of the image to be searched
IMAGE_PATH = "InputImage.png"  
# Number of results per page
PER_PAGE = 100
# Path to save the search results
RESULT_PATH = "SimilarImages.json"

class ShutterstockReverseImageSearchEngine:
    # Initialize API Engine
    def __init__(self, APITOKEN: str, PERPAGE: int) -> None:
        self.BaseURL = "https://api.shutterstock.com/v2"
        self.APIToken = APITOKEN
        self.PerPage = PERPAGE
        self.Headers = {
            "Authorization": f"Bearer {APITOKEN}",
            "Content-Type": "application/json"
        }       

    # Upload images and obtain corresponding IDs
    def UploadImage(self, ImagePath: str) -> str:
        # Encode the image to base64 string
        EncodedImage = EncodeImageToBase64(ImagePath)
        if not EncodedImage:
            return None
        
        URL = f"{self.BaseURL}/cv/images"
        Data = {
            "base64_image": EncodedImage
        }
        
        try:
            # Send POST request to upload image
            Response = requests.post(URL, headers=self.Headers, json=Data)
            Response.raise_for_status()
            
            # Parse the response to get uploadID
            Result = Response.json()
            UploadID = Result.get("upload_id")
            
            if UploadID:
                LogMessage(f"Image uploaded successfully, uploadID: {UploadID}")
                return UploadID
            
            else:
                LogMessage("Error: uploadID not found in response", Type="ERROR")
                LogMessage(f"Full response: {Result}", Type="ERROR")
                return None
                
        except requests.exceptions.RequestException as e:
            LogMessage(f"Error uploading image: {ImagePath}. Error: {str(e)}", Type="ERROR")
            if hasattr(e, 'response') and e.response:
                LogMessage(f"Status code: {e.response.status_code}", Type="ERROR")
                LogMessage(f"Response content: {e.response.text}", Type="ERROR")
            return None

    # Search for similar images using uploadID
    def SearchSimilarImages(self, UploadID: str) -> dict:
        URL = f"{self.BaseURL}/cv/similar/images"
        Headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.APIToken}"
        }
        Params = {
            "asset_id": UploadID,
            "per_page": self.PerPage
        }

        try:
            # Send GET request to search similar images
            Response = requests.get(URL, headers = Headers, params = Params)
            Response.raise_for_status()

            Results = Response.json()
            return Results

        except requests.exceptions.RequestException as e:    
            LogMessage(f"Error searching similar images for uploadID: {UploadID}. Error: {str(e)}", Type="ERROR")
            if hasattr(e, 'response') and e.response:
                LogMessage(f"Status code: {e.response.status_code}", Type="ERROR")
                LogMessage(f"Response content: {e.response.text}", Type="ERROR")
            return None    

    # Main function to perform reverse image search
    def ReverseImageSearch(self, ImagePath: str, RetryTimes: int = 3) -> dict:
        LogMessage(f"Starting reverse image search for: {ImagePath}")

        for Attempt in range(RetryTimes):
            UploadID = self.UploadImage(ImagePath)
            if not UploadID:
                LogMessage(f"Upload failed for image: {ImagePath}. Attempt {Attempt + 1} of {RetryTimes}", Type="WARNING")
                time.sleep(WAIT_TIME_BETWEEN_RETRIES)
                continue
            
            time.sleep(0.5)
            Results = self.SearchSimilarImages(UploadID)
            if Results:
                LogMessage(f"Reverse image search successful for: {ImagePath}")
                return Results
            else:
                LogMessage(f"Search failed for uploadID: {UploadID}. Attempt {Attempt + 1} of {RetryTimes}", Type="WARNING")
                time.sleep(WAIT_TIME_BETWEEN_RETRIES)

        LogMessage(f"All attempts failed for image: {ImagePath}", Type="ERROR")
        return None
    
if __name__ == "__main__":
    # Ensure API token is provided
    if not API_TOKEN:
        LogMessage("API token is not provided. Please set the API_TOKEN variable.", Type="ERROR")
        exit(1)

    # Check if the image file exists
    if not os.path.isfile(IMAGE_PATH):
        LogMessage(f"Image file does not exist: {IMAGE_PATH}", Type="ERROR")
        exit(1)

    # Initialize the Shutterstock reverse image search engine
    ShutterstockEngine = ShutterstockReverseImageSearchEngine(API_TOKEN, PER_PAGE)
    # Perform reverse image search
    SearchResults = ShutterstockEngine.ReverseImageSearch(IMAGE_PATH)

    if SearchResults:
        # Save the search results to a JSON file
        with open(RESULT_PATH, 'w', encoding='utf-8') as ResultFile:
            json.dump(SearchResults, ResultFile, indent=4, ensure_ascii=False)
        LogMessage(f"Search results saved to: {RESULT_PATH}")
