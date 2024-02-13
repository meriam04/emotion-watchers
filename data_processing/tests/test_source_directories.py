import os
import pytest
from pathlib import Path
from data_processing.data_processing import separate_images_multiple
from data_processing.data_processing import separate_images_binary

test_files_dir = Path(__file__).parent / "test_files"

"""General Input Directory Info: There is one large dir with all datapoints inside
The datapoints are a particiapnt plus an emotion
eg: /source_dir_cropped_images/kirti_happy.file

Output Directory Info: One large dir with all emotions as dirs
eg:
/source_dir
  -/happy
  -/sad
  -/fear
  -/anger
  -/fun
  -/calm
  -/joy
the emotion dirs have all participant data files within
eg:
/happy/kirti_happy.file"""

# 1) A test for multiclass where the source directory doesn't exist 
def test_multiclass_dir_not_exist(tmp_path):

    #Printing for debugging 
    print(test_files_dir)

    #Using the source directory and creating a temporary output directory
    output_dir = tmp_path / "source_dir" 

    #Creating a non-exsistant directory, not existing or based off source
    non_existent_source_dir = tmp_path / "non_existent_dir"

    #Calling seperate_images_multiple from data_processing and checking that non-exsistant directory is not found
    #Assert a FileNotFoundError when trying to process the non-existent source directory
    try:
        separate_images_multiple([non_existent_source_dir], output_dir)
    except FileNotFoundError as e:
        assert type(e) == FileNotFoundError


# 2) Multiclass case where the source directory exsists but it doesn't contain a cropped subdirectory
def test_source_dir_no_cropped_subdir_multiclass(tmp_path):

    #Using the source directory and creating a temporary output directory
    output_dir = tmp_path / "source_dir"
    os.makedirs(output_dir)

    #Creating a temporary source directory
    source_dir = tmp_path / "existing_source"
    os.makedirs(source_dir)

    #Making a dummy file in the source directory (without "cropped" subdirectory), we don't need a real image here
    with open(source_dir / "example_image.jpg", "w"):
        pass

    #Calling seperate_images_multiple from data_processing and checking that file is not found if it does not have cropped
    with pytest.raises(FileNotFoundError):
        separate_images_multiple([source_dir], output_dir)

    #Ensuring the output directories for each emotion are not created
    emotions = ["happy", "fun", "calm", "joy", "anger", "sad", "fear"]
    for emotion in emotions:
        emotion_dir = output_dir / emotion
        assert not os.path.isdir(emotion_dir)
    
    #Making sure the source directory exsists and crop does not 
    assert 'source_dir' in os.listdir(tmp_path)
    assert 'cropped' not in os.listdir(tmp_path)


# 3) A test for binary class where one of the source directories exists and another doesn't
def test_binary_dir_not_exist(tmp_path):
    #Creating a temporary output directory for binary output
    output_dir = tmp_path / "binary_output" 
    os.makedirs(output_dir)

    #Creating a temporary source directory
    existing_source_dir = tmp_path / "existing_source"
    os.makedirs(existing_source_dir)

    #Creating a temporary source directory which is non-exsistant
    non_existent_source_dir = tmp_path / "non_existent_source"

    #Calling seperate_images_binary from data_processing with both directories (exsisting and non-exsisting)
    #If FileNotFoundError is raised it indicates that the 'non_existent_source_dir' doesn't exist
    #Assert that exception raised is FileNotFoundError
    try:
        separate_images_binary([existing_source_dir, non_existent_source_dir], output_dir)
    except FileNotFoundError as e:
        assert type(e) == FileNotFoundError



# 4) Binary case where the source directory exsists but it doesn't contain a cropped subdirectory
def test_source_dir_no_cropped_subdir_binary(tmp_path):
    #Creating a temporary output directory for binary output
    output_dir = tmp_path / "binary_output"
    os.makedirs(output_dir)

    #Creating a temporary source directory
    source_dir = tmp_path / "existing_source"
    os.makedirs(source_dir)

    #Making a dummy file in the source directory (without "cropped" subdirectory), we don't need a real image here
    with open(source_dir / "example_image.jpg", "w"):
        pass

    # Call separate_images_binary with the existing source directory
    try:
        separate_images_binary([source_dir], output_dir)
    except FileNotFoundError as e:
        assert type(e) == FileNotFoundError

    #Making sure the source directory exsists and crop does not 
    assert 'cropped' not in os.listdir(output_dir)
