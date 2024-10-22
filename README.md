# Telco Customer Churn Prediction
This project uses the **Telco Customer Churn** dataset from [Kaggle](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) to predict customer churn using several machine learning models.

## Project Overview
- **Dataset**: Telco Customer Churn
- **Goal**: To predict whether a customer will churn based on features such as monthly charges, tenure, and service usage.
- **Key Steps**:
  - Data exploration and cleaning
  - Model training (Random Forest, Gradient Boosting, etc.)
  - Cross-validation, AUC-ROC analysis, and feature importance evaluation.

## Dataset
The dataset can be found on [Kaggle](https://www.kaggle.com/datasets/blastchar/telco-customer-churn). It contains customer data including demographic information, account details, and services used.

## Improvements Made
- **Class Imbalance**: Applied class weighting and SMOTE to improve churn prediction.
- **Threshold Tuning**: Optimized decision threshold to increase recall for churn customers.
- **Random Forest Tuning**: Optimized using RandomizedSearchCV.

## Results
- **Best Model**: Random Forest with a test accuracy of 77.19%.
- **ROC-AUC Score**: 0.8481, indicating strong model performance in distinguishing churn vs. non-churn customers.

## How to Run the Project
1. Clone this repository.
2. Download the dataset from [Kaggle](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) and place it in the `data/` directory.
3. Install dependencies using `pip install -r requirements.txt`.
4. Open the notebook `customer_segmentation_using_kmeans.ipynb` and run all cells.
