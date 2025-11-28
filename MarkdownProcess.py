'''
Copyright(c) Liang Yiyan, Pekin University, 2025. All rights reserved.

This file contains some basic Markdown text processing functions,
such as rendering Markdown text into images, extracting images contained in Markdown text,
and other related functions. Of course, I have only listed those that I think are useful.
I hope that these methods will be further supplemented in the future.

Function Table:
'''

import re

# Extract all image paths of all images contained in the Markdown text
def GetImagePathsinMD(MarkdownText: str) -> list:
    # Regular expression pattern to match Markdown image syntax ![alt text](image path)
    Pattern = r'!\[.*?\]\((.*?)\)'
    # Find all image paths in the Markdown text
    ImagePath = re.findall(Pattern, MarkdownText)
    
    return ImagePath
