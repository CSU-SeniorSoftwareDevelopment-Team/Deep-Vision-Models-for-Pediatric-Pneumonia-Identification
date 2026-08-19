# DeepImage

### AI-Powered Pediatric Pneumonia Detection

**Columbus State University**

DeepImage is an artificial intelligence project focused on helping detect **pediatric pneumonia from chest X-ray images**.

The project uses **Python, PyTorch, and image-processing technologies** to train an AI model to identify patterns in chest X-rays that may be associated with pneumonia.

Our goal is to explore how AI can assist with medical image analysis, particularly in areas where access to medical specialists or advanced computing resources may be limited.

> **Disclaimer:** DeepImage is an academic research project and is not a medical diagnostic device. It is not intended to replace doctors, radiologists, or other qualified healthcare professionals.

---

## About the Project

Pneumonia is an important health concern for children around the world. Chest X-rays can be used to help identify pneumonia, but interpreting medical images can require specialized training and experience.

DeepImage explores how artificial intelligence can assist with this process.

The project focuses on developing a model that can:

* Analyze pediatric chest X-ray images
* Identify images that may show pneumonia
* Provide a prediction based on the image
* Improve as more data becomes available
* Work efficiently on computers with limited resources

---

## What Makes DeepImage Different?

Many AI projects focus primarily on getting the highest possible accuracy.

DeepImage also considers **where and how the technology could actually be used**.

We are particularly interested in environments where there may be:

* Limited computing resources
* Limited internet access
* Fewer medical specialists
* Older or lower-cost computer hardware

This means we are exploring ways to make the AI model **smaller, faster, and more efficient** while maintaining good performance.

---

## Active Learning

Another important part of DeepImage is **active learning**.

Instead of having experts review and label every available X-ray, the AI can identify images where it is less confident.

Those images can then be selected for expert review and added to the training data.

This creates a cycle where:

```text
AI Makes Predictions
        ↓
Finds Uncertain Images
        ↓
Expert Reviews Images
        ↓
New Information Is Added
        ↓
AI Learns From New Data
        ↓
Improved Predictions
```

We will investigate whether this approach can reduce the amount of expert labeling required while continuing to improve the model.

---

## Measuring Performance

We will evaluate the AI using several measurements, including:

* **Accuracy** — How often the model makes the correct prediction
* **Precision** — How often a pneumonia prediction is correct
* **Recall (Sensitivity)** — How well the model identifies pneumonia cases
* **F1 Score** — A combined measure of precision and recall
* **Confusion Matrix** — A breakdown of correct and incorrect predictions
* **mAP** — A measurement that can be used when evaluating detection and localization

These measurements will help us understand not only how accurate the model is, but also where it performs well and where it needs improvement.

---

## Technology

DeepImage is primarily developed using:

* **Python**
* **PyTorch**
* **Computer Vision**
* **Image Processing**
* **Machine Learning**

Additional Python libraries may be used for data processing, visualization, and model evaluation.

---

## Project Goals

The main goals of DeepImage are to:

1. Develop an AI model capable of identifying pediatric pneumonia from chest X-rays.
2. Explore lightweight AI models that can run on less powerful hardware.
3. Demonstrate how active learning can reduce the amount of expert labeling required.
4. Measure how the model improves as additional data is introduced.
5. Explore ways AI predictions can be made easier to understand.
6. Investigate the potential of AI-assisted medical imaging in resource-constrained environments.

---

## Why This Matters

AI has the potential to assist healthcare professionals by providing additional tools for analyzing medical images.

DeepImage is exploring how that technology could potentially be made more accessible by focusing not only on model performance, but also on **efficiency, accessibility, and reduced data-labeling requirements**.

The long-term idea is to investigate whether useful AI-assisted medical imaging can be developed for environments that may not have access to expensive computing infrastructure or large numbers of medical specialists.

---

## Project Status

**Currently in Development**

DeepImage is an ongoing academic project at Columbus State University. The model, dataset, and methods used in the project may change as development and testing continue.

---

## Academic Affiliation

**Columbus State University**

This project is being developed as part of a student research/project effort at Columbus State University.

---

## References

1. Center for Policy Impact — *From Pixels to Prognosis: How Artificial Intelligence (AI) Analyzes Medical Images for Childhood Pneumonia Detection*
   https://centerforpolicyimpact.org/2024/08/10/from-pixels-to-prognosis-how-artificial-intelligence-ai-analyzes-medical-images-for-childhood-pneumonia-detection/

2. National Library of Medicine / PMC
   https://pmc.ncbi.nlm.nih.gov/articles/PMC10047666/

3. arXiv
   https://arxiv.org/abs/2507.09759
