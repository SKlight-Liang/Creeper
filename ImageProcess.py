'''
Copyright(c) Liang Yiyan, Pekin University, 2026. All rights reserved.

This program mainly focus on the process of images.
For example, sometimes we may want to know there are how many similar images in a folder.
Or sometimes we just want to add a white border resulting in better OCR results. 
So I gathered and encapsulated some common image processing functions here.
Hope these functions can help you in your work and give you some inspiration.

Function Table:
LoadCLIPModel(ModelName: str = "ViT-B/32") -> (Model, Preprocess)
-- Load CLIP model for image embeddings
Embeddings(ImagePaths: list, Model, Preprocess, BatchSize: int = 32) -> np.ndarray
-- Extract image embeddings using CLIP
FoldersCompare(FolderA: str, FolderB: str, Threshold: float = 0.9, TopK: int = 5, SavePath: str = None) -> list
-- Compare the images in two folders and find out the similar ones
AddWhiteBorder(ImagePath: str, BorderSize: int, SavePath: str = None) -> Image.Image
-- Add white border around the image
'''

import os

# I meet an environment error when initializing libomp.dll
# The error is related to the OpenMP library. The information is as follows:
# OMP: Error #15: Initializing libomp.dll, but found libiomp5md.dll already initialized.
# If you meet this problem as well, you can try to add the following line to avoid the error.
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import json
import tqdm

import clip
import torch
import faiss
# Determine whether to use GPU or CPU
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

import numpy as np

from PIL import Image
from PIL import ImageOps

from FileProcess import LogMessage
from FileProcess import GetFileNamesinDir

# Load CLIP model for image embeddings
def LoadCLIPModel(ModelName: str = "ViT-B/32"):
    Model, Preprocess = clip.load(ModelName, device=DEVICE)
    # Set the model to evaluation mode
    Model.eval()

    return Model, Preprocess

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

# Extract image embeddings using CLIP
@torch.no_grad()
def Embeddings(ImagePaths: list, Model, Preprocess, BatchSize: int = 32):
    EmbeddingsList = []

    for i in tqdm.tqdm(range(0, len(ImagePaths), BatchSize), desc="Extract embeddings"):
        Batch = ImagePaths[i:i + BatchSize]

        Images = []
        for Pic in Batch:
            # Preprocess each image
            Img = Image.open(Pic).convert("RGB")
            # Append the preprocessed image to the list
            Images.append(Preprocess(Img))

        # Stack images into a batch tensor
        ImageTensor = torch.stack(Images).to(DEVICE)
        # Get the image embeddings from the model
        Feats = Model.encode_image(ImageTensor)
        # Normalize the embeddings
        Feats = Feats / Feats.norm(dim=1,keepdim=True)
        # Append the embeddings to the list
        EmbeddingsList.append(Feats.cpu().numpy())
    
    return np.vstack(EmbeddingsList).astype("float32")

# This program is used to compare the images in two given folders.
# Simply speaking, assume we have two folders: Folder A and Folder B.
# We want to find out which images in Folder A are similar to those in Folder B.
# Here we will use CLIP image embeddings to achieve this goal.
# So I recommend that your computer should have a decent GPU to speed up the process.
# Otherwise, it may take a long time to complete the comparison.

# NOTE: The duplication detection strategy adopted in this program is semantic analysis 
# based on CLIP image embeddings, which is different from traditional pixel-based methods.
# Therefore, it cannot be guaranteed that two images deemed similar by the program are almost identical.
# However, this method can easily handle the situation when similar images have different resolutions.

# Variables:
# FolderA: The path of folder A
# FolderB: The path of folder B
# Threshold: The similarity threshold for determining whether two images are similar
# TopK: The number of top similar images to retrieve for each image in folder B
# SavePath: The path to save the comparison results in json format. If None, the results will not be saved to a file.
def FoldersCompare(FolderA: str = None, FolderB: str = None, 
                   Threshold: float = 0.9, TopK: int = 5, SavePath: str = None) -> list:
    # Check whether the folders exist
    if not os.path.exists(FolderA) or not os.path.exists(FolderB):
        LogMessage(f"One or both folders do not exist: {FolderA}, {FolderB}", Type="ERROR")
        return []
    
    # Obtain all image paths in folder A & folder B
    ImageNamesA = GetFileNamesinDir(FolderA)
    ImageNamesA = [name for name in ImageNamesA 
                   if name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'))]
    ImagePathsA = [os.path.join(FolderA, Name) for Name in ImageNamesA]
    ImageNamesB = GetFileNamesinDir(FolderB)
    ImageNamesB = [name for name in ImageNamesB 
                   if name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'))]   
    ImagePathsB = [os.path.join(FolderB, Name) for Name in ImageNamesB]

    if not ImagePathsA or not ImagePathsB:
        LogMessage("One or both folders contain no valid images.", Type="ERROR")
        return []

    # Load CLIP model and preprocess function
    Model, PreProcess = LoadCLIPModel()
    # Extract embeddings for images in both folders
    EmbeddingsA = Embeddings(ImagePathsA, Model, PreProcess)
    EmbeddingsB = Embeddings(ImagePathsB, Model, PreProcess)
    # Get the embedding dimension
    Dim = EmbeddingsA.shape[1]

    # Build FAISS index for images in folder A
    Index = faiss.IndexFlatIP(Dim)
    Index.add(EmbeddingsA)

    # Search for similar images in folder A for each image in folder B
    Score, Indices = Index.search(EmbeddingsB, TopK)

    Duplicates = []

    for i in tqdm.tqdm(range(len(ImagePathsB)), desc="Comparing images"):
        for j in range(TopK):
            if ImagePathsB[i] != ImagePathsA[Indices[i][j]] and Score[i][j] >= Threshold:
                Duplicates.append({
                    "ImageInFolderB": ImagePathsB[i],
                    "ImageInFolderA": ImagePathsA[Indices[i][j]],
                    "SimilarityScore": float(Score[i][j])
                })

    if SavePath:
        with open(SavePath, "w", encoding="utf-8") as outfile:
            json.dump(Duplicates, outfile, indent=4, ensure_ascii=False)
        LogMessage(f"Comparison results saved to: {SavePath}", Type="INFO")

    return Duplicates

