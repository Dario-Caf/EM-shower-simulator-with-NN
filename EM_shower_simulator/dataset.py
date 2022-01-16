"""Subroutines for the dataset organization and shower plot."""

import os
import logging

import numpy as np
import uproot as up
import matplotlib.pyplot as plt
from tensorflow.data import Dataset

#-------------------------------------------------------------------------------

# Creation of the default dataset path
# "data_MVA_normalized.root"
data_path_1 = os.path.join("dataset","filtered_data","data_MVA_24pixel_parte1.root")
DPATH_1 = os.path.join("..", data_path_1)

data_path_2 = os.path.join("dataset","filtered_data","data_MVA_24pixel_parte2.root")
DPATH_2 = os.path.join("..", data_path_2)
# Configuration of the dataset structure
ENERGY_NORM = 6.7404
ENERGY_SCALE = 1000000
GEOMETRY = (12, 25, 25, 1) # (12, 12, 12, 1)
BUFFER_SIZE = 10400

# Define logger
logger = logging.getLogger("DataLogger")

#-------------------------------------------------------------------------------

def data_pull(path_1, path_2, verbose=False):
    """Organize and reshape the dataset for the cGan training.
    Inputs:
    path = path to a .root file containing the dataset.

    Description:
    Take in input a path to the dataset and return an iterator over events that
    can be used to train the cGAN using the method train.
    """
    if verbose :
        logger.setLevel(logging.DEBUG)
        logger.info('Logging level set on DEBUG.')
    else:
        logger.setLevel(logging.WARNING)
        logger.info('Logging level set on WARNING.')

    logger.info("Loading the training dataset.")
    try:
       with up.open(path_1) as file_1:
           branches_1 = file_1["h"].arrays()
    except Exception as e:
       print("Error: Invalid path or corrupted file.")
       raise e

    try:
       with up.open(path_2) as file_2:
           branches_2 = file_2["h"].arrays()
    except Exception as e:
       print("Error: Invalid path or corrupted file.")
       raise e

    train_images_1 = np.array(branches_1["shower"]).astype("float32")
    # Images in log10 scale, empty pixels are set to -5,
    # maximum of pixel is 2.4E5 keV => maximum<7 in log scale
    N_EVENT = train_images_1.shape[0]
    # Normalize the images to [-1, 1] and reshape
    train_images_1 = np.reshape(train_images_1, (N_EVENT, *GEOMETRY))

    en_labels_1 = np.array(branches_1["en_in"]).astype("float32") / ENERGY_SCALE
    en_labels_1 = np.transpose(en_labels_1)
    assert N_EVENT == en_labels_1.shape[0], "Dataset energy labels compromised!"
    en_labels_1 = np.reshape(en_labels_1, (N_EVENT, 1))

    # Particle labels are -1, 0, 1 ==> 0, 1, 2 for embedding layer
    pid_labels_1 = np.array(branches_1["primary"]) + 1
    pid_labels_1 = np.transpose(pid_labels_1)
    assert N_EVENT == pid_labels_1.shape[0], "Dataset PID labels compromised!"
    pid_labels_1 = np.reshape(pid_labels_1, (N_EVENT, 1))

    train_images_2 = np.array(branches_2["shower"]).astype("float32")
    # Images in log10 scale, empty pixels are set to -5,
    # maximum of pixel is 2.4E5 keV => maximum<7 in log scale
    N_EVENT = train_images_2.shape[0]
    # Normalize the images to [-1, 1] and reshape
    train_images_2 = np.reshape(train_images_2, (N_EVENT, *GEOMETRY))

    en_labels_2 = np.array(branches_2["en_in"]).astype("float32") / ENERGY_SCALE
    en_labels_2 = np.transpose(en_labels_2)
    assert N_EVENT == en_labels_2.shape[0], "Dataset energy labels compromised!"
    en_labels_2 = np.reshape(en_labels_2, (N_EVENT, 1))

    # Particle labels are -1, 0, 1 ==> 0, 1, 2 for embedding layer
    pid_labels_2 = np.array(branches_2["primary"]) + 1
    pid_labels_2 = np.transpose(pid_labels_2)
    assert N_EVENT == pid_labels_2.shape[0], "Dataset PID labels compromised!"
    pid_labels_2 = np.reshape(pid_labels_2, (N_EVENT, 1))


    train_images = np.concatenate([train_images_1, train_images_2], axis=0)
    en_labels = np.concatenate([en_labels_1, en_labels_2], axis=0)
    pid_labels = np.concatenate([pid_labels_1,pid_labels_2],axis=0)

    dataset = Dataset.from_tensor_slices((train_images, en_labels, pid_labels))
    dataset = dataset.shuffle(BUFFER_SIZE)
    return dataset

