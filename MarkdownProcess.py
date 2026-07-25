'''
Copyright(c) Liang Yiyan, Pekin University, 2025. All rights reserved.

This file contains some basic Markdown text processing functions,
such as rendering Markdown text into images, extracting images contained in Markdown text,
and other related functions. Of course, I have only listed those that I think are useful.
I hope that these methods will be further supplemented in the future.

Function Table:
GetImagePathsinMD(MarkdownText: str) -> list -- Extract all image paths of all images contained in the Markdown text
ClearMDFormatting(MarkdownText: str) -> str -- Clear formatting characters in Markdown text, such as *, #, etc., to get the pure text content
'''

import re

# Extract all image paths of all images contained in the Markdown text
def GetImagePathsinMD(MarkdownText: str) -> list:
    # Regular expression pattern to match Markdown image syntax ![alt text](image path)
    Pattern = r'!\[.*?\]\((.*?)\)'
    # Find all image paths in the Markdown text
    ImagePath = re.findall(Pattern, MarkdownText)
    
    return ImagePath

# Clear formatting characters in Markdown text, such as *, #, etc., to get the pure text content
def ClearMDFormatting(MarkdownText: str) -> str:
    # Remove Pictures syntax
    MarkdownText = re.sub(r'!\[.*?\]\(.*?\)', '', MarkdownText)
    # Remove titles syntax
    MarkdownText = re.sub(r'#+ ', '', MarkdownText)
    # Remove bold syntax
    MarkdownText = re.sub(r'\*\*(.*?)\*\*', r'\1', MarkdownText)
    # Remove italic syntax
    MarkdownText = re.sub(r'\*(.*?)\*', r'\1', MarkdownText)
    # Remove inline code syntax
    MarkdownText = re.sub(r'`(.*?)`', r'\1', MarkdownText)
    # Remove blockquote syntax
    MarkdownText = re.sub(r'> (.*?)\n', r'\1\n', MarkdownText)
    # Remove unordered list syntax
    MarkdownText = re.sub(r'- (.*?)\n', r'\1\n', MarkdownText)
    # Remove ordered list syntax
    MarkdownText = re.sub(r'\d+\. (.*?)\n', r'\1\n', MarkdownText)
    # Remove horizontal rule syntax
    MarkdownText = re.sub(r'---', '', MarkdownText)
    # Remove link syntax
    MarkdownText = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', MarkdownText)
    # Remove other special characters
    MarkdownText = re.sub(r'[\\*_#`>]', '', MarkdownText)

    return MarkdownText.strip()