#!/usr/bin/env python3

from pathlib import Path
import sys
import os
import shutil
from typing import List

from crop_and_resize_images import crop_and_resize_images
from utils import Point, Region, Resolution
from video_to_images import extract_frames

#If we are making a UI, return these values for TOP_LEFT and BOTTOM_RIGHT 
RATE = 1
TOP_LEFT = Point(100, 100)
BOTTOM_RIGHT = Point(324, 324)
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
def separate_images_binary(source_folder, positive_folder, negative_folder, keyword):
    os.makedirs(positive_folder, exist_ok=True)
    os.makedirs(negative_folder, exist_ok=True)

    for filename in os.listdir(source_folder):
        source_path = os.path.join(source_folder, filename)

        # Check if the keyword is present in the filename
        if keyword in filename:
            destination_path = os.path.join(positive_folder, filename)
        else:
            destination_path = os.path.join(negative_folder, filename)

        # Move the file to the appropriate folder
        shutil.move(source_path, destination_path)
        print(f"Moved {filename} to {destination_path}")

# Example usage:
#source_folder = "/data"
#positive_folder = "/data/baseline/positive"
#negative_folder = "/data/baseline/negative"
#keyword = "positive"

#separate_images_binary(source_folder, positive_folder, negative_folder, keyword)

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