def debug_data_pull(path_1, path_2, num_examples=1, verbose=False):
    """Import data images from the dataset and test shapes.
    Inputs:
    path = path to a .root file containing the dataset;
    num_examples = number of random shower to plot.

    Description:
    Take in input a path to the dataset and return num_examples of events from
    the dataset that can be plotted with debug_shower.
    """
    if verbose :
        logger.setLevel(logging.DEBUG)
        logger.info('Logging level set on DEBUG.')
    else:
        logger.setLevel(logging.WARNING)
        logger.info('Logging level set on WARNING.')

    logger.info("Start debugging the dataset loading subroutines.")
    try:
       with up.open(path_1) as file_1:
           branches_1 = file_1["h"].arrays()
    except Exception as e:
       print("Error: Invalid path or corrupted file.")
       raise e

    try:
       with up.open(path_2) as file_2:
           branches_2 = file_2["h"].arrays()
    except Exception as e:
       print("Error: Invalid path or corrupted file.")
       raise e

    train_images_1 = np.array(branches_1["shower"]).astype("float32")
    # Images in log10 scale, empty pixels are set to -5,
    # maximum of pixel is 2.4E5 keV => maximum<7 in log scale
    N_EVENT = train_images_1.shape[0]
    # Normalize the images to [-1, 1] and reshape
    train_images_1 = np.reshape(train_images_1, (N_EVENT, *GEOMETRY))

    en_labels_1 = np.array(branches_1["en_in"]).astype("float32") / ENERGY_SCALE
    en_labels_1 = np.transpose(en_labels_1)
    assert N_EVENT == en_labels_1.shape[0], "Dataset energy labels compromised!"
    en_labels_1 = np.reshape(en_labels_1, (N_EVENT, 1))

    # Particle labels are -1, 0, 1 ==> 0, 1, 2 for embedding layer
    pid_labels_1 = np.array(branches_1["primary"]) + 1
    pid_labels_1 = np.transpose(pid_labels_1)
    assert N_EVENT == pid_labels_1.shape[0], "Dataset PID labels compromised!"
    pid_labels_1 = np.reshape(pid_labels_1, (N_EVENT, 1))

    train_images_2 = np.array(branches_2["shower"]).astype("float32")
    # Images in log10 scale, empty pixels are set to -5,
    # maximum of pixel is 2.4E5 keV => maximum<7 in log scale
    N_EVENT = train_images_2.shape[0]
    # Normalize the images to [-1, 1] and reshape
    train_images_2 = np.reshape(train_images_2, (N_EVENT, *GEOMETRY))

    en_labels_2 = np.array(branches_2["en_in"]).astype("float32") / ENERGY_SCALE
    en_labels_2 = np.transpose(en_labels_2)
    assert N_EVENT == en_labels_2.shape[0], "Dataset energy labels compromised!"
    en_labels_2 = np.reshape(en_labels_2, (N_EVENT, 1))

    # Particle labels are -1, 0, 1 ==> 0, 1, 2 for embedding layer
    pid_labels_2 = np.array(branches_2["primary"]) + 1
    pid_labels_2 = np.transpose(pid_labels_2)
    assert N_EVENT == pid_labels_2.shape[0], "Dataset PID labels compromised!"
    pid_labels_2 = np.reshape(pid_labels_2, (N_EVENT, 1))


    train_images = np.concatenate([train_images_1, train_images_2], axis=0)
    en_labels = np.concatenate([en_labels_1, en_labels_2], axis=0)
    pid_labels = np.concatenate([pid_labels_1,pid_labels_2],axis=0)

    train_images = train_images[0:num_examples]
    en_labels = en_labels[0:num_examples]
    pid_labels = pid_labels[0:num_examples]

    logger.info("Debug of the loading subroutines finished.")
    return [train_images, en_labels, pid_labels]

def debug_shower(data_images, verbose=False):
    """Plot all showers from data_images and return the figure.
    Inputs:
    data_images = vector of images with shape equal to GEOMETRY.
    """
    if verbose :
        logger.setLevel(logging.DEBUG)
        logger.info('Logging level set on DEBUG.')
    else:
        logger.setLevel(logging.WARNING)
        logger.info('Logging level set on WARNING.')

    logger.info("Start debug data_images features.")
    logger.info(f"Shape of data_images: {data_images.shape}")
    k=0
    fig = plt.figure("Generated showers", figsize=(20,10))
    num_examples = data_images.shape[0]
    for i in range(num_examples):
       for j in range(GEOMETRY[0]):
          k=k+1
          plt.subplot(num_examples, GEOMETRY[0], k)
          plt.imshow(data_images[i,j,:,:,0]) #, cmap="gray")
          plt.axis("off")
    plt.show()
    logger.info("Debug of data_images features finished.")
    return fig
