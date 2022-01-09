"""Subroutines for the dataset organization, debug and plot."""

import os
import logging
from pathlib import Path

import numpy as np
import uproot as up
import matplotlib.pyplot as plt

#-------------------------------------------------------------------------------
"""Constant parameters of configuration and definition of global objects."""

# Creation of the default dataset path
data_path = os.path.join("dataset","filtered_data","data_MVA.root")
DPATH = os.path.join("..", data_path)

# Configuration of the dataset structure
ENERGY_NORM = 6.
ENERGY_SCALE = 1000000
GEOMETRY = (12, 12, 12, 1)

# Define logger and handler
ch = logging.StreamHandler()
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger = logging.getLogger("DataSetLogger")
logger.addHandler(ch)

#-------------------------------------------------------------------------------
"""Subroutines for the dataset organization and shower plot."""

def data_pull(path=DPATH, verbose=False):
    """Organize and reshape the dataset for the cGan training.
    Take in input a path to the dataset and return an iterator over batchs that
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
       with up.open(Path(path).resolve()) as file:
           branches = file["h"].arrays()
    except Exception as e:
       print("Error: Invalid path or corrupted file.")
       raise e

    train_images = np.array(branches["shower"]).astype("float32")
    # Images in log10 scale, empty pixels are set to -5,
    # maximum of pixel is 2.4E5 keV => maximum<7 in log scale
    N_EVENT = train_images.shape[0]
    # Normalize the images to [-1, 1] and reshape
    train_images = (train_images - 1.) / ENERGY_NORM
    train_images = np.reshape(train_images, (N_EVENT, *GEOMETRY))

    en_labels = np.array(branches["en_in"]).astype("float32") / ENERGY_SCALE
    en_labels = np.transpose(en_labels)
    assert N_EVENT == en_labels.shape[0], "Dataset energy labels compromised!"
    en_labels = np.reshape(en_labels, (N_EVENT, 1))

    # Particle labels are -1, 0, 1 ==> 0, 1, 2 for embedding layer
    pid_labels = np.array(branches["primary"]) + 1
    pid_labels = np.transpose(pid_labels)
    assert N_EVENT == pid_labels.shape[0], "Dataset PID labels compromised!"
    pid_labels = np.reshape(pid_labels, (N_EVENT, 1))

    return (train_images, en_labels, pid_labels)

def debug_data_pull(path=DPATH, num_examples=1, verbose=False):
    """Import data images from the dataset and test shapes.
    Take in input a path to the dataset and return train_images from the dataset
    that can be plotted with debug_shower.
    """
    if verbose :
        logger.setLevel(logging.DEBUG)
        logger.info('Logging level set on DEBUG.')
    else:
        logger.setLevel(logging.WARNING)
        logger.info('Logging level set on WARNING.')

    logger.info("Start debugging the dataset loading subroutines.")
    try:
       with up.open(Path(path).resolve()) as file:
           branches = file["h"].arrays()
    except Exception as e:
       print("Error: Invalid path or corrupted file.")
       raise e

    train_images = np.array(branches["shower"]).astype("float32")
    # Images in log10 scale, zeros like pixel are set to -5,
    # maximum of pixel is 2.4E5 keV => maximum<7 in log scale
    N_EVENT = train_images.shape[0]
    # Normalize the images to [-1, 1] and reshape
    train_images = (train_images - 1.) / ENERGY_NORM
    train_images = np.reshape(train_images, (N_EVENT, *GEOMETRY))
    train_images = train_images[0:num_examples]

    en_labels = np.array(branches["en_in"]).astype("float32") / ENERGY_SCALE
    en_labels = np.transpose(en_labels)
    assert N_EVENT == en_labels.shape[0], "Dataset energy labels compromised!"
    en_labels = np.reshape(en_labels, (N_EVENT, 1))
    en_labels = en_labels[0:num_examples]

    # Particle labels are -1, 0, 1 ==> 0, 1, 2 for embedding layer
    pid_labels = np.array(branches["primary"]) + 1
    pid_labels = np.transpose(pid_labels)
    assert N_EVENT == pid_labels.shape[0], "Dataset PID labels compromised!"
    pid_labels = np.reshape(pid_labels, (N_EVENT, 1))
    pid_labels = pid_labels[0:num_examples]

    logger.info("Debug of the loading subroutines finished.")
    return [train_images, en_labels, pid_labels]

def debug_shower(data_images, verbose=False):
    """Plot all showers from data_images and return the figure."""
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