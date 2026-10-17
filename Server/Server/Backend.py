import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import time
import io
from pathlib import Path
from PIL import Image

import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import resnet50, ResNet50_Weights

class Backend(object):
    def __init__(self):

        
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

        self.epochs             = 3
        self.learning_rate      = 0.001
        self.batch_size         = 32

        # Print progress every N batches
        self.print_every        = 10
        self.threshold          = 70 # threshold for error


        # ---------------------------------------------------------
        # VARs
        # ---------------------------------------------------------

        # progress / network data tracking 
        self.Processing = False  # traffic indicator 
        self.Training   = False  # should tell everyone on the network that the server may be busy 
        

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

        print(" [Backend] Initialized") 





    def Update():
        pass





    '''
    loadModel - loads the trained model from disk if it exists. 
                If not, it will print a warning and return False.
    '''
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



    '''
    saveModel - saves the trained model to disk.
    ''' 
    def saveModel(self):
        torch.save(
            self.model.state_dict(),
            self.model_path
        )

        print(f"Model saved to: {self.model_path}")


    '''
    Predict images from network buffer
    '''
    def predict_from_buffer(self, image_bytes):
        self.Processing = True
        image_stream = io.BytesIO(image_bytes)
        image = Image.open(image_stream).convert("L")

        sample = self.transform(image).unsqueeze(0)

        label, confidence = self.predict(sample)

        if confidence * 100 < self.threshold:
            print(f"Warning: Confidence {confidence * 100:.2f}% is below threshold of {self.threshold}%")

        print("\n==============================")
        print("PREDICTION (FROM BUFFER)")
        print("==============================")
        print(f"Prediction: {label}")
        print(f"Confidence: {confidence * 100:.2f}%")

        return label, confidence



    '''
       predict - predicts the class of a given sample using the trained model.
       Properties:
           sample: a single image tensor of shape (1, 1, 224, 224) - a single grayscale image resized to 224x224 pixels.
    '''
    def predict(self, sample):

        self.model.eval()

        sum_ = 0 
        samples = 2 # setting this too high does kind amake this run slow - 2 is a good number for now

        for i in range(0,samples):

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
            sum_ = sum_ + confidence

         
        return label, sum_/samples  # return the average confidence over 2 runs


    # helper function to get the container 
    def get_class_name(self, class_index):

        idx_to_class = {
            value: key
            for key, value
            in self.train_dataset.class_to_idx.items()
        }

        return idx_to_class[
            class_index
        ].upper()
