# Model Training and Testing 

## Table of Contents
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#overview">Overview</a></li>
    <li><a href="#before-we-begin">Before We Begin</a></li>
    <li><a href="#data-flow-diagram">Data Flow Diagram</a></li>
    <li><a href="#pupillometry-model">Pupillometry Model</a></li>
    <li><a href="#facial-model">Facial Model</a></li>
    <li><a href="#fusion-model">Fusion Model</a></li>
  </ol>
</details>

## Overview
This document outlines the process of training and testing the 3 models (face, pupil, and fusion).

## Before We Begin
The collected data should have already been processed as shown in the [data processing README](https://github.com/meriam04/emotion-watchers/tree/main/data_processing/README.md)

## Data Flow Diagram
The following shows the flow for each of the models at a high level.

**Pupil Model:**
Continuous Pupil Function (.pkl) --> `pupil/train.py` --> checkpoint (model weights) + accuracy

**Face Model:**
Separated Images --> `face/train.py` --> checkpoint (model weights) + accuracy

## Pupillometry Model
The processed pupil data can be used to train and test the model.

### Training
1. Run the `emotion-watchers/models/models/pupil/train.py` script with the following parameters:
   -  `pupil_data_dir`: The directory with the pupil data (same as in [data processing README](https://github.com/meriam04/emotion-watchers/tree/main/data_processing/README.md#process-pupillometry-data))
   - `face_data_dir`: The directory containing the processed facial images (equivalent to the `output_path` from the [data processing README](https://github.com/meriam04/emotion-watchers/tree/main/data_processing/README.md#process-facial-videos))
   
   Here is an example on how to run it from `emotion-watchers/models/models/pupil`:
    ```shell
    python3 train.py pupil_data_dir facial_data_dir
    ```
2. As the model trains, there should be a progress bar visible with the accuracy of each epoch. Select the epoch with the highest validation accuracy as the 'best epoch'. 

3. Set the `CHECKPOINT_PATH` variable in `emotion-watchers/models/models/pupil/test.py` to the checkpoint of the 'best epoch' chosen above. 
   ```python
   CHECKPOINT_PATH = Path(__file__).parent / "checkpoints/binary-006.ckpt"
   ```
4. (Optional) Delete the other checkpoints and keep the checkpoints directory as:
  ```shell
    /checkpoints
        binary-006.ckpt.data-00000-of-00001
        binary-006.ckpt.index
        checkpoint
  ```

### Testing

1. Validate that there is a model checkpoint saved in the `emotion-watchers/models/models/pupil/checkpoints` directory. 
   
2. Run the `emotion-watchers/models/models/pupil/test.py` script with the same parameters as `train.py`:
   - `pupil_data_dir`: The directory with the pupil data (same as in [data processing README](https://github.com/meriam04/emotion-watchers/tree/main/data_processing/README.md#process-pupillometry-data))
   - `face_data_dir`: The directory containing the processed facial images (equivalent to the `output_path` from the [data processing README](https://github.com/meriam04/emotion-watchers/tree/main/data_processing/README.md#process-facial-videos))
   
   Here is an example on how to run it from `emotion-watchers/models/models/pupil`:
    ```shell
    python3 test.py pupil_data_dir facial_data_dir
    ```
3. View the accuracy on the test data in the terminal.

## Facial Model
The cropped and classified facial images can be used to train and test the facial model.

### Training
1. Run the `emotion-watchers/models/models/face/train.py` script with the following parameter:
   - `face_data_dir`: The directory containing the processed facial images (equivalent to the `output_path` from the [data processing README](https://github.com/meriam04/emotion-watchers/tree/main/data_processing/README.md#process-facial-videos))
   
   Here is an example on how to run it from `emotion-watchers/models/models/face`:
    ```shell
    python3 train.py facial_data_dir
    ```
2. As the model trains, there should be a progress bar visible with the accuracy of each epoch. Select the epoch with the highest validation accuracy as the 'best epoch'. 

3. Set the `CHECKPOINT_PATH` variable in `emotion-watchers/models/models/face/test.py` to the checkpoint of the 'best epoch' chosen above. 
   ```python
   CHECKPOINT_PATH = Path(__file__).parent / "checkpoints/binary-010.ckpt"
   ```
4. (Optional) Delete the other checkpoints and keep the checkpoints directory as:
  ```shell
    /checkpoints
        binary-010.ckpt.data-00000-of-00001
        binary-010.ckpt.index
        checkpoint
  ```
   
### Testing

1. Validate that there is a model checkpoint saved in the `emotion-watchers/models/models/face/checkpoints` directory. 
   
2. Run the `emotion-watchers/models/models/face/test.py` script with the same parameters as `train.py`:
   - `face_data_dir`: The directory containing the processed facial images (equivalent to the `output_path` from the [data processing README](https://github.com/meriam04/emotion-watchers/tree/main/data_processing/README.md#process-facial-videos))
   
   Here is an example on how to run it from `emotion-watchers/models/models/face`:
    ```shell
    python3 test.py facial_data_dir
    ```
3. View the accuracy on the test data in the terminal.

## Fusion Model
The fusion model is an ensemble (average) of the pupillometry and facial models that were previously trained. As a result, it does not require training and can only be tested.

### Testing

1. Validate that both the `pupil/test.py` and `face/test.py` files contain the correct `CHECKPOINT_PATH` variables with the best models, as described in the (Pupil Model)[#pupil-model] and (Facial Model)["facial-model] sections above.

2. Run the `fusion.py` script with the following parameters:
   - `pupil_data_dir`: The directory with the pupil data (same as in [data processing README](https://github.com/meriam04/emotion-watchers/tree/main/data_processing/README.md#process-pupillometry-data))
   - `test_face_data_dir`: The directory containing the **test** subset of the processed facial images (equivalent to the `output_path` from the [data processing README](https://github.com/meriam04/emotion-watchers/tree/main/data_processing/README.md#process-facial-videos))
  
  Here is an example on how to call it from the `emotion-watchers/models/models` directory:
  ```shell
  python3 fusion.py pupil_data_dir face_data_dir/test
  ```

3. See the resulting test accuracy in the terminal, along with a confusion matrix in `emotion-watchers/models/models/confusion_matrix.png`.

#### Testing Individual Accuracies
In order to notice the bias of the model, there is an option to output a test accuracy for each participant. In order to do so, use the same steps as above EXCEPT change the `test_face_data_dir` to the directory for the participant.

Here is an example on how to call it from the `emotion-watchers/models/models` directory for the `cs` participant:
```shell
python3 fusion.py pupil_data_dir face_data_dir/cs
```
