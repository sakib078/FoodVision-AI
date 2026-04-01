# 🍽️ FoodVision AI  
### AI-Powered Food Recognition & Calorie Estimation System

FoodVision AI is a computer vision–based system that identifies food items from images and supports calorie and nutritional estimation using deep learning. The project demonstrates the practical application of convolutional neural networks (CNNs) in food analysis, with a modular backend–frontend architecture suitable for real-world deployment.

This project was developed as part of **SEA710 – Computer Vision** at **Seneca Polytechnic**.

---

## 📌 Problem Statement
Tracking food intake and estimating calories manually is time-consuming and often inaccurate. FoodVision AI aims to automate food recognition from images using deep learning, helping users gain better awareness of their dietary habits through computer vision–based analysis.

---

## 📊 Dataset
- **Source:** Publicly available food image datasets used for academic research
- **Data Type:** RGB food images
- **Annotations:** Ground truth food category labels
- **Characteristics:** Images captured under varying lighting conditions, angles, and backgrounds to ensure robustness

---

## 🧠 Ground Truth
Ground truth labels consist of food category annotations provided with the dataset. These labels are used for supervised training and evaluation of the classification model.

---

## 🔀 Dataset Splitting
The dataset was divided into:
- **Training set** – model learning
- **Validation set** – tuning and performance monitoring
- **Test set** – final evaluation

This split ensures generalization while reducing overfitting.

---

## 🔍 Previous Work
The project builds upon existing research in food recognition using CNN architectures such as ResNet and MobileNet. Prior work demonstrates strong classification performance but often lacks deployment-ready design. FoodVision AI extends these approaches by focusing on preprocessing consistency, modular system design, and real-world usability.

---

## ⚙️ Methodology & Contributions
The system pipeline includes:
1. Image preprocessing (resizing, normalization, augmentation)
2. CNN-based feature extraction
3. Model training and validation
4. Inference and prediction pipeline

### Key Contributions
- Modular **Backend–Frontend architecture**
- Consistent preprocessing between training and inference
- Deployment-ready project structure
- Quantitative and qualitative evaluation

Individual contributions are detailed in personal reports as required by the course.

---

## 📈 Evaluation
### Quantitative
- Model accuracy and validation metrics monitored during training
- Performance comparison with baseline CNN approaches

### Qualitative
- Visual inspection of predictions
- Correct classification across diverse food categories

---

## 🧪 Outcome & Reflection
The project successfully achieved reliable food image classification. Challenges included dataset variability and model size constraints, which were addressed through preprocessing strategies and architectural choices.

---

## 🗂️ Repository Structure
