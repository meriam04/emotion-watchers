#!/usr/bin/env python3

from pathlib import Path
import sys
import os
import shutil
from typing import List
import logging
logging.basicConfig(level=logging.DEBUG)

from .crop_and_resize_images import crop_and_resize_images
from .utils import Point, Region, Resolution
from .video_to_images import extract_frames

#If we are making a UI, return these values for TOP_LEFT and BOTTOM_RIGHT 
RATE = 1
TOP_LEFT = Point(430, 80)
BOTTOM_RIGHT = Point(930, 580)
RESOLUTION = Resolution(224, 224)
#Add FILE_LIST as global variable 

def data_processing(video_path: Path, output_path: Path) -> List[Path]:
    image_paths = extract_frames(video_path, RATE, output_path)
    return crop_and_resize_images(image_paths, Region(TOP_LEFT, BOTTOM_RIGHT), RESOLUTION)

if __name__ == "__main__":
    data_processing(Path(sys.argv[1]), Path(sys.argv[2]))

#Adding a function to move the images to the corresponding directory 
    #Data/baseline/emotion 
    #seperate from the overall /baseline folder 
    #All negative emotions and positive emotions have to be mapped

############## BINARY SEPARATOR ############# 
def separate_images_binary(source_folder, positive_folder, negative_folder, keyword):
    os.makedirs(positive_folder, exist_ok=True)
    os.makedirs(negative_folder, exist_ok=True)

    positive_keywords = ["happy", "fun", "calm", "joy"]
    negative_keywords = ["anger", "sad", "fear"]

    print("Source folder:", source_folder)
    for folder_name in os.listdir(source_folder):
        logging.debug("Subfolder:", folder_name)
        source_path = os.path.join(source_folder, folder_name)

        # Check if the folder name contains "cropped"
        if os.path.isdir(source_path) and "cropped" in os.listdir(source_path):
            cropped_folder_path = os.path.join(source_path, "cropped")

            print("Cropped folder path:", cropped_folder_path)
            # Check if the folder name contains positive or negative keywords
            if any(keyword in folder_name for keyword in positive_keywords):
                destination_path = positive_folder
                logging.debug("Keyword matched: Positive")
            elif any(keyword in folder_name for keyword in negative_keywords):
                destination_path = negative_folder
                logging.debug("Keyword matched: Negative")
            else:
                logging.debug(f"Folder {folder_name} does not match positive or negative criteria, skipping.")
                continue

            # Move all files from the cropped folder to the appropriate destination folder
            files = os.listdir(cropped_folder_path)
            for filename in files:
                source_file_path = os.path.join(cropped_folder_path, filename)
                destination_file_path = os.path.join(destination_path, filename)
                shutil.move(source_file_path, destination_file_path)
                logging.debug(f"Moved {filename} to {destination_path}")

        else:
            logging.debug(f"Folder {folder_name} does not contain a 'cropped' directory, skipping.")

# def separate_images_binary(source_folder, positive_folder, negative_folder, keyword):
#     os.makedirs(positive_folder, exist_ok=True)
#     os.makedirs(negative_folder, exist_ok=True)

#     positive_keywords = ["happy", "fun", "calm", "joy"]
#     negative_keywords = ["anger", "sad", "fear"]

#     for folder_name in os.listdir(source_folder):
#         source_path = os.path.join(source_folder, folder_name)

#         #Checking if cropped directory exists 
#         for folder_name in os.listdir(source_folder):
#             source_path = os.path.join(source_folder, folder_name)
#             cropped_folder_path = os.path.join(source_path, "cropped")

#         if os.path.exists(cropped_folder_path) and os.path.isdir(cropped_folder_path):
#             # Check if the folder name contains positive or negative keywords
#             if any(keyword in folder_name for keyword in positive_keywords):
#                 destination_path = os.path.join(positive_folder, folder_name)
#             elif any(keyword in folder_name for keyword in negative_keywords):
#                 destination_path = os.path.join(negative_folder, folder_name)
#             else:
#                 print(f"Folder {folder_name} does not match positive or negative criteria, skipping.")
#                 continue

#             # Move all files from the source folder to the appropriate destination folder
#             files = os.listdir(source_path)
#             for filename in files:
#                 source_file_path = os.path.join(source_path, filename)
#                 destination_file_path = os.path.join(destination_path, filename)
#                 shutil.move(source_file_path, destination_file_path)
#                 print(f"Moved {filename} to {destination_path}")

#         else:
#             print(f"Folder {folder_name} does not contain a 'cropped' directory, skipping.")

# # Example usage:
# #source_folder = "/data"
# #positive_folder = "/data/baseline/positive"
# #negative_folder = "/data/baseline/negative"
# #keyword = "positive"

# #separate_images_binary(source_folder, positive_folder, negative_folder, keyword)
        
######### MULTICLASS SEPERATOR ###############
def separate_images_multiple(source_folder, output_folders, keywords):
    for folder in output_folders:
        os.makedirs(folder, exist_ok=True)

    for folder_name in os.listdir(source_folder):
        source_path = os.path.join(source_folder, folder_name)

        #check if there is a cropped folder, if not then throw an error 
        #if there is a cropped, copy all images from cropped into correct emotion folder 
        cropped_folder_path = os.path.join(source_path, "cropped")
        if os.path.exists(cropped_folder_path) and os.path.isdir(cropped_folder_path):

        # Check if the foldername contains any of the keywords
            for keyword, destination_folder in zip(keywords, output_folders):
                if keyword in folder_name:
                    files = os.listdir(source_path)
                    for filename in files:
                        source_file_path = os.path.join(source_path, filename)
                        destination_path = os.path.join(destination_folder, filename)
                        # Move the file to the appropriate folder
                        shutil.move(source_file_path, destination_path)
                        print(f"Moved {filename} to {destination_folder}")
                    break  # Move to the next file

        else: 
            print(f"Folder {folder_name} does not contain a 'cropped' directory, skipping.")

#This is where the source folder is 
#/data/1_cs_joy/cropped 
            #So check if folder name has the keyword 
            
# source_folder = "/data"
# output_folders = [
#     "/data/baseline/anger",
#     "/data/baseline/sad",
#     "/data/baseline/fear",
#     "/data/baseline/happy",
#     "/data/baseline/fun",
#     "/data/baseline/calm"
#     "/data/baseline/joy"            
# ]
# keywords = ["anger", "sad", "fear", "happy", "fun", "calm", "joy"]

# separate_images_multiple(source_folder, output_folders, keywords)