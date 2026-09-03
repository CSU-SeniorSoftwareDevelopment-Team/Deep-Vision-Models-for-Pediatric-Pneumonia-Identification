import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import time

from pathlib import Path
from PIL import Image

import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import resnet50, ResNet50_Weights


class Backend:

    def __init__(self):

        # ---------------------------------------------------------
        # DEVICE
        # ---------------------------------------------------------

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        print("\n==============================")
        print("DEVICE INFORMATION:")
        print("==============================")

        print(f"Using device: {self.device}")

        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(
                f"CUDA Version: {torch.version.cuda}"
            )

            print(
                f"GPU Memory available: "
                f"{torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB"
            )

        else:
            print("WARNING: CUDA is NOT available on this machine!")
            print("Training will run on CPU... \n This will take some time...")

        # ---------------------------------------------------------
        # SETTINGS
        # ---------------------------------------------------------

        self.epochs = 3
        self.learning_rate = 0.001
        self.batch_size = 32

        # Print progress every N batches
        self.print_every = 10

        # ---------------------------------------------------------
        # FILE PATHS
        # ---------------------------------------------------------

        BASE_DIR = Path(__file__).resolve().parent

        self.train_data_folder = BASE_DIR / "TRAINING_IMAGES"
        self.test_data_folder = BASE_DIR / "TEST_IMAGES"

        print(f"\nTraining folder: {self.train_data_folder}")
        print(f"Testing folder:  {self.test_data_folder}")
        self.model_path = BASE_DIR / "pneumonia_resnet50.pth"

        # ---------------------------------------------------------
        # CHECK FOLDERS - raise error if not found
        # ---------------------------------------------------------

        if not self.train_data_folder.exists():
            raise FileNotFoundError(
                f"Training folder not found:\n"
                f"{self.train_data_folder}"
            )

        if not self.test_data_folder.exists():
            raise FileNotFoundError(
                f"Test folder not found:\n"
                f"{self.test_data_folder}"
            )

        # ---------------------------------------------------------
        # IMAGE TRANSFORM - resize, grayscale, normalize
        # ---------------------------------------------------------

        self.transform = transforms.Compose([

            transforms.Grayscale(
                num_output_channels=1
            ),

            transforms.Resize(
                (224, 224)
            ),

            transforms.ToTensor(),

            transforms.Normalize(
                mean=[0.5],
                std=[0.5]
            )
        ])

        # ---------------------------------------------------------
        # DATASETS - load training and testing datasets using ImageFolder
        # ---------------------------------------------------------

        self.train_dataset = datasets.ImageFolder(
            root=self.train_data_folder,
            transform=self.transform
        )

        self.test_dataset = datasets.ImageFolder(
            root=self.test_data_folder,
            transform=self.transform
        )

        # ---------------------------------------------------------
        # CHECK DATASET - raise error if not exactly 2 classes
        # ---------------------------------------------------------

        print("\n==============================")
        print("DATASET INFORMATION")
        print("==============================")

        print(
            f"Classes: "
            f"{self.train_dataset.class_to_idx}"
        )

        print(
            f"Training images: "
            f"{len(self.train_dataset)}"
        )

        print(
            f"Testing images:  "
            f"{len(self.test_dataset)}"
        )

        if len(self.train_dataset.classes) != 2:
            raise ValueError(
                "Expected exactly 2 classes: "
                "NORMAL and PNEUMONIA.\n"
                f"Found: {self.train_dataset.classes}"
            )

        # ---------------------------------------------------------
        # DATALOADERS - load training and testing datasets into DataLoader for batching
        # ---------------------------------------------------------

        self.train_dataloader = DataLoader(            # this is the training dataloader
            self.train_dataset, 
            batch_size      =self.batch_size,         
            shuffle         =True,
            num_workers     =0,
            pin_memory      =torch.cuda.is_available()
        )

        self.test_dataloader = DataLoader(
            self.test_dataset,
            batch_size      =self.batch_size,          # batch size for testing
            shuffle         =False,                    # don't shuffle test data
            num_workers     =0,                        # number of subprocesses to use for data loading. 0 means that the data will be loaded in the main process.
            pin_memory      =torch.cuda.is_available() # pin memory if using GPU
        )

        print(
            f"\nTraining batches per epoch: "
            f"{len(self.train_dataloader)}"
        )

        print(
            f"Batch size: "
            f"{self.batch_size}"
        )

        # ---------------------------------------------------------
        # MODEL - load pretrained ResNet50 and modify for 2-class classification
        # ---------------------------------------------------------

        print("\n==============================")
        print("LOADING RESNET50")
        print("==============================")

        self.model = resnet50(
            weights=ResNet50_Weights.IMAGENET1K_V2
        )

        # ResNet normally expects 3-channel RGB.
        # Change first layer to accept grayscale.

        self.model.conv1 = nn.Conv2d(
            1,
            64,
            kernel_size =7, # copied from resnet documention
            stride      =2,
            padding     =3,
            bias        =False
        )

        # Two classes:
        #
        # 0 = NORMAL
        # 1 = PNEUMONIA

        self.model.fc = nn.Linear(
            self.model.fc.in_features,
            2
        )

        self.model = self.model.to(
            self.device
        )

        print("Model loaded.")

        # Load trained model on boot
        self.loadModel()
        print("Trained Model loaded.")

        # ---------------------------------------------------------
        # LOSS
        # ---------------------------------------------------------

        self.loss_fn = nn.CrossEntropyLoss()

        # ---------------------------------------------------------
        # OPTIMIZER
        # ---------------------------------------------------------

        self.optimizer = torch.optim.SGD(
            self.model.parameters(),
            lr=self.learning_rate,
            momentum=0.9
        )

        print("Optimizer initialized.")





    # =============================================================
    # TRAIN MODEL
    # =============================================================

    def train_model(self, epochs=None, progress_callback=None ,  on_training_complete = None ):

        if epochs is None:
            epochs = self.epochs

        # diplay start of training sesson 
        print("\n==============================")
        print("STARTING TRAINING")
        print("==============================")

        print(f"Epochs: {epochs}")
        print(f"Device: {self.device}")
        print(
            f"Images per epoch: "
            f"{len(self.train_dataset)}"
        )
        print(
            f"Batches per epoch: "
            f"{len(self.train_dataloader)}"
        )

        self.model.train()

        total_training_start = time.time()

        for epoch in range(epochs):         # epoch loop 

            epoch_start         = time.time() # start up time
            running_loss        = 0.0         # initialize running loss for the epoch
            correct             = 0
            total               = 0

            print("\n==============================")
            print(
                f"Epoch {epoch + 1}/{epochs}"
            )
            print("==============================")

            for batch_idx, (inputs, labels) in enumerate(
                self.train_dataloader
            ):

                batch_start = time.time()   # start up time batch

                # -------------------------------------------------
                # MOVE DATA TO DEVICE  
                # non blocking
                # -------------------------------------------------

                inputs = inputs.to(
                    self.device,
                    non_blocking=True
                )

                labels = labels.to(
                    self.device,
                    non_blocking=True
                )

                # -------------------------------------------------
                # CLEAR GRADIENTS


                self.optimizer.zero_grad(
                    set_to_none=True
                )

                # FORWARD PASS

                outputs = self.model(
                    inputs
                )

 
                # LOSS


                loss = self.loss_fn(
                    outputs,
                    labels
                )


                # BACKPROPAGATION

                loss.backward()


                # -------------------------------------------------
                # UPDATE WEIGHTS
                # -------------------------------------------------

                self.optimizer.step()

                # STATISTICS

                running_loss += loss.item()

                _, predicted = torch.max(
                    outputs,
                    1
                )

                total += labels.size(0)

                correct += (
                    predicted == labels
                ).sum().item()


                # PROGRESS report


                if (
                    batch_idx % self.print_every == 0
                    or batch_idx == len(
                        self.train_dataloader
                    ) - 1
                ):

                    batch_time = (
                        time.time()
                        - batch_start
                    )

                    elapsed = (
                        time.time()
                        - epoch_start
                    )

                    progress = (
                        (batch_idx + 1)
                        / len(self.train_dataloader)
                    ) * 100

                    current_accuracy = (
                        100 * correct / total
                    )

                    avg_batch_time = (
                        elapsed
                        / (batch_idx + 1)
                    )

                    remaining_batches = (
                        len(self.train_dataloader)
                        - (batch_idx + 1)
                    )

                    estimated_remaining = (
                        remaining_batches
                        * avg_batch_time
                    )

                    # gets all of the data of the current epoch 
                    print(
                        f"[{progress:6.2f}%] "
                        f"Batch "
                        f"{batch_idx + 1}/"
                        f"{len(self.train_dataloader)} "
                        f"| Loss: "
                        f"{loss.item():.4f} "
                        f"| Accuracy: "
                        f"{current_accuracy:.2f}% "
                        f"| Batch: "
                        f"{batch_time:.2f}s "
                        f"| ETA: "
                        f"{estimated_remaining / 60:.1f} min"
                    )
                    # sow results in UI
                    if progress_callback is not None:

                        progress_callback(
                            epoch + 1,
                            epochs,
                            loss,
                            current_accuracy
                        )

            # EPOCH RESULTS

            # average losses 
            average_loss = (
                running_loss
                / len(self.train_dataloader)
            )
            # accuracy 
            accuracy = (
                100 * correct / total
            )
            # run time 
            epoch_time = (
                time.time()
                - epoch_start
            )

            print("\n------------------------------")
            print(
                f"Epoch {epoch + 1} COMPLETE"
            )
            print("------------------------------")

            print(
                f"Loss:     {average_loss:.4f}"
            )

            print(
                f"Accuracy: {accuracy:.2f}%"
            )

            print(
                f"Time:     {epoch_time / 60:.2f} minutes"
            )

            if torch.cuda.is_available():

                print(
                    f"GPU Memory Allocated: "
                    f"{torch.cuda.memory_allocated() / 1024**3:.2f} GB"
                )

                print(
                    f"GPU Memory Reserved:  "
                    f"{torch.cuda.memory_reserved() / 1024**3:.2f} GB"
                )

        total_training_time = (
            time.time()
            - total_training_start
        )

        print("\n==============================")
        print("TRAINING COMPLETE")
        print("==============================")

        print(
            f"Total training time: "
            f"{total_training_time / 60:.2f} minutes"
        )
        # save the resenet50 model - load on boot 
        if on_training_complete is not None:
            on_training_complete() # CALL BACK TO FRONTSIDE POPUP FOR SAVE MODEL - THIS IS A CALLBACK FUNCTION PASSED FROM THE FRONTEND




    # ===========================================================
    # LOAD MODEL
    # ===========================================================

    def loadModel(self):

        if not self.model_path.exists():

            print("\n==============================")
            print("NO TRAINED MODEL FOUND")
            print("==============================")

            return False

        print("\n==============================")
        print("LOADING TRAINED MODEL")
        print("==============================")

        self.model.load_state_dict(
            torch.load(
                self.model_path,
                map_location=self.device
            )
        )

        self.model.to(self.device)
        self.model.eval()

        print(
            f"Model loaded from:\n"
            f"{self.model_path}"
        )

        return True


    
    # ===========================================================
    # SAVE MODEL
    # ===========================================================


    def saveModel(self):
        torch.save(
            self.model.state_dict(),
            self.model_path
        )

        print(f"Model saved to: {self.model_path}")



    # =============================================================
    # TEST MODEL
    # =============================================================

    def test_model(self):

        self.model.eval()

        correct = 0
        total = 0

        running_loss = 0.0

        with torch.no_grad():

            for inputs, labels in self.test_dataloader:

                inputs = inputs.to(
                    self.device,
                    non_blocking=True
                )

                labels = labels.to(
                    self.device,
                    non_blocking=True
                )

                outputs = self.model(
                    inputs
                )

                loss = self.loss_fn(
                    outputs,
                    labels
                )

                running_loss += loss.item()

                _, predicted = torch.max(
                    outputs,
                    1
                )

                total += labels.size(0)

                correct += (
                    predicted == labels
                ).sum().item()

        accuracy = (
            100 * correct / total
        )

        average_loss = (
            running_loss
            / len(self.test_dataloader)
        )

        print("\n==============================")
        print("TEST RESULTS")
        print("==============================")

        print(
            f"Loss:     {average_loss:.4f}"
        )

        print(
            f"Accuracy: {accuracy:.2f}%"
        )

        return accuracy

    
    
    
    # =============================================================
    # PREDICT A TENSOR
    # =============================================================

    def predict(self, sample):

        self.model.eval()

        with torch.no_grad():

            sample = sample.to(
                self.device
            )

            outputs = self.model(
                sample
            )

            probabilities = torch.softmax(
                outputs,
                dim=1
            )

            predicted = torch.argmax(
                probabilities,
                dim=1
            )

            confidence = probabilities[
                0,
                predicted.item()
            ].item()

        label = self.get_class_name(
            predicted.item()
        )

        return label, confidence




    # =============================================================
    # GET CLASS NAME - helper 
    # =============================================================

    def get_class_name(self, class_index):

        idx_to_class = {
            value: key
            for key, value
            in self.train_dataset.class_to_idx.items()
        }

        return idx_to_class[
            class_index
        ].upper()






    # =============================================================
    # PREDICT FROM FILE
    # Loads an image and runs it through 
    # =============================================================

    def predict_from_file(self, file_path):

        image = Image.open(
            file_path
        ).convert("L")

        sample = self.transform(
            image
        ).unsqueeze(0)

        label, confidence = self.predict( # prediction 
            sample
        )

        print("\n==============================")
        print("PREDICTION")
        print("==============================")

        print(
            f"Prediction: {label}"
        )

        print(
            f"Confidence: "
            f"{confidence * 100:.2f}%"
        )

        return label, confidence





    # =============================================================
    # DISPLAY / TEST ONE IMAGE
    # runs a single image throught the model 
    # =============================================================

    def Run_Single_Img_Through(self):

        self.model.eval()

        idx = 0

        sample, label = self.test_dataset[
            idx
        ]

        sample_batch = sample.unsqueeze(0)

        predicted_label, confidence = (
            self.predict(sample_batch)
        )

        actual_label = self.get_class_name(
            label
        )

        plt.figure(
            figsize=(6, 6)
        )

        plt.imshow(
            sample.squeeze(0),
            cmap="gray"
        )

        plt.title(
            f"Actual: {actual_label}\n"
            f"Predicted: {predicted_label} "
            f"({confidence * 100:.2f}%)"
        )

        plt.axis("off")

        plt.show()

        print(
            f"Actual:    {actual_label}"
        )

        print(
            f"Predicted: {predicted_label}"
        )

        print(
            f"Confidence: "
            f"{confidence * 100:.2f}%"
        )

        return predicted_label, confidence