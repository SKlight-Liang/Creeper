'''
Copyright(c) Liang Yiyan, Pekin University, 2025. All rights reserved.

This program provides a series of universal crawler functions. 
Although these functions can often be detected and blocked by simple anti crawler systems, 
their universality is very high.

DISCLAIMER:
Please note that this program is only for scientific research and learning purposes.
The author shall not be held legally responsible for any consequences resulting from improper use of the program.

Function Table:
DownloadImage(URL: str, SavePath: str, MaxRetries: int = 3) -> bool -- Download images with retry mechanism
'''

import os
import time
import random
import requests

from FileProcess import LogMessage

# Download images
def DownloadImage(URL: str, SavePath: str, MaxRetries: int = 3) -> bool:
    for Attempt in range(1, MaxRetries + 1):
        try:
            # Header information can be added here to simulate browser behavior
            Response = requests.get(URL, timeout=10)

            # Download successful
            if Response.status_code == 200:
                # Ensure the directory exists before saving the file
                os.makedirs(os.path.dirname(SavePath), exist_ok=True)
                
                with open(SavePath, 'wb') as f:
                    f.write(Response.content)
                    LogMessage(f"Image saved to {SavePath} successfully.")
                    
                return True
            
            # Download failed
            else:
                # Output error log
                ERROR_MSG = f"Failed to download image from {URL}, status code: {Response.status_code} (Attempt {Attempt}/{MaxRetries})"
                LogMessage(ERROR_MSG, 'WARNING')

                # Wait before retrying
                if Attempt < MaxRetries:
                    time.sleep(random.uniform(2, 4))  
                    
        except requests.exceptions.Timeout:
            ERROR_MSG = f"Timeout while downloading image from {URL} (Attempt {Attempt}/{MaxRetries})"
            LogMessage(ERROR_MSG, 'WARNING')

            # Wait before retrying
            if Attempt < MaxRetries:
                time.sleep(random.uniform(2, 4))  
                
        except requests.exceptions.RequestException as e:
            ERROR_MSG = f"Network error while downloading image from {URL}: {str(e)} (Attempt {Attempt}/{MaxRetries})"
            LogMessage(ERROR_MSG, 'WARNING')

            # Wait before retrying
            if Attempt < MaxRetries:
                time.sleep(random.uniform(2, 4))  
    
    # All retries failed
    FINAL_ERROR_MSG = f"Failed to download image from {URL} after {MaxRetries} attempts"
    LogMessage(FINAL_ERROR_MSG, 'ERROR')

    return False