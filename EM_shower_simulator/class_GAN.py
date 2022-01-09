"""Conditional GAN structure and subroutines."""

# Examples of conditional GANs from which we built our neural network :
# https://machinelearningmastery.com/how-to-develop-a-conditional-generative-adversarial-network-from-scratch/
# https://keras.io/examples/generative/conditional_gan/

import os
import time
import logging
from pathlib import Path

import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from matplotlib.image import imread
from tensorflow.keras.utils import plot_model
from tensorflow.keras.metrics import Mean
from tensorflow.keras.optimizers import Adam

from IPython import display

#-------------------------------------------------------------------------------
"""Constant parameters of configuration and definition of global objects."""

# Configuration of the cGAN structure
N_CLASSES_PID = 3
N_CLASSES_EN = 30 + 1
EPOCHS = 200
BATCH_SIZE = 256         #complicate relation with minibatch!
BUFFER_SIZE = 10400
L_RATE = 3e-4
NOISE_DIM = 1000

# Create a random seed, to be used during the evaluation of the cGAN.
tf.random.set_seed(42)
num_examples = 6                 #multiple or minor of minibatch
test_noise = [tf.random.normal([num_examples, NOISE_DIM]),
              tf.random.uniform([num_examples, 1], minval= 0.,
                                maxval=N_CLASSES_EN),
              tf.random.uniform([num_examples, 1], minval= 0.,
                                maxval=N_CLASSES_PID)]

# Define logger and handler
ch = logging.StreamHandler()
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger = logging.getLogger("CGANLogger")
logger.addHandler(ch)

#-------------------------------------------------------------------------------

def generate_and_save_images(model, noise, epoch=0):
    """Create images generated by the model at each epoch from the input noise.
    If verbose=True it only shows the output images of the model in debug model.
    If verbose=False it also saves the output images in 'training_results/'.
    Arguments:
    -) model: model (cGAN) to be evaluated;
    -) noise: constant input to the model in order to evaluate performances;
    -) epoch: epoch whose predictions are to be saved.
    """
    # 1 - Generate images
    predictions = model(noise, training=False)
    logger.info(f"Shape of generated images: {predictions.shape}")

    # 2 - Plot the generated images
    k=0
    fig = plt.figure("Generated showers", figsize=(20,10))
    num_examples = predictions.shape[0]
    for i in range(num_examples):
       for j in range(predictions.shape[1]):
          k=k+1
          plt.subplot(num_examples, predictions.shape[1], k)
          plt.imshow(predictions[i,j,:,:,0]) #, cmap="gray")
          plt.axis("off")
    plt.show()

    # 3 - Save the generated images
    save_path = Path('training_results').resolve()
    file_name = f"image_at_epoch_{epoch}.png"
    if not os.path.isdir(save_path):
       os.makedirs(save_path)
    fig.savefig(os.path.join(save_path, file_name))


def generator_loss(fake_output):
    """Definie generator loss:
    successes on fake samples from the generator valued as true samples by
    the discriminator fake_output.
    """
    cross_entropy = tf.keras.losses.BinaryCrossentropy()
    return cross_entropy(tf.ones_like(fake_output), fake_output)

def discriminator_loss(real_output, fake_output):
    """Define discriminator loss:
    fails on fake samples (from generator) and successes on real samples.
    """
    cross_entropy = tf.keras.losses.BinaryCrossentropy()
    real_loss = cross_entropy(tf.ones_like(real_output), real_output)
    fake_loss = cross_entropy(tf.zeros_like(fake_output), fake_output)
    total_loss = real_loss + fake_loss
    return total_loss

#-------------------------------------------------------------------------------

