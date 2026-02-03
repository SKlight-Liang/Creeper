'''
Copyright(c) Liang Yiyan, Pekin University, 2026. All rights reserved.

This program mainly focus on the process of images.
For example, sometimes we may want to know there are how many similar images in a folder.
Or sometimes we just want to add a white border resulting in better OCR results. 
So I gathered and encapsulated some common image processing functions here.
Hope these functions can help you in your work and give you some inspiration.

Function Table:
'''

from PIL import Image
from PIL import ImageOps

from FileProcess import LogMessage

# Add white border around the image
def AddWhiteBorder(ImagePath: str, BorderSize: int, SavePath: str = None) -> Image.Image:
    try:
        # Open the image
        Img = Image.open(ImagePath)
        # Add white border
        BorderedImg = ImageOps.expand(Img, border=BorderSize, fill='white')

        if SavePath:
            BorderedImg.save(SavePath)
            LogMessage(f"Image with white border saved to: {SavePath}", Type="INFO")

        return BorderedImg
    
    except Exception as e:
        LogMessage(f"Error adding white border to image: {ImagePath}. Error: {str(e)}", Type="ERROR")
        return None

