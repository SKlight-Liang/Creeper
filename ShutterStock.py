'''
Copyright(c) Liang Yiyan, Pekin University, 2025. All rights reserved.

This program can be used for bulk downloading of Shooterstock.com images,
according to the provided search keywords or specific webpage URLs.
Note that the first time opening a webpage requires human-machine verification.
To improve speed, there is no need to use human simulation algorithms 
during the process of pulling down the webpage.

DISCLAIMER:
Please note that this program is only for scientific research and learning purposes.
The author shall not be held legally responsible for any consequences resulting from improper use of the program.
'''

import os
import tqdm
import time
import json
import random

# Search parameters
SEARCH_KEYWORD = "iq-test"
SEARCH_ENGINE = "https://www.google.com"
PAGE = 1

# Set this if you want to download multiple pages
END_PAGE = 5

# Image folder path
IMAGE_FOLDER = "Images"
# Download information save path
DOWNLOAD_INFO_PATH = "DownloadImages.json"

def PageURL() -> str:
    URL_TEMPLATE = "https://www.shutterstock.com/search/{keyword}?dd_referrer={engine}&page={page}"
    return URL_TEMPLATE.format(keyword=SEARCH_KEYWORD, engine=SEARCH_ENGINE, page=PAGE)

# The initial URL contains "-260nw-"
# We need to replace it with "-600nw-" to get higher resolution images
def ImageURL(url: str) -> str:
    return url.replace("-260nw-", "-600nw-")

# Analyze image addresses in web pages
from bs4 import BeautifulSoup   
def GetImageLinks(PageContent: str) -> list:
    Scraper = BeautifulSoup(PageContent, 'lxml')

    # The description of the image on the webpage is as follows:
    # HTML:
    # <picture>
    #     <img class="mui-1l7n00y-thumbnail" src="..." ...>
    # </picture>
    # Extract all "src" attributes under the <img> tags.

    ImageTags = Scraper.find_all('img', class_ = 'mui-1l7n00y-thumbnail')
    ImageLinks = [img['src'] for img in ImageTags if 'src' in img.attrs]

    return list(set(ImageLinks))


from ChromeSimulate import OpenWebpage
from ChromeSimulate import ScrollToBottom
from ChromeSimulate import RetrieveWebpageContent
from ChromeSimulate import CloseBrowser

from Creeper import DownloadImage
from FileProcess import LogMessage

def ShutterStockDownloader():
    # Open the target webpage
    if not OpenWebpage(PageURL()):
        return
    
    # Scroll to the bottom of the page without human simulation
    if not ScrollToBottom(SimulateHumans=False):
        return
    
    # Retrieve webpage content
    WebpageContent = RetrieveWebpageContent()
    if not WebpageContent:
        return
    
    # Obtain image links
    ImageLinks = GetImageLinks(WebpageContent)

    # Download images
    DownloadedInfo = []
    for ImageLink in tqdm.tqdm(ImageLinks, desc="Downloading images", unit="image"):
        ImageName = ImageLink.split('-')[-1]
        SavePath = os.path.join(IMAGE_FOLDER, ImageName)

        # If the image already exists, skip downloading
        if os.path.exists(SavePath):
            continue

        # Render higher resolution image link
        ImageLink = ImageURL(ImageLink)

        # Download images
        if DownloadImage(ImageLink, SavePath, MaxRetries=3):
            DownloadedInfo.append({
                "ImageLink": ImageLink,
                "SavePath": SavePath
            })
            # Random wait time between downloads to avoid being blocked
            time.sleep(random.uniform(1, 2))

    LogMessage(f"Downloaded {len(DownloadedInfo)}/{len(ImageLinks)} images successfully.")
    return DownloadedInfo

    
if __name__ == "__main__":
    Result = ShutterStockDownloader()

    # Save download information
    if Result:
        with open(DOWNLOAD_INFO_PATH, "w", encoding="utf-8") as f:
            json.dump(Result, f, indent=4, ensure_ascii=False)
    
    CloseBrowser()

    # If you want to download multiple pages continuously
    # while ('END_PAGE' in globals() and PAGE <= END_PAGE):
    #     Result = ShutterStockDownloader()

    #     # Save download information using append mode
    #     if Result:
    #         with open(DOWNLOAD_INFO_PATH, "a", encoding="utf-8") as f:
    #             for item in Result:
    #                 f.write(json.dumps(item, ensure_ascii=False) + "\n")

    #     PAGE += 1

    # CloseBrowser()