class ConditionalGAN(tf.keras.Model):
    """Class for a conditional GAN.
    It inherits keras.Model properties and functions.
    """
    def __init__(self, discrim, gener, discrim_optim=Adam(L_RATE), gener_optim=Adam(L_RATE)):
        """Constructor.
        Inputs:
        discrim = discriminator network;
        gener = generator network;
        discrim_optim = discriminator optimizer;
        gener_optim = generator optimizer;
        """
        super(ConditionalGAN, self).__init__()
        self.discriminator = discrim
        self.generator = gener
        self.discriminator_optimizer = discrim_optim
        self.generator_optimizer = gener_optim
        self.gen_loss_tracker = Mean(name="generator_loss")
        self.discr_loss_tracker = Mean(name="discriminator_loss")

    @property
    def metrics(self):
        """Metrics of the network."""
        return [self.gen_loss_tracker, self.discr_loss_tracker]

    def compile(self):
        """Compile method for the network."""
        super(ConditionalGAN, self).compile(optimizer = 'adam')

    def summary(self):
        """Summary method for both the generator and discriminator."""
        print("\n\n Conditional GAN model summary:\n")
        self.generator.summary()
        print("\n")
        self.discriminator.summary()

    def plot_model(self):
        """Plot and saves the current cGAN model"""
        save_path = Path('model_plot').resolve()
        if not os.path.isdir(save_path):
           os.makedirs(save_path)

        fig = plt.figure("Model scheme", figsize=(20,10))
        plt.subplot(1, 2, 1)
        plt.title("Generator")
        file_name = "cgan-generator.png"
        path = os.path.join(save_path, file_name)
        plot_model(self.generator, to_file=path, show_shapes=True)
        plt.imshow(imread(path))
        plt.axis("off")
        plt.subplot(1, 2, 2)
        plt.title("Discriminator")
        file_name = "cgan-discriminator.png"
        path = os.path.join(save_path, file_name)
        plot_model(self.discriminator, to_file=path, show_shapes=True)
        plt.imshow(imread(path))
        plt.axis("off")
        plt.show()

        file_name = "cgan-scheme.png"
        path = os.path.join(save_path, file_name)
        fig.savefig(os.path.join(save_path, file_name))

    # tf.function annotation causes the function
    # to be "compiled" as part of the training

    def fit(self, dataset, epochs=EPOCHS, batch=BATCH_SIZE, buffer=BUFFER_SIZE):
        """Overwrite fit std method."""
        # Split the dataset in Buffer and batch
        dataset = tf.data.Dataset.from_tensor_slices(dataset)
        dataset = dataset.shuffle(buffer)
        dataset = dataset.batch(batch, drop_remainder=True)
        super(ConditionalGAN, self).fit(dataset, epochs=epochs)

    def train_step(self, dataset):
        """Train step of the cGAN.
        Input: dataset = combined images vector and labels upon which the network trained.
        Description:
        1 - Create a random noise to feed it into the model for the images generation ;
        2 - Generate images and calculate loss values using real images and labels ;
        3 - Calculate gradients using loss values and model variables;
        4 - Process Gradients and Run the Optimizer ;
        """
        real_images, real_en_labels, real_pid_labels = dataset
        #dummy_labels = real_labels[:, :, None, None, None]
        #dummy_labels = tf.repeat( dummy_labels, repeats=[12 * 12 * 12] )
        #dummy_labels = tf.reshape( dummy_labels, (-1, 12 ,12 , 12, N_CLASSES) )
        #print(dummy_labels.shape)
        random_noise = tf.random.normal([BATCH_SIZE, NOISE_DIM])
        #noise_and_labels= tf.concat([random_noise, real_labels],axis=1)

        # GradientTape method records operations for automatic differentiation.
        with tf.GradientTape() as gen_tape, tf.GradientTape() as disc_tape:

            generated_images = self.generator([random_noise, real_en_labels,
                                               real_pid_labels], training=True)

            #fake_image_and_labels = tf.concat([generated_images, dummy_labels], -1)
            #real_image_and_labels = tf.concat([real_images, dummy_labels], -1)

            real_output = self.discriminator([real_images, real_en_labels,
                                              real_pid_labels], training=True)
            fake_output = self.discriminator([generated_images, real_en_labels,
                                              real_pid_labels], training=True)

            gen_loss = generator_loss(fake_output)
            discr_loss = discriminator_loss(real_output, fake_output)

        gradients_of_generator = gen_tape.gradient(gen_loss,
                                          self.generator.trainable_variables)
        gradients_of_discriminator = disc_tape.gradient(discr_loss,
                                           self.discriminator.trainable_variables)
        self.generator_optimizer.apply_gradients(zip(gradients_of_generator,
                                         self.generator.trainable_variables))
        self.discriminator_optimizer.apply_gradients(zip(gradients_of_discriminator,
                                         self.discriminator.trainable_variables))

        # Monitor losses
        self.gen_loss_tracker.update_state(gen_loss)
        self.discr_loss_tracker.update_state(discr_loss)
        return{
            "gen_loss": self.gen_loss_tracker.result(),
            "discr_loss": self.discr_loss_tracker.result(),
        }

    def train(self, dataset, epochs=EPOCHS, batch=BATCH_SIZE, buffer=BUFFER_SIZE):
        """Define the training function of the cGAN.
        Inputs:
        dataset = combined real images vectors and labels;
        epochs = number of epochs for the training.

        For each epoch:
        -) For each batch of the dataset, run the custom "train_step" function;
        -) Produce images;
        -) Save the model every 5 epochs as a checkpoint;
        -) Print out the completed epoch no. and the time spent;
        Then generate a final image after the training is completed.
        """
        # Split the dataset in Buffer and batch
        dataset = tf.data.Dataset.from_tensor_slices(dataset)
        dataset = dataset.shuffle(buffer)
        dataset = dataset.batch(batch, drop_remainder=True)

        # Create a folder to save rusults from training in form of checkpoints.
        checkpoint_dir = "./training_checkpoints"
        checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt")
        checkpoint = tf.train.Checkpoint(
                   generator=self.generator,
                   discriminator=self.discriminator,
                   generator_optimizer=self.generator_optimizer,
                   discriminator_optimizer=self.discriminator_optimizer)

        display.clear_output(wait=True)
        for epoch in range(epochs):
           print(f"Running EPOCH = {epoch + 1}")
           start = time.time()

           for image_batch in dataset:
              self.train_step(image_batch)

           display.clear_output(wait=True)
           print(f"EPOCH = {epoch + 1}")
           print (f"Time for epoch {epoch + 1} is {time.time()-start} sec")
           generate_and_save_images(self.generator, test_noise, epoch + 1)

           if epoch+1 % 5 == 0:
               logger.info("Saving checkpoint.")
               checkpoint.save(file_prefix = checkpoint_prefix)